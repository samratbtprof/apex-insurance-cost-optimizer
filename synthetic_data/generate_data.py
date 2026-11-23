"""Synthetic data generator for apex-insurance-cost-optimizer.

All data is invented. Seeded patterns (generic-substitution misses, over-dispensing,
off-formulary dispensing, expiry wastage, late claims) are placed at known rates so the
dashboard can be checked against ground truth. Not client data; reference implementation only.

Usage: python3 generate_data.py [--out ../data] [--seed 42] [--members 3000]
"""
import argparse, csv, os, random
from datetime import date, timedelta

p = argparse.ArgumentParser()
p.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
p.add_argument("--seed", type=int, default=42)
p.add_argument("--members", type=int, default=3000)
a = p.parse_args()
random.seed(a.seed)
os.makedirs(a.out, exist_ok=True)

START, END = date(2025, 1, 1), date(2025, 12, 31)

# ---- reference tables ----
providers = [(1, "Synthetic General Hospital", "HOSPITAL"), (2, "Synthetic City Clinic", "CLINIC"),
             (3, "Synthetic Care Pharmacy", "PHARMACY"), (4, "Synthetic Metro Hospital", "HOSPITAL"),
             (5, "Synthetic Community Clinic", "CLINIC")]
plans = [(1, "Basic", 6000, 20, "Y"), (2, "Standard", 12000, 10, "Y"), (3, "Premium", 24000, 5, "N")]

# generic_group -> (branded unit cost, generic unit cost, shelf life days)
groups = {"Metformin": (9.0, 6.0, 730), "Atorvastatin": (14.0, 9.0, 730), "Amlodipine": (8.0, 5.5, 730),
          "Omeprazole": (11.0, 7.0, 540), "Azithromycin": (38.0, 26.0, 365), "Amoxicillin": (20.0, 13.0, 365),
          "Telmisartan": (16.0, 10.5, 730), "Pantoprazole": (13.0, 8.5, 540), "Cetirizine": (5.0, 3.2, 730),
          "Insulin Glargine": (420.0, 340.0, 365)}
drugs, drug_id = [], 0
for g, (b, gen, shelf) in groups.items():
    drug_id += 1
    drugs.append([drug_id, f"{g} (brand)", g, "N", b, shelf, "Y"])
    drug_id += 1
    drugs.append([drug_id, f"{g} (generic)", g, "Y", gen, shelf, "Y"])
# a few off-formulary specialty items
for n, c in [("Specialty Brand X", 95.0), ("Specialty Brand Y", 140.0)]:
    drug_id += 1
    drugs.append([drug_id, n, n, "N", c, 365, "N"])
dm = {d[0]: d for d in drugs}
by_group = {}
for d in drugs:
    by_group.setdefault(d[2], {})["Y" if d[3] == "Y" else "N"] = d[0]

members = [(i, random.choices([1, 2, 3], [0.5, 0.35, 0.15])[0],
            random.choice(["0-17", "18-34", "35-49", "50-64", "65+"]),
            random.choice(["TIER1", "TIER2", "TIER3"])) for i in range(1, a.members + 1)]
plan_of = {m[0]: m[1] for m in members}

# ---- transactions ----
RATE = dict(branded_when_generic=0.30, over_dispense=0.06, off_formulary=0.03,
            late_claim=0.04, near_expiry=0.05)
rx_rows, ds_rows, cl_rows = [], [], []
n_rx = a.members * 4
span = (END - START).days
for rx_id in range(1, n_rx + 1):
    mid = random.randint(1, a.members)
    prov = random.choices([1, 2, 3, 4, 5], [0.3, 0.15, 0.2, 0.25, 0.1])[0]
    rx_date = START + timedelta(days=random.randint(0, span))
    qty = random.choice([10, 14, 20, 28, 30, 60])
    if random.random() < RATE["off_formulary"]:
        did = random.choice([d[0] for d in drugs if d[6] == "N"])
    else:
        g = random.choice(list(groups))
        did = by_group[g]["N" if random.random() < 0.55 else "Y"]
    rx_rows.append([rx_id, mid, prov, did, rx_date.isoformat(), qty])

    ds_drug = did
    d = dm[did]
    # dispensing: branded may be swapped to generic most of the time; leakage = missed swap
    if d[3] == "N" and d[6] == "Y":
        if random.random() > RATE["branded_when_generic"]:
            ds_drug = by_group[d[2]]["Y"]
    ds_qty = qty + (random.choice([2, 4, 6, 10]) if random.random() < RATE["over_dispense"] else 0)
    ds_date = rx_date + timedelta(days=random.randint(0, 2))
    near = random.random() < RATE["near_expiry"]
    shelf_left = random.randint(5, 29) if near else random.randint(60, dm[ds_drug][5])
    expiry = ds_date + timedelta(days=shelf_left)
    unit_paid = round(dm[ds_drug][4] * random.uniform(0.97, 1.05), 2)
    ds_id = rx_id
    ds_rows.append([ds_id, rx_id, ds_drug, ds_date.isoformat(), ds_qty, expiry.isoformat(), unit_paid])

    # ---- claim + reimbursement rules ----
    claimed = round(ds_qty * unit_paid, 2)
    late = random.random() < RATE["late_claim"]
    claim_date = ds_date + timedelta(days=random.randint(31, 60) if late else random.randint(1, 20))
    approved, status, rule = claimed, "APPROVED", ""
    dd = dm[ds_drug]
    if dd[6] == "N":
        approved, status, rule = 0.0, "REJECTED", "R01_OFF_FORMULARY"
    elif (claim_date - ds_date).days > 30:
        approved, status, rule = 0.0, "REJECTED", "R04_LATE_CLAIM"
    elif ds_qty > qty:
        approved, status, rule = round(qty * unit_paid, 2), "SHORT_PAID", "R02_QTY_EXCEEDS_RX"
    elif dd[3] == "N":
        gen_cost = dm[by_group[dd[2]]["Y"]][4]
        cap = round(ds_qty * gen_cost * 1.10, 2)
        if cap < claimed:
            approved, status, rule = cap, "SHORT_PAID", "R03_GENERIC_CAP"
    cl_rows.append([rx_id, ds_id, mid, claim_date.isoformat(), claimed, approved, status, rule])

