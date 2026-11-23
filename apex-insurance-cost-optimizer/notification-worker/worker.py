"""Reference notification worker (stdlib only, SQLite stand-in for the APEX/Oracle outbox).

Rules (from the delivered design):
  - Every message is generic ("An update is available"); details are read in the app after login.
  - Nothing is sent, and no front-desk alert is raised, outside 6 am - 9 pm.
  - Each unacknowledged outbox row is (re)sent every RETRY_MINUTES.
  - 3 sends in normal conditions; if still unacknowledged (a channel was down, or Web Push was ignored)
    2 more sends are allowed. Hard cap: MAX_SENDS = 5.
  - After the cap with no acknowledgement, the front desk is alerted once to call the patient's registered number.
  - Acknowledgement = the patient logs in and opens the update (read_at is set by the app).
  - Each timer tick resends on every channel while the acknowledged marker is empty; per-channel flags record the
    result of the current cycle, and a cycle is never repeated before the next timer.
  - The delivered system ran one worker per channel (email, SMS, push), replaced automatically by a health checker
    if it failed. This reference code is a single loop for all channels, a simplification.
Delivery is at-least-once: a crash or a failover overlap can cause one repeat message; messages are generic, so this is harmless.
"""
import sqlite3, time

RETRY_MINUTES = 10
MAX_SENDS = 5
CHANNELS = ("email", "sms", "push")

SCHEMA = """
CREATE TABLE IF NOT EXISTS notification_outbox (
  outbox_id INTEGER PRIMARY KEY, member_id INTEGER, event_type TEXT, ref_id INTEGER,
  created_at REAL, attempts INTEGER DEFAULT 0, next_attempt REAL,
  email_status TEXT DEFAULT 'PENDING', sms_status TEXT DEFAULT 'PENDING', push_status TEXT DEFAULT 'PENDING',
  last_error TEXT, read_at REAL, frontdesk_alerted_at REAL);
CREATE TABLE IF NOT EXISTS member_contact_prefs (
  member_id INTEGER PRIMARY KEY, email_opt_in TEXT DEFAULT 'Y', sms_opt_in TEXT DEFAULT 'Y', push_opt_in TEXT DEFAULT 'Y');
"""


def within_window(now, start=6, end=21):
    """Sending window: messages and front-desk alerts go out only from 6 am to 9 pm (local time)."""
    return start <= time.localtime(now).tm_hour < end


def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def enqueue(db, member_id, event_type, ref_id, now):
    db.execute("INSERT INTO notification_outbox (member_id,event_type,ref_id,created_at,next_attempt) VALUES (?,?,?,?,?)",
               (member_id, event_type, ref_id, now, now))
    db.commit()


def run_once(db, senders, frontdesk_alert, now, window=within_window):
    """senders: {'email': fn(member_id, text), 'sms': fn, 'push': fn}; each raises on failure.

    One cycle per timer tick for each unacknowledged row:
      1. claim the cycle first (count it, set the next timer), so a crash cannot cause a second send before the next timer
      2. send on every channel the patient has not opted out of; a failing channel never blocks the others
      3. record per-channel results (the per-channel flags)
    The next tick checks only the acknowledged marker (read_at); if it is still empty the cycle repeats on all channels.
    """
    if not window(now):
        return  # outside 6 am - 9 pm: nothing is sent and no cycle is counted; due rows wait for the window to open
    due = db.execute("SELECT * FROM notification_outbox WHERE read_at IS NULL AND frontdesk_alerted_at IS NULL "
                     "AND next_attempt <= ?", (now,)).fetchall()
    for row in due:
        oid = row["outbox_id"]
        if row["attempts"] >= MAX_SENDS:
            frontdesk_alert(row["member_id"], oid)
            db.execute("UPDATE notification_outbox SET frontdesk_alerted_at=? WHERE outbox_id=?", (now, oid))
            continue
        db.execute("UPDATE notification_outbox SET attempts=attempts+1, next_attempt=?, last_error=NULL, "
                   "email_status='PENDING', sms_status='PENDING', push_status='PENDING' WHERE outbox_id=?",
                   (now + RETRY_MINUTES * 60, oid))
        db.commit()  # cycle claimed
        prefs = db.execute("SELECT * FROM member_contact_prefs WHERE member_id=?", (row["member_id"],)).fetchone()
        errors = []
        for ch in CHANNELS:
            if prefs is not None and prefs[f"{ch}_opt_in"] == "N":
                db.execute(f"UPDATE notification_outbox SET {ch}_status='OPTED_OUT' WHERE outbox_id=?", (oid,))
                continue
            try:
                senders[ch](row["member_id"], "An update is available. Please log in to view it.")
                db.execute(f"UPDATE notification_outbox SET {ch}_status='SENT' WHERE outbox_id=?", (oid,))
            except Exception as e:
                db.execute(f"UPDATE notification_outbox SET {ch}_status='FAILED' WHERE outbox_id=?", (oid,))
                errors.append(f"{ch}: {e}")
        db.execute("UPDATE notification_outbox SET last_error=? WHERE outbox_id=?", ("; ".join(errors) or None, oid))
        db.commit()


def acknowledge(db, outbox_id, now):
    """Called when the patient logs in and opens the update."""
    db.execute("UPDATE notification_outbox SET read_at=? WHERE outbox_id=?", (now, outbox_id))
    db.commit()
