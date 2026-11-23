# Case study: Health insurance cost optimization with pharmacy dispensing

## 1. Product owner layer

**The problem.** Patients were often left in the dark about their insurance claims. A claim could be rejected or reduced without a clear reason or evidence, and charges were not explained beforehand. Behind that, the hospital pharmacy worked from handwritten prescriptions or a nurse relaying a doctor's order by phone, so doses and drug choices were easy to get wrong, and costlier branded drugs were often dispensed when a cheaper generic was available. Money was lost on every side and nobody could see where.

**What I built.** One application where the prescription, the dispensing record and the claim sit together, so any claim outcome can be traced to a clear reason. Patients became a stakeholder in the process, not just the person who receives the bill.

**What changed for users.**
- **Pharmacy staff:** before, they worked from handwritten prescriptions or phone calls, and costlier branded drugs were often dispensed when a generic was available. Now they see the doctor's name, the date and time of the prescription, the generic medicine prescribed, the dosage, times per day and number of days. Where additional items are needed, pharmacy staff add their suggestion on the doctor's advice. These notes are visible to every stakeholder, including the patient and the doctor. The patient is free to accept or decline each suggestion, with a note. The system (not the staff) marks each piece of advice as covered or not covered by insurance, and billing follows that.
- **Hospital claims team:** every rejection carries a plain-language reason and the rule behind it, every reduced amount shows its evidence, and charges are disclosed in advance, so the team can give patients a clear answer.
- **Patients:** use a browser-based app (a progressive web app, so nothing needs to be installed) with live updates pushed to it. They see the claim reason and the evidence behind any reduction, plus the suggestions from the pharmacist and doctor, each marked covered or not covered by insurance, and choose to accept or decline with a note. The bill follows their choices. Because it runs in a browser and works with screen readers, it is usable by people who are not comfortable with mobile apps, such as elderly patients.
- **Management:** a leakage and wastage dashboard that shows where money goes and why.

**A key product decision.** Patient grievances showed that people had little understanding of the claim process. I decided to make patients a stakeholder with proper inputs and visibility, and management approved it.

**Outcome.** As reported to me by the hospital accounts team, measured over 90 days: total dispensary cost 30% lower; claim rejections at the insurer end down 10% with proper documentation and reports; drug wastage down 20% with centralized drug distribution; generic substitution up 30%; time to process a claim at the APEX end down 40%. Whether the 10% and 30% changes are relative or percentage points is not confirmed, so they are written as reported. The effects overlap and must not be added together, and the wastage fall also reflects the hospital's centralized drug distribution. Each figure compares the first 90 days after go-live with the preceding 90 days; it is not a full financial year and is not annualized.

The client signed off after three months of live running, the same 90 days as these measurements, and then signed a two-year extended post-production service agreement (as I recall; I hold no sign-off document).

**My role.** Project lead, acting as both product owner and architect. We built and deployed within six months of receiving the business requirements, with a team of six including me. What I personally owned:
- Agreed the metrics and deliverables of the product with management
- Architected the front end and the back end
- Prepared the product and sprint backlogs
- Oversaw sprint delivery and code reviews, and handled design changes when requested or advised
- Kept the client's pre-development data from the business requirement document, compared it with the results after deployment, and presented a comparative analysis report to senior management and the client, and a presentation to the product and tech teams
- Throughout all five phases: kept and updated the product and sprint backlogs, adjusted change requirements, discussed functional and technical issues, removed road blocks, and kept the client and all stakeholders informed of updates and problems

## 2. Architect layer (chose X over Y because Z)

