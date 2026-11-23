# Review notes: drawbacks, lags and improvement options

Purpose: honest critique of the delivered design, kept apart from the case study. This is the raw material for section 5 ("What I would do differently"), which we agreed to discuss later together with AI integration ideas. Nothing here is claimed as delivered. Items marked **Ask** need your answer.

## A. Where the design is strong (use these as proof points)
1. Outbox written in the same transaction as the business change: no lost or phantom notifications.
2. Generic messages and login-gated details: no health data over email, SMS or push.
3. Login as acknowledgement, with escalation to a human (front desk): the process does not stop at "message sent".
4. Failure of any channel never blocks the others, and a failed worker is replaced automatically, with pending updates safe in the table.
5. A single self-healing unit is a defensible choice at this scale (up to 300 beds).

## B. Drawbacks and lags, most important first
| # | Issue | Why it matters | Improvement option |
|---|---|---|---|
| 1 | Up to 15 messages per update (5 cycles on 3 channels), shown by the worker test | Patient annoyance, SMS cost, and risk of being ignored or opting out | Escalate by channel: push first, SMS later, email as last resort; or stop SMS after one delivery receipt |
| 2 | The retry window is about 40 to 50 minutes before the front desk is alerted (40 if the alert follows the fifth send, 50 if it waits for the next timer) | Fine for information, slow if the patient must act (accept or decline a suggestion before dispensing) | Shorter intervals for action-needed events, longer for information-only ones; quiet hours at night |
| 3 | One unit means a gap while a replacement starts: up to the detection time (pings every 5 seconds) plus start time | Updates are delayed, not lost, because of the outbox | Report the gap as a measured number from Loki (**Ask**: missed pings before failure, start time) |
| 4 | Failover overlap: a hung old worker and its new replacement can both send | A duplicate message; harmless as messages are generic | Claim rows with a lease (database row lock with a timeout) so only one worker owns a row at a time |
| 5 | The health checker and API gateway are themselves single points; workers and Redis share fate as one unit | If the checker is down, no one replaces a failed worker | Watch the checker from outside, or alert if the outbox backlog grows past a threshold |
| 6 | Acknowledgement set when each update is opened (confirmed) | Resolved: opening one update does not clear others | Keep this as a proof point |
| 7 | Redis pub/sub does not store messages, and replacing the unit loses messages in flight | Harmless here because the outbox and the next timer cover it; Redis was chosen as easy to set up and suitable for simple pub/sub | Say this plainly; if volume grew, Redis Streams or a managed queue would add durability |
| 8 | Patient id in the push channel | Reveals only that this patient has an update; low risk, but sequential ids are guessable | Use opaque identifiers in channel names |
| 9 | Email and SMS contact details | A wrong or changed number sends to the wrong person (even generic messages leak that care happened) | Verify contact details by one-time code; log who changed them |
| 10 | Front desk phone calls | Manual workload and no record of outcomes | Record the call outcome in the outbox row; report the count per week |
| 11 | Personal data rules | Health-related data of patients in India falls under the Digital Personal Data Protection Act, 2023; consent records and retention matter | I have not verified current rules; have compliance review consent records, retention and logging of messages |
| 12 | Delivery rate, time to acknowledgement and front-desk escalations are in Loki (confirmed) | These are your best evidence of reliability | Pull the real figures for the ledger, with period and source tag |

## C. Candidate AI integration ideas (for the later discussion, none built)
- Predict which patients are unlikely to log in and choose the best channel or time for them.
- Summarise a claim decision in simple language for the patient from the rule and evidence, with a person approving the wording.
- Flag likely over-dispensing or generic-substitution misses at the dispensing step.
- Detect unusual claim or wastage patterns for the management dashboard.
Each needs a clear metric and a human in the loop for anything the patient sees.

## D. Corrections made to the reference code during this review
1. The leakage view returned every claim, including claims with no leakage, so a dashboard summing it would have overstated leakage. Fixed: claims without leakage are excluded, each type has its own amount, and priority order is documented. Logic tested on the generated data (3,224 leakage claims out of 12,000, no empty types, no negative amounts). Not run on Oracle.
2. A suggestion's price was read from the current drug price, so a later price change would alter an old bill. Fixed: the price is frozen when the suggestion is made.

## E. Third review: resolved and remaining
Resolved:
1. Login depends on SMS and login is the acknowledgement, but the code comes from a different SMS provider, and the login screen also offers the code by email (SMS is the default). A notification-SMS outage cannot block login.
2. Quiet hours (6 am to 9 pm): night updates wait until 6 am and the 10-minute cycle then continues, as in the reference worker.
3. Temporary authorization: 30 minutes or logout.
4. Snapshots are system-generated, timestamped, read-only and show who is logged in.
5. The 2.5-minute longest delay was the time until the patient received the message, in both tests, shorter than the 10-minute cycle.
6. Audit trails: Internal Audit and the system team own what happens to unmarked trails (separate table, retention period, analysis for suspicious activity). That is outside the APEX app. Good separation of duties: the team that builds and runs the app does not alone decide what is deleted.

Remaining:
1. One-time code and session rules (validity, attempts, lockout, session timeout).
2. Access after discharge and after the claim closes.
3. Whether the insurer had any access. I had written "hospital and insurer look at the same record"; your words were only "one point of truth", so I removed the insurer claim until you confirm.
4. Quarterly audit means an improper edit could go unnoticed for up to three months; the manager authorization and per-change log are the real control.

