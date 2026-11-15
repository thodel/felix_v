// Shared helpers for the Felix V site.
const TK = (key, type = "view") => `https://files.transkribus.eu/Get?id=${encodeURIComponent(key)}&fileType=${type}`;
const IIIF = key => `https://files.transkribus.eu/iiif/2/${encodeURIComponent(key)}`;
const IIIF_IMG = (key, size) => `${IIIF(key)}/full/${size}/0/default.jpg`;
async function iiifSource(key) { // OpenSeadragon 4.1 trips over "sizes" in this info.json
  const info = await getJSON(`${IIIF(key)}/info.json`);
  delete info.sizes;
  return info;
}
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
const MONTHS = ["", "Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."];

function header(active) {
  const items = [["index.html", "Bände"], ["eintraege.html", "Einträge"], ["register.html", "Register (Test)"], ["methode.html", "Methode & Tests"]];
  const nav = items.map(([h, t]) => `<a href="${h}"${active === h ? ' aria-current="page" style="font-weight:600"' : ""}>${t}</a>`).join("");
  document.body.insertAdjacentHTML("afterbegin",
    `<header class="site"><a class="brand" href="index.html">Bullarium Felix’ V.</a><nav>${nav}</nav></header>`);
}

async function getJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function fmtDate(d) {
  if (!d || !d.iso) return "";
  const [y, m, day] = d.iso.split("-");
  const s = day ? `${+day}. ${MONTHS[+m]} ${y}` : `${MONTHS[+m]} ${y}`;
  return s;
}

function dateFlag(d) {
  if (!d || !d.iso) return "";
  if (d.inherited) return `<span class="muted" title="«Datum ut supra»: vom vorangehenden Eintrag übernommen">ut supra</span>`;
  if (d.check === "ok") return `<span class="flag-ok" title="Pontifikatsjahr passt zum Datum">✓ Pont.-Jahr</span>`;
  if (d.check === "mismatch") return `<span class="flag-bad" title="Pontifikatsjahr passt nicht zum Datum: Lesefehler prüfen">⚠ prüfen</span>`;
  return `<span class="muted" title="Kein Pontifikatsjahr gelesen">ungeprüft</span>`;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