| Decision | Chose | Over | Because | Where it shows in the reference app |
|---|---|---|---|---|
| Rule engine | Rules as data, one rule set per integrated insurer, set up from that insurer's rules at integration and versioned | Hard-coded PL/SQL branches, or one common rule set | Each insurer has different rules; the claims team could change a cap or tolerance without a release | `reimbursement_rules`, `db/05_insurer_integration.sql` |
| Leakage definition | One view with a single cause per claim | Separate reports per cause | One number to reconcile with finance, no double counting | `v_claim_leakage` |
| Linking insurer and hospital | Our system holds the single record; for integrated insurers, claim data goes through the insurer's API, the insurer's tag locks the submission, and the decision returns, updates the record, raises an alert and starts the next process | Manual re-entry of claim data for every insurer | One point of truth and an automatic next step; for insurers without an API the client advised a manual process, so the integration effort went to the insurers who had one | `claim_submissions` (sketch); the API itself is not in the reference app |
| Duplicates, retries, downtime | A marker saved before sending plus an idempotency key on the API call; the insurer's returned tag locks a submission; a duplicate is rejected when the patient already has an open claim (the app checks the patient's current status); automated retries until the insurer is up, with the API health checker alerting the claims team; the claims team sees "decision pending at insurer end" | Letting the claims team resubmit by hand | A lost reply or an outage can never cause a double claim or a lost one | `claim_submissions` |
| Rejection reasons | Rejection codes stored with plain-language text at integration, and new codes sent in advance by the insurer's API to update the table; the app shows the code, the text and any insurer note | Showing the insurer's raw code | The patient party and claims team understand why a claim was rejected | `insurer_rejection_codes`, `v_claim_decision` |
| Insurers without an API | Password-protected zip of documents emailed to the insurer's assigned person; the password is randomly generated, encrypted with the insurer's public key and sent through a small key-delivery service for the insurer; the claims team enters the feedback | Building an integration for every insurer, or sending the password by email | Client's advice for the process; the password is kept off the email channel so a mailbox compromise cannot open the documents | Not in the reference app |
| UI | Oracle APEX | Custom web stack | Delivery speed, team skills, and a uniform look across the other APEX applications the organization already uses | APEX pages |
| Quantity dispensed | Strictly the prescribed days of medicine | Extra days beyond the prescription | Over-selling can lead to over-consumption and make the patient ill | Rule R02 (pay prescribed quantity only), over-dispense leakage type |
| Items dispensed | Only prescribed items | Pushing non-prescribed items | Extra items may not be covered by insurance, which puts the burden on the patient | Rule R01 (off-formulary reject), off-formulary leakage type |
| Billing | Uniform, transparent billing: every suggestion visible to patient, doctor and pharmacy, each marked covered or not by the system, patient accepts or declines with a note; claimable and non-claimable items kept apart; the claim document carries only claimable items; after approval a fresh invoice with approved and non-claimable items and a complete total, and after a rejection a plain-English reason with the insurer's decline code and an updated invoice | Items sold outside the insurance purview | Billing follows the patient's choice and the system's covered mark, so every party sees the same numbers. Because the patient party is also a stakeholder, uniform billing removes later concerns from any stakeholder | `advisories`, `v_patient_bill` |
| Items not available at a dispensary | Mark the item as unavailable, with a strict note | Referring or cross-selling between dispensaries of different hospitals | Cross-dispensary referral could create unaccountable ("shady") accounts; the strict note prevents discrepancies | Dispensary staff act only on what the app displays and nothing else; anything beyond that is the dispensary's own liability. Not modeled in the reference app |
| Patient access | Progressive web app that runs in the browser | A native mobile app that must be installed | Easy to build and maintain, including by non-mobile developers; opens on any device with a browser; any form of authentication can be implemented; screen readers can read it, which helps less confident mobile users such as elderly patients | `patient-pwa/` |
| Notifications | Transactional outbox table in the APEX database, read by a separate Python worker | APEX sending messages directly, or sending mail and SMS from the database | Not sure of APEX's own notification service; sending mail and SMS from the database was impractical; we wanted several ways to get confirmation from the patient; and delivery depends on third parties, so it stays decoupled from the rest of the system. An update is written in the same transaction as the business change, so none is lost | `notification_outbox` |
| Notification channels | Email, SMS (pre-registered templates, registered by the client before deployment and tested) and Web Push (through Redis), each patient choosing any or all at admission or enrolment, opt-out by mutual consent; all messages generic ("An update is available") | Putting details in the message | Health information stays inside the app and is shown after login; if the patient is already logged in, an alert appears in the app | `member_contact_prefs`; reference app uses in-process live updates in place of the Python worker and Redis |
| Delivery and escalation | Resend every 10 minutes until the patient logs in; 3 sends are enough in normal conditions, and if email or SMS was down or the push was ignored, up to 2 more (cap of 5); then alert the front desk, on a pending-alerts screen in the app, to call the registered number; the alert holds only the patient and the update type, and for a "priority" type also the details of the person to contact | Fire and forget | A message that is sent but never seen is not delivered; the login is the confirmation, and a human call is the last resort | `notification_outbox` (attempts, next_attempt, read_at, frontdesk_alerted_at), `notification-worker/` |
| Resilience | Workers and Redis run as one notification unit; a health checker at the API gateway pings it every 5 seconds and, on failure, starts a new unit, diverts to it, logs the event and alerts the system team | Several parallel workers per channel, or a single unsupervised worker | Patient volume is modest (client maximum 300 beds, load-tested at 500), so parallel workers add complexity with no benefit; pending updates wait in the outbox during a replacement, so nothing is lost | Documented in docs/architecture.md; reference worker is a single-loop simplification |
| Redis for push | Redis publish/subscribe | A heavier message broker | Easy to set up and suitable for simple notification publishing; it only triggers a generic alert, so losing a message is harmless | Reference app uses in-process live updates instead |
| Notification volume | At most 5 notifications per outbox entry, with per-channel sent flags and no second send before the next timer | Unlimited resends | Avoids flooding a patient when a channel misbehaves | `notification_outbox.attempts`, `notification-worker/` |
| Monitoring | Logs of the Python and Redis services in Loki, covering delivery rate, time to acknowledgement and updates escalated to the front desk; health pings every 5 seconds | No central logs | Visibility into failures of third-party delivery, and measurable evidence of reliability | Not part of the reference app |
| Scope boundary | Informational notifications only; urgent messages by phone call, backed by email from a separate address; a "priority" update type, meaning the patient party's immediate attention is needed on billing, an invoice or medicine (not a clinical matter), which gets the usual email, SMS and push messages, marked as priority, and an immediate front-desk call, without the sending window changing (nothing goes out between 9 pm and 6 am, even for priority); it is marked by the claims manager or the hospital chief administrative officer, only the person who marked it can cancel it after a satisfactory reply and enters remarks when closing it, and the front desk calls the patient party at once (inside the window), enters the result and retries up to 5 times | Treating every message as urgent | Client decision: an urgent matter should never depend on a patient opening an app | Not part of the reference app |
| Authentication | Password plus a one-time code sent to the registered phone, from a different SMS provider than the notifications | Password only, or the same SMS provider for both | Health data; the code confirms the person holds the phone given at admission; a separate provider means a notification outage or load cannot block login; the login screen has a radio button to receive the code on the registered email instead, with SMS as the default; the code is valid for 5 minutes, 3 attempts then a 3-hour lockout that releases automatically, and the patient party's session times out after 30 minutes | Not part of the reference app |
| Access and audit | Own credentials per user; claim edits need a temporary authorization from the claims manager (30 minutes or until logout) and are logged under both; patient party and doctor view only, with system-generated, timestamped snapshots that show who is logged in; audit each quarter, with important trails marked by the auditors and flagged by the system from their perspective; what happens to the unmarked trails is owned by Internal Audit and the system team, outside the application | Shared logins, free editing, or keeping every trail forever | Accountability for every change, traceable copies, and a manageable audit record | `db/04_security_audit.sql` (sketch) |
| Rule versioning | Reimbursement rules versioned | Overwriting rules | A claim is judged by the rule in force on its date | `reimbursement_rules.version_no`, `effective_from` |
| Sending window | Messages, calls and front-desk alerts only from 6 am to 9 pm, with no exception, including priority | Round-the-clock sending | Patients and front-desk staff are not disturbed at night; urgent matters use phone calls | `notification-worker/` |
| Central database | One centralized database | Separate databases per hospital | Keeps a future multi-hospital version possible; replication or merging was not designed because it was not needed then | Single database in the reference app |

