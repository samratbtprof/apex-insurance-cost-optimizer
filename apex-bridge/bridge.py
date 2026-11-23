"""Reference bridge: reads PENDING rows from the APEX outbox over REST and writes the result back.

This is the "separate Python layer" of the delivered design, reduced to the part that talks to APEX:
  1. GET  <BASE>/notification_outbox/?q={"status":"PENDING"}        read pending updates
  2. (send step)  here only printed; the real layer sends email, SMS and a Redis push with a generic text
  3. PUT  <BASE>/notification_outbox/<id>                          write the result back (status, attempts)

Needs the table REST-enabled in SQL Workshop > RESTful Services (AutoREST). Uses the standard library only.
Config by environment variables:
  APEX_REST_BASE   e.g. https://oracleapex.com/ords/<schema-alias>     (copy it from the RESTful Services page)
  APEX_REST_TOKEN  optional OAuth bearer token if you protected the table
Run:  python3 bridge.py            (one pass)       python3 bridge.py --dry-run   (read only, no write-back)
Data is synthetic. No real contact details are sent anywhere: the send step is a print.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

MAX_SENDS = 5


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=None if body is None else json.dumps(body).encode())
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "apex-bridge-reference/1.0")   # some servers refuse the default Python agent
    if body is not None:
        req.add_header("Content-Type", "application/json")
    token = os.environ.get("APEX_REST_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:      # show what the server said, not just a traceback
        sys.exit(f"HTTP {e.code} from {method} {url}\n{e.read().decode(errors='replace')[:600]}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach {url}: {e.reason}")


def pending(base):
    q = urllib.parse.quote(json.dumps({"status": "PENDING"}))
    return call("GET", f"{base}/notification_outbox/?q={q}&limit=50").get("items", [])


def send_generic(row):
    """Stand-in for email, SMS and push. The text is generic on purpose: details show only after login."""
    print(f"  would send to member {row['member_id']}: 'An update is available. Please log in.' (event {row['event_type']})")
    return True


def run(base, dry_run=False):
    rows = pending(base)
    print(f"{len(rows)} pending update(s)")
    for row in rows:
        if (row.get("attempts") or 0) >= MAX_SENDS:
            continue
        ok = send_generic(row)
        if dry_run:
            continue
        row["attempts"] = (row.get("attempts") or 0) + 1
        row["email_status"] = row["sms_status"] = row["push_status"] = "SENT" if ok else "FAILED"
        row["status"] = "SENT" if ok else "PENDING"
        body = {k: v for k, v in row.items() if k != "links"}   # ORDS adds a "links" list to each item; do not send it back
        call("PUT", f"{base}/notification_outbox/{row['outbox_id']}", body)
        print(f"  outbox {row['outbox_id']}: written back, attempts={row['attempts']}, status={row['status']}")
    return len(rows)


if __name__ == "__main__":
    base = os.environ.get("APEX_REST_BASE")
    if not base:
        sys.exit("Set APEX_REST_BASE first (see the header of this file).")
    run(base.rstrip("/"), dry_run="--dry-run" in sys.argv)
