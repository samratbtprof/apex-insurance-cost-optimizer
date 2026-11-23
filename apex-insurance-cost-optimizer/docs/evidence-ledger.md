# Evidence ledger

Rule: no number appears in the case study, resume or interviews unless it has a row here.
Source tags: **measured** (I saw it in system data), **client-reported** (the client told me the outcome; no document held, because the work is under NDA), **estimated** (my calculation or recollection).
Use a range if a point value is not defensible. Credit only my own share of the result.

| # | Claim | Baseline | Result | Period | Source tag | My share | Evidence I can show | Range if unsure |
|---|---|---|---|---|---|---|---|---|
| 1 | Pharmacy dispensing cost saving | Total dispensary cost in the preceding 90 days | 30% lower total dispensary cost | 90 days | client-reported (hospital accounts team, measured over 90 days) | Product owner, all five phases (note A). Share of the application versus hospital process changes not separated | None held (NDA); outcome as reported to me by the client | none; stated as a single figure |
| 2 | Claim rejection rate (rejections at the insurer end) | Rejections by the insurer in the preceding 90 days | Down 10% (write "down 10%" exactly; relative or points not confirmed, never write "points") | 90 days | client-reported (hospital accounts team, measured over 90 days) | Product owner (note A). The decision is the insurer's; I do not claim the insurer's side | None held (NDA); outcome as reported to me by the client | none; stated as exact |
| 3 | Drug wastage (expiry) value, branded and generic | Wastage on drugs, branded and generic, in the preceding 90 days | Down 20%, with centralized drug distribution | 90 days | client-reported (hospital accounts team, measured over 90 days) | Product owner (note A). The result came from the application together with the hospital's centralized distribution change, which together improved drug expiry management; the split between them is not separated | None held (NDA); outcome as reported to me by the client | none; stated as a single figure |
| 4 | Generic substitution rate (generic drugs issued by the dispensary) | Before the app, branded drugs were routinely pushed to patients and wastage was high | Up 30% exactly (write "up 30%"; relative or points not confirmed) | 90 days | client-reported (hospital accounts team, measured over 90 days) | Product owner (note A) | None held (NDA); outcome as reported to me by the client | none; stated as exact |
| 5 | Time to process a claim (at the APEX end only, not the insurer's time) | Preceding 90 days, before almost all of the process was digitized and automated | Down 40% | 90 days | client-reported (hospital accounts team, measured over 90 days) | Product owner (note A) | None held (NDA); outcome as reported to me by the client | none; stated as a single figure |
| 6 | Scale: client maximum | n/a | 300 beds (client requirement) | [ ] | client-reported | n/a | [ ] | n/a |
| 6b | Load test, ceiling case at full capacity | [ ] | 500 beds; 2 updates per bed per day taken to the cap of 5 sends (10 SMS and 10 email per bed, about 10,000 sends), push via Redis over Web Push; stable; longest delivery delay about 2.5 min (SMS provider) | not recalled | estimated (recollection; no report or log held) | [ ] | None held (NDA) | 1.67x the client maximum |
| 6c | Failure test: SMS and email redirected to a void | [ ] | Retries ran as designed; new Redis and Python unit started; event logged; front desk alerted; longest delivery delay also about 2.5 min | not recalled | estimated (recollection; no report or log held) | [ ] | None held | [ ] |
| 7 | Client sign-off and extended service | n/a | Sign-off after 3 months in production (same 90 days as rows 1 to 5); client then signed an extended post-production service agreement of 2 years | 3 months live; 2-year term | estimated (recollection; no document held) | [ my share ] | None held (NDA) | n/a |

Rows for delivery rate, time to acknowledgement, front-desk escalations and notifications per day were removed: the logs are no longer accessible, so no figures for them will be claimed. The design facts about what was logged stay in docs/architecture.md.

Note A (my share, rows 1 to 5, all five phases). As product owner I kept the client's data from the business requirement document from before development, compared it with the results after deployment, and presented a comparative analysis report to senior management and the client, and a presentation to the product and tech teams. Throughout, I kept and updated the product and sprint backlogs, adjusted change requirements, discussed functional and technical issues, removed road blocks, and kept the client and all stakeholders informed of updates and problems. This is my share: it is not a claim that I alone caused the outcomes.

ROI to the client: not stated. It is the client's monetary gain and is under NDA.

Period caveat (rows 1 to 5): each figure compares the first 90 days after go-live with the preceding 90 days. It is not a full financial year. Do not annualize it, and do not describe it as a yearly saving. The two windows were not matched for season, so part of any change may be seasonal; say "over the first 90 days" every time.

Rows 1 to 5: do not add these percentages together. Lower dispensing cost, higher generic substitution and lower wastage overlap, and some come from a hospital process change (centralized drug distribution) and not from the application. State each row's own share.

Synthetic-data figures (e.g. 15% claimed-vs-approved gap in the generated set) belong only in the repo README as demo output, never in this table.
