// Shared helpers for the Felix V site. Needs i18n.js loaded first.
const TK = (key, type = "view") => `https://files.transkribus.eu/Get?id=${encodeURIComponent(key)}&fileType=${type}`;
const IIIF = key => `https://files.transkribus.eu/iiif/2/${encodeURIComponent(key)}`;
const IIIF_IMG = (key, size) => `${IIIF(key)}/full/${size}/0/default.jpg`;
async function iiifSource(key) { // OpenSeadragon 4.1 trips over "sizes" in this info.json
  const info = await getJSON(`${IIIF(key)}/info.json`);
  delete info.sizes;
  return info;
}
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
const LANGS = ["de", "fr", "la"];

// language: ?lang= wins, then the viewer's last choice, then the browser, then German
const LANG = (() => {
  const q = new URLSearchParams(location.search).get("lang");
  if (LANGS.includes(q)) { try { localStorage.setItem("felix-lang", q); } catch (e) { /* storage blocked */ } return q; }
  try { const s = localStorage.getItem("felix-lang"); if (LANGS.includes(s)) return s; } catch (e) { /* storage blocked */ }
  const nav = (navigator.language || "").slice(0, 2);
  return nav === "fr" ? "fr" : nav === "la" ? "la" : "de";
})();
document.documentElement.lang = LANG;

// internal links carry the language, so it survives even where storage is blocked
document.addEventListener("click", ev => {
  const a = ev.target.closest && ev.target.closest("a[href]");
  if (!a) return;
  const href = a.getAttribute("href");
  if (!/^[\w-]+\.html(\?|#|$)/.test(href) || /[?&]lang=/.test(href)) return;
  const [path, hash = ""] = href.split("#");
  a.setAttribute("href", `${path}${path.includes("?") ? "&" : "?"}lang=${LANG}${hash ? "#" + hash : ""}`);
}, true);

function t(key, vars = {}) {
  let s = I18N[LANG][key] ?? I18N.de[key] ?? key;
  if (typeof s !== "string") return s;
  return s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
}

function num(n) { return LANG === "la" ? String(n) : Number(n).toLocaleString(LANG === "fr" ? "fr-CH" : "de-CH"); }

function applyI18n(root = document) {
  root.querySelectorAll("[data-i18n]").forEach(el => { el.innerHTML = t(el.dataset.i18n); });
  root.querySelectorAll("[data-i18n-attr]").forEach(el => {
    for (const pair of el.dataset.i18nAttr.split(";")) {
      const [attr, key] = pair.split(":");
      el.setAttribute(attr.trim(), t(key.trim()));
    }
  });
  root.querySelectorAll("[data-i18n-th]").forEach(row => { // a <tr> whose cells come from a list
    const nums = (row.dataset.num || "").split(",").filter(Boolean).map(Number); // right-aligned columns
    row.innerHTML = t(row.dataset.i18nTh).map((h, i) => `<th${nums.includes(i) ? ' class="num"' : ""}>${h}</th>`).join("");
  });
}

function setTitle(key, vars) { document.title = `${t(key, vars)}${key === "title.index" ? "" : " – " + t("brand")}`; }

function langHref(l) {
  const u = new URLSearchParams(location.search); u.set("lang", l);
  return `?${u.toString()}`;
}

function header(active) { // Thun-style top bar: brand, navigation pills, language switch
  const items = [["index.html", "nav.vols"], ["eintraege.html", "nav.entries"], ["regesten.html", "nav.regests"], ["register.html", "nav.register"], ["methode.html", "nav.method"]];
  const nav = items.map(([h, k]) => `<a href="${h}"${active === h ? ' class="on" aria-current="page"' : ""}>${t(k)}</a>`).join("");
  const sw = LANGS.map(l => l === LANG
    ? `<strong aria-current="true" title="${I18N[l]["lang.name"]}">${l.toUpperCase()}</strong>`
    : `<a href="${langHref(l)}" hreflang="${l}" lang="${l}" title="${I18N[l]["lang.name"]}">${l.toUpperCase()}</a>`).join("");
  document.body.insertAdjacentHTML("afterbegin",
    `<header class="top"><a class="brand" href="index.html">${t("brand")} <span>· ${t("brand.sub")}</span></a>
      <nav>${nav}<span class="lang" role="group" aria-label="Sprache · Langue · Lingua">${sw}</span></nav></header>`);
  applyI18n();
}

async function getJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function fmtDate(d) {
  if (!d || !d.iso) return "";
  const [y, m, day] = d.iso.split("-");
  const mon = MONTHS_L[LANG][+m];
  if (!day) return `${mon} ${y}`;
  if (LANG === "de") return `${+day}. ${mon} ${y}`;
  if (LANG === "fr") return `${+day === 1 ? "1er" : +day} ${mon} ${y}`;
  return `${+day} ${mon} ${y}`;
}

function dateFlag(d) {
  if (!d || !d.iso) return "";
  if (d.inherited) return `<span class="muted" title="${t("flag.supra.t")}">${t("flag.supra")}</span>`;
  if (d.check === "ok") return `<span class="flag-ok" title="${t("flag.ok.t")}">${t("flag.ok")}</span>`;
  if (d.check === "range") return `<span class="flag-bad" title="${t("flag.range.t")}">${t("flag.range")}</span>`;
  if (d.check === "mismatch") return `<span class="flag-bad" title="${t("flag.bad.t")}">${t("flag.bad")}</span>`;
  return `<span class="muted" title="${t("flag.none.t")}">${t("flag.none")}</span>`;
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