Data model: see db/01_schema.sql and db/03_advisories_billing.sql (reference version, simplified from the real one). Full architecture and flow: docs/architecture.md.

## 3. Page plan for the reference app

Pages 1 to 5 are built in Oracle APEX and exported in `apex/`; the screenshots are in the README. Each page's figures were checked against numbers computed independently on the same synthetic data.

1. Leakage overview: total by cause, by month, by provider
2. Leakage drill-down: claim list with rule code and amount lost
3. Drug wastage: by reason, drug and month, with value
4. Generic substitution opportunities: branded dispensed where a generic exists
5. Rules admin: list the versioned rules and add or edit a version (tolerance %, late-claim days). It maintains the rule table only: it does not change claim decisions or any figure on the other pages
6. Patient app (PWA, runs in the browser): claims with plain-language reasons, pharmacy suggestions marked covered or not, accept or decline with a note, live updates, and billing details by email in the reference app (see patient-pwa/)

In the delivered system, management's dashboard showed leakage by cause (off-formulary dispensed, generic available but branded dispensed), leakage by month, and drug wastage by reason (expired, overstock, damaged). The other cuts (other rejection or short-pay, dispensed more than prescribed, wastage by month, and the list of drugs where a generic was available but branded dispensed) came from the accounts team's own reports. The delivered dashboard also held client-specific parameters unrelated to this app's outcomes; none are reproduced here. The reference dashboard puts all the cuts on one page for demonstration.

## 3a. How it evolved (about six months, five phases)