# ---- wastage ----
waste = []
wid = 0
for prov in [1, 3, 4]:
    for month in range(1, 13):
        for _ in range(random.randint(3, 7)):
            wid += 1
            d = random.choice(drugs)
            reason = random.choices(["EXPIRED", "OVERSTOCK", "DAMAGED"], [0.6, 0.3, 0.1])[0]
            waste.append([wid, d[0], prov, date(2025, month, random.randint(1, 28)).isoformat(),
                          random.randint(20, 400), reason])

# ---- pharmacy advice (generated last so earlier tables keep identical values) ----
NOTES = ["Doctor advised a cheaper generic alternative is available, patient may choose.",
         "Pharmacist suggests an additional item to go with this prescription.",
         "Suggested supplement to support the prescribed course, optional.",
         "Alternative brand suggested because the prescribed one is out of stock."]
# patient notes follow the decision (and coverage), so a note never contradicts the choice
NOTES_ACCEPT_COVERED = ["Prefer to take the doctor's advice.", "Happy to go with the suggestion."]
NOTES_ACCEPT_UNCOVERED = ["I understand it is not covered and accept the charge."]
NOTES_DECLINE = ["Not needed right now.", "Will discuss with my doctor."]
plan_form = {p[0]: p[4] for p in plans}
adv = []
aid = 0
for rx_id, mid, prov, did, rx_date, qty in rx_rows:
    if random.random() < 0.12:
        for _ in range(random.choice([1, 1, 2])):
            aid += 1
            d = random.choice(drugs)
            covered = "Y" if (d[6] == "Y" or plan_form[plan_of[mid]] == "N") else "N"
            decided = random.random() < 0.4
            dec = random.choice(["ACCEPTED", "DECLINED"]) if decided else ""
            adv.append([aid, rx_id, d[0], random.choice([1, 2, 5, 10]), "PHARMACIST",
                        random.choice(NOTES), covered, dec,
                        (random.choice(NOTES_DECLINE if dec == "DECLINED" else NOTES_ACCEPT_COVERED if covered == "Y" else NOTES_ACCEPT_UNCOVERED) if decided else ""), "", d[4]])

def w(name, header, rows):
    with open(os.path.join(a.out, name), "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

w("providers.csv", ["provider_id", "provider_name", "provider_type"], providers)
w("insurance_plans.csv", ["plan_id", "plan_name", "annual_premium", "copay_pct", "formulary_required"], plans)
w("members.csv", ["member_id", "plan_id", "age_band", "city_tier"], members)
w("drug_master.csv", ["drug_id", "drug_name", "generic_group", "is_generic", "unit_cost", "shelf_life_days", "on_formulary"], drugs)
w("prescriptions.csv", ["rx_id", "member_id", "provider_id", "drug_id", "rx_date", "rx_qty"], rx_rows)
w("dispense_records.csv", ["dispense_id", "rx_id", "drug_id", "dispense_date", "dispensed_qty", "batch_expiry", "unit_cost_paid"], ds_rows)
w("claims.csv", ["claim_id", "dispense_id", "member_id", "claim_date", "claimed_amount", "approved_amount", "status", "rule_code"], cl_rows)
w("stock_wastage.csv", ["wastage_id", "drug_id", "provider_id", "written_off", "qty", "reason"], waste)
w("advisories.csv", ["advisory_id", "rx_id", "drug_id", "item_qty", "suggested_by", "note", "covered_flag", "patient_decision", "patient_note", "decided_at", "unit_price"], adv)
print(f"wrote {len(rx_rows)} prescriptions/dispenses/claims, {len(waste)} wastage rows to {os.path.abspath(a.out)}")
