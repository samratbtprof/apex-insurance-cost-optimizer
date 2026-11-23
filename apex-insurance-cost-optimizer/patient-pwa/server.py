"""Patient PWA reference server (python3 stdlib only, synthetic data).

Serves the PWA files and a small JSON API over the generated CSVs, and pushes live updates to
each patient's open app with Server-Sent Events (SSE).

Run:  python3 server.py            then open http://localhost:8080 (works in any browser, no install)

Scope note: live updates arrive while the app is open (or in a background tab). True background
push to a closed browser needs a push service (Web Push with VAPID keys, or the built-in push
notification feature of Oracle APEX PWA apps). That is out of scope for this stdlib demo.
"""
import csv, json, os, queue, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
LOCK = threading.Lock()


def load(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


drugs = {r["drug_id"]: r for r in load("drug_master.csv")}
plans = {r["plan_id"]: r for r in load("insurance_plans.csv")}
members = {r["member_id"]: r for r in load("members.csv")}
rx = {r["rx_id"]: r for r in load("prescriptions.csv")}
disp = {r["rx_id"]: r for r in load("dispense_records.csv")}
claims = {r["dispense_id"]: r for r in load("claims.csv")}
advisories = {r["advisory_id"]: r for r in load("advisories.csv")}
rx_by_member = {}
for r in rx.values():
    rx_by_member.setdefault(r["member_id"], []).append(r["rx_id"])
adv_by_rx = {}
for a in advisories.values():
    adv_by_rx.setdefault(a["rx_id"], []).append(a["advisory_id"])
subscribers = {}  # member_id -> list of queues

REASONS = {
    "R01_OFF_FORMULARY": "This medicine is not on your plan's approved list, so the claim was not paid.",
    "R02_QTY_EXCEEDS_RX": "More medicine was dispensed than the doctor prescribed, so only the prescribed quantity was paid.",
    "R03_GENERIC_CAP": "A cheaper generic equivalent exists, so the claim was paid at the generic price plus a small tolerance.",
    "R04_LATE_CLAIM": "The claim was filed more than 30 days after dispensing, so it was not paid.",
}


def cost(a):
    return round(float(a["item_qty"]) * float(a.get("unit_price") or drugs[a["drug_id"]]["unit_cost"]), 2)


def adv_view(a):
    return {"advisory_id": a["advisory_id"], "drug": drugs[a["drug_id"]]["drug_name"], "qty": int(a["item_qty"]),
            "cost": cost(a), "by": a["suggested_by"], "note": a["note"], "covered": a["covered_flag"] == "Y",
            "decision": a["patient_decision"] or None, "patient_note": a["patient_note"]}


def patient_view(mid):
    items, insurer, shortfall, extra = [], 0.0, 0.0, 0.0
    for rid in sorted(rx_by_member.get(mid, []), key=lambda i: rx[i]["rx_date"], reverse=True)[:12]:
        r, d = rx[rid], disp[rid]
        c = claims[d["dispense_id"]]
        claimed, approved = float(c["claimed_amount"]), float(c["approved_amount"])
        insurer += approved
        shortfall += claimed - approved
        advs = [adv_view(advisories[i]) for i in adv_by_rx.get(rid, [])]
        extra += sum(x["cost"] for x in advs if x["decision"] == "ACCEPTED" and not x["covered"])
        items.append({"rx_id": rid, "date": r["rx_date"], "drug": drugs[d["drug_id"]]["drug_name"],
                      "qty": int(d["dispensed_qty"]), "claim": {
                          "status": c["status"], "claimed": claimed, "approved": approved,
                          "reason": REASONS.get(c["rule_code"], "") if c["status"] != "APPROVED" else "Approved in full.",
                          "rule": c["rule_code"]},
                      "advisories": advs})
    m = members[mid]
    return {"member_id": mid, "plan": plans[m["plan_id"]]["plan_name"], "items": items,
            "bill": {"insurer_pays": round(insurer, 2), "claim_shortfall": round(shortfall, 2),
                     "accepted_uncovered_items": round(extra, 2),
                     "you_pay": round(shortfall + extra, 2)}}


def push(mid, event):
    for q in list(subscribers.get(mid, [])):
        q.put(event)


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=os.path.join(HERE, "app"), **k)

    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urlparse(self.path).path
        parts = path.strip("/").split("/")
        if path == "/api/members":
            ids = [m for m in sorted(rx_by_member, key=int) if adv_by_rx.get(rx_by_member[m][0])][:12]
            return self.send_json(ids)
        if parts[:2] == ["api", "patient"] and len(parts) == 3 and parts[2] in members:
            return self.send_json(patient_view(parts[2]))
        if parts[0] == "events" and len(parts) == 2 and parts[1] in members:
            q = queue.Queue()
            subscribers.setdefault(parts[1], []).append(q)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                self.wfile.write(b": connected\n\n"); self.wfile.flush()
                while True:
                    try:
                        ev = q.get(timeout=15)
                        self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                subscribers[parts[1]].remove(q)
            return
        return super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        parts = urlparse(self.path).path.strip("/").split("/")
        # patient accepts or declines an advisory, with a note
        if parts[:2] == ["api", "decision"] and len(parts) == 3 and parts[2] in advisories:
            a = advisories[parts[2]]
            if body.get("decision") not in ("ACCEPTED", "DECLINED"):
                return self.send_json({"error": "decision must be ACCEPTED or DECLINED"}, 400)
            with LOCK:
                a["patient_decision"] = body["decision"]
                a["patient_note"] = (body.get("note") or "")[:400]
            mid = rx[a["rx_id"]]["member_id"]
            push(mid, {"type": "decision", "text": f"Your choice was recorded: {body['decision'].lower()}. Billing details will be sent by email."})
            return self.send_json(patient_view(mid))
        # demo: a pharmacist adds a suggestion on a prescription; pushed live to the patient
        if parts[:3] == ["api", "demo", "pharmacy-note"] and body.get("rx_id") in rx:
            with LOCK:
                nid = str(max(map(int, advisories)) + 1)
                did = body.get("drug_id") or "21"
                m = members[rx[body["rx_id"]]["member_id"]]
                covered = "Y" if (drugs[did]["on_formulary"] == "Y" or plans[m["plan_id"]]["formulary_required"] == "N") else "N"
                advisories[nid] = {"advisory_id": nid, "rx_id": body["rx_id"], "drug_id": did,
                                   "item_qty": str(body.get("qty", 1)), "unit_price": drugs[did]["unit_cost"], "suggested_by": "PHARMACIST",
                                   "note": body.get("note", "Pharmacist suggestion."), "covered_flag": covered,
                                   "patient_decision": "", "patient_note": "", "decided_at": ""}
                adv_by_rx.setdefault(body["rx_id"], []).append(nid)
            mid = rx[body["rx_id"]]["member_id"]
            push(mid, {"type": "advisory", "text": "New suggestion from your pharmacist. Tap to review."})
            return self.send_json({"ok": True, "advisory_id": nid})
        self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Patient PWA demo on http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