We built and deployed within six months of receiving the business requirements: four deployments over 170 days, then 15 days of observation and testing with no development. Each phase ended with testing before the next began. Sprints were 25 days. Each of the first four phases was one or two sprints plus a 5-day buffer for leave management, testing and fixes, which gives 30, 55, 55 and 30 days. The first three deployments went to the client's test environment; the fourth, on day 170, was the production go-live, and the 90-day outcomes and the 3-month sign-off count from it.

| Phase | Days | What was built | Why in this order |
|---|---|---|---|
| 1 | 30 (1 sprint + 5 buffer) | Patient PWA, Python middleware and a dummy API gateway | Security mattered most. The client was unsure how and where this part should be implemented, and because it sits outside APEX on the open web, we built a working version first and took the client's input from hands-on use of the app |
| 2 | 55 (2 sprints + 5 buffer) | The database: all tables and business logic, tested against the client's old data | The rules and billing logic had to be proven on real past cases before any screen depended on them |
| 3 | 55 (2 sprints + 5 buffer) | The APEX UI, connected to the data tables | With the data layer proven, screens could be built on stable tables |
| 4 | 30 (1 sprint + 5 buffer) | The real API gateway, integrated with the PWA, the Python middleware and APEX | The riskiest join was left until both sides were stable, and the dummy gateway let each side be tested alone until then |
| 5 | 15 (no development) | Observation and testing after deployment, on live data | The old real data had shown how the data behaves all through the build, so the last step was about real-scenario load and performance |

**What worked.** Every sprint ended with a product demo to all stakeholders, including the client's teams. The client had the PWA and a temporary API gateway after the first sprint and was free to give its opinion from then on.

**For a non-technical reader.** We built the part patients touch, and the part that needed the client's judgement on security, first, so the client could try it and decide. Then we built and tested the data and rules, then the staff screens, and only then joined everything through the real gateway.

**Architect view (chose X over Y because Z).**
- Chose to build the outside-APEX layer first with a stand-in gateway, over specifying it on paper first, because the client could not decide on security from a document but could from a working app.
- Chose to prove the database on the client's old data before building screens, over building screens first, because a wrong rule found after the UI exists costs rework in both.
- Chose to integrate the real gateway late (phase 4), over early, for three reasons: the client was not yet clear which services the real gateway would include; we needed a standard API gateway to build and test against in the meantime; and the client's teams were not technical enough to handle early development problems at their end. The temporary gateway let the PWA, middleware and APEX be built and tested independently.


## 3b. Testing and acceptance

**A written testing standard.** While building these APEX applications, we wrote one common testing standard that every app had to follow. It set the levels, the tools and the strategy:
- **Unit tests:** individual features: forms, reports, calculations and access permissions.
- **System and integration tests:** complete workflows, connections to other systems and overall performance.
- **Browser automation:** Chrome Recorder (records user flows without code) and Puppeteer (scripted browser actions) to replay user flows; Lighthouse for performance and accessibility.
- **Accessibility:** APEX Advisor for common issues such as missing labels or headers, plus testing with users of varying abilities and assistive technologies.
- **Strategy:** test throughout the development cycle, not only at the end.

