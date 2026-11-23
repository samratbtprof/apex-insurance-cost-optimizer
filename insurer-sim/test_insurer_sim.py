import insurer_sim as s


def test_lost_reply_never_creates_a_second_claim():
    db, ins = s.connect(), s.FakeInsurer()
    s.submit_claim(db, 1, 100)
    ins.drop_next_reply = True
    s.process(db, ins)                                    # insurer got it, reply lost
    assert db.execute("SELECT status FROM claim_submissions").fetchone()[0] == "SENDING"
    s.process(db, ins)                                    # retry with the same key
    assert len(ins.received) == 1
    assert db.execute("SELECT status FROM claim_submissions").fetchone()[0] == "PENDING_AT_INSURER"


def test_outage_retries_until_insurer_is_up():
    db, ins = s.connect(), s.FakeInsurer()
    ins.up = False
    s.submit_claim(db, 1, 100)
    for _ in range(3):
        s.process(db, ins)
    assert db.execute("SELECT attempts, status FROM claim_submissions").fetchone()[:] == (3, "SENDING")
    assert s.shown_status(db, 1) == "Decision pending at insurer end"
    ins.up = True
    s.process(db, ins)
    assert len(ins.received) == 1


def test_locked_after_tag_and_never_resent():
    db, ins = s.connect(), s.FakeInsurer()
    s.submit_claim(db, 1, 100)
    s.process(db, ins)
    s.process(db, ins)
    assert db.execute("SELECT attempts FROM claim_submissions").fetchone()[0] == 1


def test_second_claim_for_patient_with_open_claim_is_rejected_then_allowed_after_decision():
    db, ins = s.connect(), s.FakeInsurer()
    assert s.submit_claim(db, 1, 100)
    assert not s.submit_claim(db, 2, 100)
    s.process(db, ins)
    s.record_decision(db, "INS-0001", "APPROVED")
    assert s.submit_claim(db, 2, 100)


def test_rejection_shows_code_and_plain_text():
    db, ins = s.connect(), s.FakeInsurer()
    s.submit_claim(db, 1, 100)
    s.process(db, ins)
    s.record_decision(db, "INS-0001", "REJECTED", "X12")
    assert s.shown_status(db, 1) == "REJECTED (X12): The drug is not on this plan's approved list."


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("ok  ", n)