## F. Insurer API integration: answers and what remains
Resolved: rules per insurer, versioned; marker before sending and idempotency key at the API (strong design); insurer tag locks a submission; retries until the insurer is up, with the API health checker alerting the claims team; "decision pending at insurer end" while waiting; rejection codes mapped to plain-language text, new codes sent in advance by the insurer; consent at admission; credentials with encrypted transport; zip password random, encrypted with the insurer's public key and sent through a secure API call; lockout 3 hours with automatic unlock; access beyond 7 days approved by hospital administration.
Resolved in the last round: the duplicate check looks at the patient's current status (an open claim); the zip password goes through a small key-delivery service for the insurer.
Remaining:
1. A national id can be linked to the patient id. Keep any real or sample national id out of the repo, logs and messages; the reference app uses synthetic ids only.

## G. Business results from the hospital accounts team
Five headline figures were reported (cost down 30%, rejections down 10%, wastage down 20%, generic substitution up 30%, processing time at the APEX end down 40%). All five were measured by the accounts team over 90 days against the preceding 90 days. Still needed: the underlying counts or rates (so relative versus percentage points is clear for rows 2 and 4) and your own share for each row. Do not add them together, since they overlap, and the wastage figure came with a hospital process change (centralized drug distribution).

## H. Build sequence (raw material for section 5)
- The APEX UI began about day 90 of 180, so the claims team saw APEX screens only after the first half; earlier feedback came from the PWA and the data tests.
- The real gateway was integrated only in phase 4 (days 135 to 165), so integration risk sat late; the dummy gateway reduced but did not remove it.
- Phase 5 was 15 days for production, live-data and security testing, a short window.

## I. Upgrade options parked for section 5 (reference app)
- Bill screen in the PWA, since the reference app sends billing details by email only; the delivered design showed the bill in the app.
- Simulated OTP login (5-minute code, 3 attempts, 3-hour lockout, email-code option), 30-minute session timeout and an audit trail. They were left out of the demo because they need real providers and sessions to mean anything.
- Invoice email with encrypted PDF and separately delivered password, not built in the reference app.
- Open question for the PDF design: the channel for the password.
- Invoice PDF password (interim: registered email plus year of birth): replace with a secret that is not in the mailbox, for example a one-time password sent by SMS or a download link that needs the app login. Normalise the email to lower case before using it.
- Priority update type: marked by the claims manager or the hospital chief administrative officer; only the marker can cancel it, after a satisfactory reply, with remarks. The usual messages go out marked as priority and the front desk calls at once, but the 6 am to 9 pm window still applies. Risk to mention in section 5: a priority stays open until its marker closes it, so if the marker is away it can stay open; consider a reassignment or a reminder. Open points are bracketed in docs/architecture.md.
- Insurer flow: `uq_one_submission_per_claim` means a rejected claim cannot be corrected and resubmitted or appealed as a new submission. Ask how the delivered system handled a corrected resubmission.
- Insurer flow: the one-open-claim-per-patient rule may block a legitimate second claim during a long treatment. Ask whether a claim covered a whole episode or a single dispense.
- Upgrade option for section 5: allow a rejected claim to be corrected and resubmitted, or appealed, through the app (now handled manually by the claims team, which leaves no trail in the app).
- The delivered system kept a part-reimbursement option for phased payment to long-term patients, with phase lengths that differ by insurer. The reference model has no phases: `v_claim_leakage` counts any gap between claimed and approved as leakage, so unpaid later phases would show as leakage until they are paid. Do not present the reference leakage figures as if they allowed for phases.
- Part payments for long-term patients arrived through the insurer's API. The reference model has no payment rows; a `claim_payments` table (claim, part number, amount, date received) would be the upgrade, and `v_claim_leakage` would then compare the claimed amount with the sum of parts received for completed claims only.

## J. Security and audit review (stop 5)
- Fixed in the sketch: the claims edit trigger would have blocked the insurer-integration account when it recorded a decision, because that account holds no manager authorization. It now passes, and its changes are still logged with no manager. A claims manager can no longer authorize themselves (check constraint). The log now also records the claimed amount, which was missing.
- Still open in the sketch: only UPDATE on claims is audited. Inserts, deletes and edits on other tables (advisories decisions, rules, priority markings) are not. Decide whether the delivered system audited them.
- The append-only rule is a commented REVOKE. A schema owner or DBA can still change the log. Section 5 option: hash-chain the log rows or copy them to a store the application owner cannot write to.
- Staff session timeout is stated only for the patient party (30 minutes). Ask what applied to staff and doctors.
- For Germany: health data is special-category data under the GDPR. Expect questions on consent, the right to erasure against audit retention, and where the data lives. These are not answered in the case study, and I am not a lawyer.
- Delivered system audited edits to other tables too, in a separate log (confirmed). The sketch covers claims only.
- GDPR and the log data (my comment, not legal advice): consent is not the main legal basis for hospital care and billing (health care provision, Art. 9(2)(h), and legal obligations are); consent fits optional things such as notification channels and patient-party access. Erasure is not automatic for medical and billing records (Art. 17(3)(b), (c), (e)). The audit log is personal data of patients and staff, so it needs a written purpose, a written retention period, access control, and as little patient data as possible in it. "Kept until Internal Audit decides" is not a retention period. A data protection impact assessment would be expected for large-scale health data. The delivered system was built under Indian rules; in interviews say "GDPR-aware design", never "GDPR compliant".