**Two decisions on test data and change control (mine and the team's, agreed with the client).**

| Decision | Chose | Because |
|---|---|---|
| Test data before go-live | The client's old production data (pre-deployment test) | Real past cases expose rule and billing errors that invented data never would |
| Acceptance after go-live | Live data (post-production acceptance test) | Only live traffic shows real behaviour |
| Findings before go-live | We change the system to fit the data provided | The data shows how the hospital really works; the system adapts to it, not the reverse |
| Findings after go-live | We present them to the client, and any change needs a unanimous decision | A live change touches patient and claim records, so every stakeholder must agree to it |

**What we applied on this project.** Unit testing of individual features; system testing of the whole application and its integrations; automation tools (Chrome Recorder, Puppeteer, Lighthouse); and accessibility checks with APEX Advisor. For the patient PWA, we used the Application panel in Chrome DevTools to inspect the manifest, service worker and cache, and its offline option to check behaviour without a network. We also tested installation and key features on real mobile devices and browsers, because PWA capabilities vary by platform. For the API gateway and Redis, we decided on load testing and integration testing. Which tool was used for which test is not recalled.

**How this maps onto the five phases.** Every phase was tested before the next began, using the client's old production data in all of them except the last 15 days. Those last 15 days (phase 5, after deployment) were observed and tested on live data, mainly for real-scenario load and performance, and for security concerns.

**What testing on the old data found.** As I recall, not much major rework was needed. The system was built in phases and the client's input was taken at every step, so differences surfaced early and in small pieces. I do not recall the individual findings, so none are listed.

**After go-live.** One kind of change: we changed settings so that the SMS and email providers matched the client's choice. This was a configuration change, not a redesign.

**Acceptance.** The client signed off after the system had been running in production for three months, the same 90 days over which the five outcomes in section 1 were measured. The client shared its own results and findings, and its satisfaction with the product. The client then signed an extended post-production service agreement of two years (as I recall; terms are under NDA and not stated here).

**For a non-technical reader.** We tested each piece as we built it, checked the whole thing on the hospital's own past records before anyone relied on it, and then checked it again on live records after go-live. If testing on past records showed our system did not fit how the hospital really worked, we changed the system. If something turned up after go-live, we showed it to the client and changed it only when everyone agreed. The client signed off only after three months of live running.

**What this section does not claim.** The standard says what we set out to use. I have no test reports, so I do not state pass rates, defect counts, coverage or a list of defects found.


## 4. Results

Every figure carries its source (client-reported), its baseline and its period. Where a point value is not defensible, a range or the exact reported wording is used.

## 5. What I would do differently

written from our review of the delivered design and the reference app. 

### 5a. Looking back at the project

**Process**
- **Keep a findings log of every test round.** I do not recall the individual findings from testing, so I cannot show what was found and what changed. I would keep a log for each round.
- **Agree how results are measured before go-live.** The client's accounts team measured the five outcomes, which was right, since they own the books. What I would add before go-live: written definitions (relative change or percentage points), a rate next to the total, such as cost per patient-day, a note of other changes in the same window (for example centralized drug distribution), and a measurement record I am allowed to keep.

**Design**
- **Fewer messages.** The client agreed to the 10-minute wait and up to 15 messages for one update (every cycle resends on every channel). Today I would escalate by channel: a push first, then SMS, with email last, or stop SMS after one delivery receipt.
- **Let a rejected claim be corrected and resubmitted, or appealed, in the app.** The claims team did this by hand, which left no trail in the app.
- **Model part payments for long-term patients.** Insurers paid these in parts through the API. I would store each part as its own row, so unpaid later parts are not counted as lost money.
- **Do not let a priority stay open.** Only the person who marked a priority can close it. I would add a reminder and a way to hand it over if that person is away.
- **Audit more safely.** In the reference sketch a database administrator could still alter the audit log. I would chain the log rows with hashes, or copy them to a store the application owner cannot write to.
- **Write down data protection decisions.** For a German or EU setting I would write down the purpose, the retention period and a data protection impact assessment for the logs, since this is health data.

### 5b. Upgrade options for the reference app

These are left out of the reference app on purpose; the delivered design had them or they are not built.
- A bill screen in the patient app. The reference app shows suggestions and records the choice, and sends billing details by email.
- The invoice email with an encrypted PDF. For now the password is the patient's registered email plus the year of birth. I would replace it with a secret that is not in the mailbox, for example a one-time code by SMS, or a link that needs the app login.
- Simulated OTP login (5-minute code, 3 attempts, 3-hour lockout, email option), a 30-minute session timeout and an audit trail.
- A table of part payments per claim, and a leakage view that compares the claimed amount with the parts received, for completed claims only.
- Correct-and-resubmit for rejected claims.
- A reminder and a hand-over for "priority" updates that stay open.

### 5c. Where AI could help (none built)

Each idea needs a clear measure of success and a person approving anything a patient sees.

- **Channel and time:** predict which patients are unlikely to log in and choose the best channel or time for them. Measure: share acknowledged within the first cycle.
- **Plain-language claim reasons:** This is a short explanation of a decision from the rule and the evidence, with the claims team approving the wording. Measure: fewer patient questions to the front desk.
- **At the dispensing step:** flag a likely over-dispense or a missed generic before the drug is handed over. Measure: leakage in those two causes.
- **Unusual patterns:** flag unusual claims or wastage for the management dashboard. Measure: confirmed findings per month.
- **Guardrail:** no patient data goes to an outside AI service without a data protection review.

### 5d. Limits of this case study

- The five outcomes are as reported to me by the client's accounts team, over the first 90 days only. I hold no documents, and I do not annualize them.
- I hold no test reports. The load and failure tests are from memory.
- The repo is a reference implementation on synthetic data. The schema, rules, load scripts and leakage view were run on Oracle APEX and matched the expected totals (checkpoints 1 and 2 of the build guide); the five APEX pages were built and their figures matched the same independent numbers; one test row went from the APEX outbox table to a Python script over REST and back (one pass, no retries, the send step is a print); the security and insurer SQL are sketches that have not been run. The rules page edits the rule table but does not drive claim decisions. The delivered system's insurer API, gateway, health checker and Redis are described, not included.
