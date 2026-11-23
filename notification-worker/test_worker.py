import worker as w

M = 600  # ten minutes in seconds


def run(db, senders, fd, t, window=lambda n: True):
    w.run_once(db, senders, fd, t, window)


HOURS = lambda n: 6 <= (n // 3600) % 24 < 21   # window on UTC clock for deterministic tests


def fresh():
    db = w.connect()
    sent, alerts = [], []
    ok = {ch: (lambda mid, text, ch=ch: sent.append((ch, mid))) for ch in w.CHANNELS}
    return db, sent, alerts, ok, (lambda mid, oid: alerts.append((mid, oid)))


def test_ack_after_first_send_stops_everything():
    db, sent, alerts, ok, fd = fresh()
    w.enqueue(db, 1, "CLAIM", 10, 0)
    run(db, ok, fd, 0)
    assert len(sent) == 3
    w.acknowledge(db, 1, 60)
    for t in range(1, 10):
        run(db, ok, fd, t * M)
    assert len(sent) == 3 and alerts == []


def test_unacknowledged_resends_on_all_channels_each_timer():
    db, sent, alerts, ok, fd = fresh()
    w.enqueue(db, 1, "CLAIM", 10, 0)
    for t in range(3): run(db, ok, fd, t * M)
    assert len(sent) == 9


def test_no_second_send_before_next_timer():
    db, sent, alerts, ok, fd = fresh()
    w.enqueue(db, 1, "CLAIM", 10, 0)
    run(db, ok, fd, 0); run(db, ok, fd, 0); run(db, ok, fd, 5 * 60)
    assert len(sent) == 3


def test_failing_channel_does_not_block_others_and_recovers_next_cycle():
    db, sent, alerts, ok, fd = fresh()
    calls = {"n": 0}
    def flaky_sms(mid, text):
        calls["n"] += 1
        if calls["n"] == 1: raise RuntimeError("gateway down")
        sent.append(("sms", mid))
    s = dict(ok, sms=flaky_sms)
    w.enqueue(db, 1, "CLAIM", 10, 0)
    run(db, s, fd, 0)
    row = db.execute("SELECT * FROM notification_outbox").fetchone()
    assert [c for c, _ in sent] == ["email", "push"] and row["sms_status"] == "FAILED" and "gateway" in row["last_error"]
    run(db, s, fd, M)
    row = db.execute("SELECT * FROM notification_outbox").fetchone()
    assert ("sms", 1) in sent and row["sms_status"] == "SENT" and row["last_error"] is None


def test_never_acknowledged_five_sends_then_one_front_desk_alert():
    db, sent, alerts, ok, fd = fresh()
    down = {ch: (lambda mid, text: (_ for _ in ()).throw(RuntimeError("down"))) for ch in w.CHANNELS}
    w.enqueue(db, 1, "CLAIM", 10, 0)
    for t in range(12): run(db, down, fd, t * M)
    row = db.execute("SELECT attempts FROM notification_outbox").fetchone()
    assert row["attempts"] == w.MAX_SENDS and len(alerts) == 1


def test_ignored_push_with_working_channels_still_escalates_after_cap():
    db, sent, alerts, ok, fd = fresh()
    w.enqueue(db, 1, "CLAIM", 10, 0)
    for t in range(12): run(db, ok, fd, t * M)
    assert len(alerts) == 1 and len(sent) == 15


def test_opt_out_respected():
    db, sent, alerts, ok, fd = fresh()
    db.execute("INSERT INTO member_contact_prefs (member_id, sms_opt_in) VALUES (1, 'N')")
    w.enqueue(db, 1, "CLAIM", 10, 0)
    run(db, ok, fd, 0)
    assert ("sms", 1) not in sent and ("email", 1) in sent


def test_nothing_sent_at_night_and_sent_when_window_opens():
    db, sent, alerts, ok, fd = fresh()
    night = 22 * 3600
    w.enqueue(db, 1, "CLAIM", 10, night)
    run(db, ok, fd, night, HOURS)
    run(db, ok, fd, night + 5 * 3600, HOURS)      # 3 am
    assert sent == [] and alerts == []
    run(db, ok, fd, 30 * 3600, HOURS)             # 6 am next day
    assert len(sent) == 3


def test_front_desk_alert_also_waits_for_the_window():
    db, sent, alerts, ok, fd = fresh()
    w.enqueue(db, 1, "CLAIM", 10, 0)
    db.execute("UPDATE notification_outbox SET attempts=5, next_attempt=0"); db.commit()
    run(db, ok, fd, 22 * 3600, HOURS)
    assert alerts == []
    run(db, ok, fd, 30 * 3600, HOURS)
    assert len(alerts) == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok  ", name)
