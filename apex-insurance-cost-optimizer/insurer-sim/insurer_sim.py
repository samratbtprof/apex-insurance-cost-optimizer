"""Reference simulation of the insurer submission guarantees (synthetic; there is no real insurer or API here).

Shows, in a small SQLite model of claim_submissions (db/05_insurer_integration.sql):
  - marker first: the row is saved as SENDING with an idempotency key before the API call
  - a lost reply or an insurer outage leaves SENDING; the retry reuses the same key, so the insurer never holds two claims
  - once the insurer's tag is stored, the submission is locked and never sent again
  - a second claim for a patient who already has an open claim is rejected
  - the claims team sees "Decision pending at insurer end" until the decision returns
"""
import sqlite3

SCHEMA = """
CREATE TABLE claims (claim_id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL);
CREATE TABLE rejection_codes (reject_code TEXT PRIMARY KEY, plain_text TEXT NOT NULL);
CREATE TABLE claim_submissions (
  claim_id INTEGER PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL DEFAULT 'QUEUED', attempts INTEGER NOT NULL DEFAULT 0,
  insurer_ref_tag TEXT, decision TEXT, reject_code TEXT);
"""


class FakeInsurer:
    def __init__(self):
        self.up = True
        self.drop_next_reply = False
        self.received = {}            # idempotency key -> tag (what the insurer holds)

    def submit(self, key):
        if not self.up:
            raise ConnectionError("insurer system down")
        tag = self.received.setdefault(key, f"INS-{len(self.received) + 1:04d}")   # same key, same record
        if self.drop_next_reply:
            self.drop_next_reply = False
            raise TimeoutError("reply lost")                                      # insurer got it, we did not hear
        return tag


def connect():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.execute("INSERT INTO rejection_codes VALUES ('X12', 'The drug is not on this plan''s approved list.')")
    return db


def submit_claim(db, claim_id, patient_id):
    """Queue a claim. A patient with an open claim cannot start another."""
    open_claim = db.execute("SELECT 1 FROM claims c JOIN claim_submissions s USING (claim_id) "
                            "WHERE c.patient_id=? AND s.status!='DECIDED'", (patient_id,)).fetchone()
    if open_claim:
        return False
    db.execute("INSERT INTO claims VALUES (?,?)", (claim_id, patient_id))
    db.execute("INSERT INTO claim_submissions (claim_id, idempotency_key) VALUES (?,?)", (claim_id, f"claim-{claim_id}"))
    db.commit()
    return True


def process(db, insurer):
    """One retry pass: every QUEUED or SENDING submission is (re)sent with its own key until the insurer's tag is stored."""
    for r in db.execute("SELECT * FROM claim_submissions WHERE status IN ('QUEUED','SENDING')").fetchall():
        db.execute("UPDATE claim_submissions SET status='SENDING', attempts=attempts+1 WHERE claim_id=?", (r["claim_id"],))
        db.commit()                                   # marker saved before the call
        try:
            tag = insurer.submit(r["idempotency_key"])
        except (ConnectionError, TimeoutError):
            continue                                  # stays SENDING; next pass reuses the same key
        db.execute("UPDATE claim_submissions SET insurer_ref_tag=?, status='PENDING_AT_INSURER' WHERE claim_id=?",
                   (tag, r["claim_id"]))
        db.commit()


def record_decision(db, tag, decision, reject_code=None):
    db.execute("UPDATE claim_submissions SET decision=?, reject_code=?, status='DECIDED' WHERE insurer_ref_tag=?",
               (decision, reject_code, tag))
    db.commit()


def shown_status(db, claim_id):
    r = db.execute("SELECT s.status, s.decision, s.reject_code, c.plain_text FROM claim_submissions s "
                   "LEFT JOIN rejection_codes c ON c.reject_code=s.reject_code WHERE claim_id=?", (claim_id,)).fetchone()
    if r["status"] != "DECIDED":
        return "Decision pending at insurer end"
    return r["decision"] if r["decision"] == "APPROVED" else f"REJECTED ({r['reject_code']}): {r['plain_text']}"
