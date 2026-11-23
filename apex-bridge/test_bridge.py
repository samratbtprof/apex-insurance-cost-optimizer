"""Tests the bridge against a tiny local fake of the APEX REST service (no network, no Oracle)."""
import json, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import bridge

ROWS = {1: {"outbox_id": 1, "member_id": 7, "event_type": "CLAIM", "status": "PENDING", "attempts": 0,
            "email_status": "PENDING", "sms_status": "PENDING", "push_status": "PENDING", "links": [{"rel": "self"}]},
        2: {"outbox_id": 2, "member_id": 8, "event_type": "BILL", "status": "SENT", "attempts": 1,
            "email_status": "SENT", "sms_status": "SENT", "push_status": "SENT"}}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, obj):
        b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        q = json.loads(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)["q"][0])
        self._send({"items": [r for r in ROWS.values() if r["status"] == q["status"]]})
    def do_PUT(self):
        n = int(self.headers["Content-Length"]); row = json.loads(self.rfile.read(n))
        assert "links" not in row
        ROWS[int(self.path.rsplit("/", 1)[1])] = row; self._send(row)


srv = HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_port}"

assert bridge.run(base, dry_run=True) == 1 and ROWS[1]["status"] == "PENDING"      # dry run changes nothing
assert bridge.run(base) == 1 and ROWS[1]["status"] == "SENT" and ROWS[1]["attempts"] == 1
assert bridge.run(base) == 0                                                          # nothing pending now
print("bridge tests passed")
