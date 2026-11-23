"""Turn the generated CSVs into Oracle INSERT scripts (data/sql/), so the data can be loaded
with SQL Workshop > SQL Scripts instead of the Data Workshop wizard. Dates use ANSI DATE literals,
so no date-format mask is needed. Usage: python3 make_sql_load.py [--data ../data] [--rows 3000]
Reference tool; not run against Oracle by its author."""
import argparse, csv, os

p = argparse.ArgumentParser()
p.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "..", "data"))
p.add_argument("--rows", type=int, default=3000, help="rows per script file")
a = p.parse_args()
out = os.path.join(a.data, "sql")
os.makedirs(out, exist_ok=True)

ORDER = ["providers", "insurance_plans", "members", "drug_master", "prescriptions",
         "dispense_records", "claims", "stock_wastage", "advisories"]
DATES = {"rx_date", "dispense_date", "batch_expiry", "claim_date", "written_off", "decided_at"}
TEXT = {"provider_name", "provider_type", "plan_name", "formulary_required", "age_band", "city_tier",
        "drug_name", "generic_group", "is_generic", "on_formulary", "status", "rule_code", "reason",
        "suggested_by", "note", "covered_flag", "patient_decision", "patient_note"}
BLOCK = 500  # inserts per PL/SQL block


def lit(col, v):
    if v == "":
        return "NULL"
    if col in DATES:
        return f"DATE '{v}'"
    if col in TEXT:
        assert "&" not in v, v
        return "'" + v.replace("'", "''") + "'"
    float(v)  # numeric: fail loudly if not a number
    return v


for n, t in enumerate(ORDER, 1):
    rows = list(csv.reader(open(os.path.join(a.data, f"{t}.csv"))))
    head, body = rows[0], rows[1:]
    cols = ", ".join(head)
    for k, start in enumerate(range(0, len(body), a.rows), 1):
        chunk = body[start:start + a.rows]
        name = f"{n:02d}_{t}_part{k}.sql"
        with open(os.path.join(out, name), "w") as f:
            f.write(f"-- {t}: rows {start + 1} to {start + len(chunk)} of {len(body)} (synthetic data)\n")
            for b in range(0, len(chunk), BLOCK):
                f.write("BEGIN\n")
                for r in chunk[b:b + BLOCK]:
                    f.write(f"INSERT INTO {t} ({cols}) VALUES ({', '.join(lit(c, v) for c, v in zip(head, r))});\n")
                f.write("END;\n/\n")
            f.write("COMMIT;\n")
        print(name)
