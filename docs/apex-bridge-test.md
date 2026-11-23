# Testing the APEX to Python connection (outbox over REST)

## Result of the live test (2026-11-21, repo owner's own APEX workspace)
One test row was inserted into `notification_outbox`. `bridge.py --dry-run` read it over REST (1 pending update, generic text printed). `bridge.py` then wrote the result back, and a query in SQL Commands showed `status SENT, attempts 1, email/sms/push SENT`. A second run found 0 pending updates. The REST object was opened only for this test (no authorization on the table); It was disabled again the next day (first attempts from the Database Actions screen collided with each other in ORDS, ORA-00060, and the endpoint kept answering; a single `ORDS.ENABLE_OBJECT(p_enabled => FALSE, ...)` call from SQL Commands closed it, confirmed by an empty `user_ords_enabled_objects` and a 404). The workspace address is deliberately not recorded in this repo.

What is real today: the patient PWA demo in `patient-pwa/` reads the CSV files, not your APEX database. The worker in `notification-worker/` uses SQLite. Nothing in the repo yet talks to Oracle. `apex-bridge/bridge.py` is the first piece that does: it reads PENDING rows of `notification_outbox` through APEX's REST feature and writes the result back.

## Steps (in your APEX workspace)
1. SQL Workshop, RESTful Services. If asked, register your schema (choose an alias, for example `icoapp`).
2. AutoREST: enable `NOTIFICATION_OUTBOX` (Object Alias `notification_outbox`). Leave "Authorization Required" ON if offered; for a first test with synthetic data you may switch it off briefly, then switch it back on.
3. Copy the base URL the page shows (the part before `/notification_outbox/`).
4. Insert one test update in SQL Commands (one block):
```sql
BEGIN
INSERT INTO notification_outbox (member_id, event_type, ref_id) VALUES (1, 'CLAIM', 1);
COMMIT;
END;
```
5. On your own computer (the cloud session cannot reach your workspace):
   `set APEX_REST_BASE=<base url>` (Windows) or `export APEX_REST_BASE=<base url>`, then `python3 bridge.py --dry-run`, then `python3 bridge.py`.
6. Check in SQL Commands: `SELECT outbox_id, status, attempts, email_status FROM notification_outbox` shows SENT and attempts 1.

## Limits (state them in the case study)
- The bridge sends nothing real; the send step is a print.
- It marks a row SENT after one pass. The delivered worker resent every 10 minutes until the patient logged in (read_at set), with a cap of 5 and a front-desk alert. `notification-worker/worker.py` has that logic on SQLite; joining the two is not done.
- The PWA still reads CSV. Pointing it at APEX (patient data and decisions over REST) is the next step, not built.
- REST availability and URL format differ between APEX workspaces. The test against a fake local service passes (`python3 test_bridge.py`), and one live run against the owner's workspace passed as described at the top. Only one row, one pass, no retries, no failure cases were tested live.

## Lesson for section 5
Opening a table to anonymous REST for a test is quick but risky: AutoREST allows writes as well as reads, and the first disable attempt did not take effect for a day. Next time enable it with authorization required from the start (`p_auto_rest_auth => TRUE`) and give the bridge a token.
