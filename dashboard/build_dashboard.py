"""Builds dashboard/leakage-wastage-dashboard.html from the synthetic CSVs (python3, stdlib only).
The leakage logic is taken from db/01_schema.sql (view v_claim_leakage), adapted to SQLite syntax, so the page and the
Oracle view use the same definition. All figures are synthetic, for demonstration only."""
import csv, json, os, re, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, ".."); DATA = os.path.join(ROOT, "data")

def typ(c):
    if c.endswith("_id") or c in ("rx_qty", "dispensed_qty", "item_qty", "shelf_life_days", "qty"): return "INTEGER"
    if any(k in c for k in ("amount", "cost", "price", "paid", "premium", "copay")): return "REAL"
    return "TEXT"

db = sqlite3.connect(":memory:")
for t in ["insurance_plans", "members", "drug_master", "prescriptions", "dispense_records", "claims", "stock_wastage"]:
    rows = list(csv.reader(open(os.path.join(DATA, t + ".csv")))); h = rows[0]
    db.execute(f"CREATE TABLE {t} ({','.join(c + ' ' + typ(c) for c in h)})")
    db.executemany(f"INSERT INTO {t} VALUES ({','.join('?' * len(h))})", rows[1:])
sql = open(os.path.join(ROOT, "db", "01_schema.sql")).read()
v = sql[sql.index("CREATE OR REPLACE VIEW v_claim_leakage"):sql.index("-- Wastage view")]
v = v.replace("CREATE OR REPLACE VIEW", "CREATE VIEW").replace("TRUNC(c.claim_date,'MM')", "substr(c.claim_date,1,7)")
v = v.replace("NVL(", "ifnull(").replace("GREATEST(", "max(")
db.execute(v)
q = lambda s: db.execute(s).fetchall()

claimed, approved, n_claims = q("SELECT SUM(claimed_amount), SUM(approved_amount), COUNT(*) FROM claims")[0]
leak, n_leak = q("SELECT SUM(leakage_amount), COUNT(*) FROM v_claim_leakage")[0]
waste_total = q("SELECT SUM(w.qty*d.unit_cost) FROM stock_wastage w JOIN drug_master d ON d.drug_id=w.drug_id")[0][0]
types = ["OFF_FORMULARY", "OVER_DISPENSE", "GENERIC_MISSED", "REIMBURSEMENT_LOSS"]
by_type = [dict(type=t, count=c, amount=round(a)) for t, c, a in q(
    "SELECT leakage_type, COUNT(*), SUM(leakage_amount) FROM v_claim_leakage GROUP BY 1 ORDER BY 3 DESC")]
months = sorted(r[0] for r in q("SELECT DISTINCT claim_month FROM v_claim_leakage"))
mt = {(m, t): a for m, t, a in q("SELECT claim_month, leakage_type, SUM(leakage_amount) FROM v_claim_leakage GROUP BY 1,2")}
by_month = [dict(month=m, **{t: round(mt.get((m, t), 0)) for t in types}) for m in months]
reasons = ["EXPIRED", "OVERSTOCK", "DAMAGED"]
w_reason = [dict(reason=r, amount=round(a), qty=qy) for r, a, qy in q(
    "SELECT w.reason, SUM(w.qty*d.unit_cost), SUM(w.qty) FROM stock_wastage w JOIN drug_master d ON d.drug_id=w.drug_id GROUP BY 1 ORDER BY 2 DESC")]
wm = sorted(r[0] for r in q("SELECT DISTINCT substr(written_off,1,7) FROM stock_wastage"))
wmr = {(m, r): a for m, r, a in q("SELECT substr(w.written_off,1,7), w.reason, SUM(w.qty*d.unit_cost) FROM stock_wastage w JOIN drug_master d ON d.drug_id=w.drug_id GROUP BY 1,2")}
w_month = [dict(month=m, **{r: round(wmr.get((m, r), 0)) for r in reasons}) for m in wm]
top = [dict(drug=n, claims=c, amount=round(a)) for n, c, a in q(
    "SELECT d.drug_name, COUNT(*), SUM(l.leakage_amount) FROM v_claim_leakage l JOIN claims c ON c.claim_id=l.claim_id "
    "JOIN dispense_records ds ON ds.dispense_id=c.dispense_id JOIN drug_master d ON d.drug_id=ds.drug_id "
    "WHERE l.leakage_type='GENERIC_MISSED' GROUP BY 1 ORDER BY 3 DESC LIMIT 8")]
payload = dict(kpi=dict(claimed=round(claimed), approved=round(approved), leakage=round(leak), leak_claims=n_leak, claims=n_claims,
                        waste=round(waste_total)), by_type=by_type, by_month=by_month, w_reason=w_reason, w_month=w_month, top=top)
tpl = open(os.path.join(HERE, "template.html")).read()
open(os.path.join(HERE, "leakage-wastage-dashboard.html"), "w").write(tpl.replace("/*DATA*/null", json.dumps(payload)))
print("built:", payload["kpi"], "| leakage rows by type:", {d["type"]: d["count"] for d in by_type})
