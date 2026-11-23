const $ = (id) => document.getElementById(id);
let member = null, es = null, current = null;
const money = (n) => "₹" + Number(n).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});

function toast(text) {
  const t = $("toast");
  t.textContent = text; t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 4500);
  // when the app is in the background, surface it as a system notification (if allowed)
  if (document.hidden && "Notification" in window && Notification.permission === "granted") {
    navigator.serviceWorker.ready.then((r) => r.showNotification("My Claims", { body: text, icon: "icon.svg" }));
  }
}

function render(v) {
  current = v;
  $("who").textContent = `Patient ${v.member_id} · ${v.plan} plan`;
  // Reference app scope: no bill screen. Billing details go to the patient party by email (encrypted PDF).
  $("bill").innerHTML = `<div class="card muted">Your choices are recorded here. Billing details are sent to you by email.</div>`;
  $("items").innerHTML = v.items.map((i) => `
    <div class="card">
      <div class="row"><strong>${esc(i.drug)}</strong><span class="pill ${i.claim.status}">${i.claim.status.replace("_", " ")}</span></div>
      <div class="muted">${esc(i.date)} · quantity ${i.qty}</div>
      <p style="margin:8px 0 0">${esc(i.claim.reason)}</p>
      ${i.claim.status !== "APPROVED" ? `<div class="muted">Claimed ${money(i.claim.claimed)} · approved ${money(i.claim.approved)} · rule ${esc(i.claim.rule)}</div>` : ""}
      ${i.advisories.map(adv).join("")}
    </div>`).join("");
}

function adv(a) {
  const tick = a.covered ? '<span class="pill covered">✔ Covered by insurance</span>' : '<span class="pill uncovered">✖ Not covered by insurance</span>';
  const decided = a.decision
    ? `<div class="muted">You ${a.decision.toLowerCase()} this${a.patient_note ? ": " + esc(a.patient_note.replace(/[.\s]+$/, "")) : ""}.</div>`
    : `<textarea id="n${a.advisory_id}" rows="2" placeholder="Add a note (optional)"></textarea>
       <div class="row" style="margin-top:8px;justify-content:flex-start">
         <button onclick="decide('${a.advisory_id}','ACCEPTED')">Accept</button>
         <button class="ghost" onclick="decide('${a.advisory_id}','DECLINED')">Decline</button></div>`;
  return `<div class="adv"><div class="row"><span><strong>Suggestion:</strong> ${esc(a.drug)} × ${a.qty}</span>${tick}</div>
    <div class="muted">${esc(a.by.toLowerCase())}: ${esc(a.note)} · ${money(a.cost)}</div>${decided}</div>`;
}

async function decide(id, decision) {
  const note = ($("n" + id) || {}).value || "";
  const r = await fetch(`/api/decision/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ decision, note }) });
  if (r.ok) render(await r.json());
}

async function load(mid) {
  member = mid;
  render(await (await fetch(`/api/patient/${mid}`)).json());
  if (es) es.close();
  es = new EventSource(`/events/${mid}`);
  es.onopen = () => { $("live").textContent = "live"; $("live").classList.add("on"); };
  es.onerror = () => { $("live").textContent = "reconnecting"; $("live").classList.remove("on"); };
  es.onmessage = async (e) => {
    const ev = JSON.parse(e.data);
    toast(ev.text);
    render(await (await fetch(`/api/patient/${member}`)).json());
  };
}

$("simulate").onclick = async () => {
  if (!current || !current.items.length) return;
  if ("Notification" in window && Notification.permission === "default") Notification.requestPermission();
  await fetch("/api/demo/pharmacy-note", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rx_id: current.items[0].rx_id, drug_id: "21", qty: 1, note: "Pharmacist suggests an additional item; please review." }) });
};

(async () => {
  const ids = await (await fetch("/api/members")).json();
  $("member").innerHTML = ids.map((i) => `<option value="${i}">Patient ${i}</option>`).join("");
  $("member").onchange = (e) => load(e.target.value);
  load(ids[0]);
})();
