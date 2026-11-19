#!/usr/bin/env python3
"""Entity linking for the Felix V register: within the corpus and to kf, SSRQ, HLS and Wikidata.

Input: the entities in data/regests/<id>.json (regest_v2: persons, places, institutions with
"as_written" and a Latin normal form). Output: data/nel/entities.json and data/nel/report.json.

Only two grades are kept, everything else stays unlinked:
  identical    same normalised name, a single candidate, dates/region fit
  very_likely  near-identical name (similarity >= 0.92) plus the same diocese or office (corpus),
               or an authority candidate the authority itself calls a match and whose dates fit

Within the corpus
  persons  cluster on the normalised full name (>= 2 name parts); single names («Lancelotus») only
           together with the same diocese or office
  places   cluster on the normalised Latin name; dioceses on a fixed list of Latin adjectives
External (cached in data/nel/cache/)
  persons  ssrq.search_name_index and kf.search_persons by exact name form
           (Human Lineage was used until 19.11.2026 and removed: the source was withdrawn)
  places   kf.search_places and Wikidata (settlements in CH/FR/IT/DE) by exact name; HLS via kf's
           hls_id or Wikidata P902; dioceses via Wikidata (diocese items, by seat)
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp_client import MCP  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
import os
REG = ROOT / os.environ.get("REGEST_OUT", "data/regests")
OUT = ROOT / "data/nel"
UA = "felix-v-nel/1.0 (research; https://github.com/thodel/felix_v)"

STOP = {"dominus", "domini", "magister", "magistri", "frater", "fratris", "dilectus", "dilecto", "venerabilis",
        "nobilis", "dompnus", "sanctus", "sancti", "beatus"}

NULLS = {"null", "none", "", "n/a", "unknown"}
TITLE_ONLY = re.compile(r"^(episcop|archiepiscop|abba|officia|prior|decan|prepositu|archidiacon|capitul|conuent|rector|cantor|"
                        r"thesaurar|sacrist|plebanu|curat|uicari|papa|cardinal)\w*( [a-z]+(is|ium|i))?$")

# Latin diocese adjectives (stems) -> seat, as Wikidata knows it
DIOCESES = {
    "gebenn": "Geneva", "lausan": "Lausanne", "sedun": "Sion", "basil": "Basel", "constanc": "Konstanz",
    "constant": "Konstanz", "curiens": "Chur", "lugdun": "Lyon", "bellic": "Belley", "maurian": "Saint-Jean-de-Maurienne",
    "tarent": "Moûtiers", "augusten": "Aosta", "taurin": "Turin", "eporedi": "Ivrea", "montisregal": "Mondovì",
    "astens": "Asti", "vercell": "Vercelli", "novari": "Novara", "bisunt": "Besançon", "cabilon": "Chalon-sur-Saône",
    "matiscon": "Mâcon", "gratianopol": "Grenoble", "viennens": "Vienne", "ebredun": "Embrun", "niciens": "Nice",
    "albingan": "Albenga", "saonens": "Savona", "argentin": "Strasbourg", "metens": "Metz", "tullens": "Toul",
    "virdun": "Verdun", "trever": "Trier", "colonien": "Cologne", "maguntin": "Mainz", "wormat": "Worms",
    "spir": "Speyer", "herbipol": "Würzburg", "bamberg": "Bamberg", "frising": "Freising", "salzburg": "Salzburg",
    "pataviens": "Passau", "ratispon": "Regensburg", "eystet": "Eichstätt", "leodien": "Liège", "traiect": "Utrecht",
    "cameracen": "Cambrai", "tornacen": "Tournai", "parisien": "Paris", "aurelian": "Orléans", "albens": "Alba",
    "mediolan": "Milan", "papiens": "Pavia", "cumana": "Como", "cumane": "Como", "laudens": "Lodi", "placentin": "Piacenza",
    "januens": "Genoa", "ianuens": "Genoa", "aquens": "Aix-en-Provence", "massil": "Marseille", "avinion": "Avignon",
    "valentin": "Valence", "dien": "Die", "vivar": "Viviers", "glandat": "Glandèves", "senec": "Senez",
}


def ascii_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("j", "i").replace("v", "u").replace("y", "i").replace("ae", "e").replace("oe", "e")
    s = s.replace("ph", "f").replace("th", "t").replace("ch", "c")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", s)).strip()


def name_key(name: str) -> str:
    parts = [p for p in ascii_key(name).split() if p not in STOP]
    # Latin case endings of the first name are noisy in the readings: compare forenames on their stem
    if parts:
        parts[0] = re.sub(r"(us|i|o|um|e|is|em)$", "", parts[0])
    return " ".join(parts)


def diocese_seat(adj: str) -> str | None:
    k = ascii_key(adj).replace(" ", "")
    for stem, seat in DIOCESES.items():
        if k.startswith(ascii_key(stem).replace(" ", "")):
            return seat
    return None


def sparql(q: str, cache: Path):
    import hashlib
    f = cache / ("sparql-" + hashlib.sha1(q.encode()).hexdigest() + ".json")
    if f.exists():
        return json.loads(f.read_text())
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                rows = json.loads(r.read())["results"]["bindings"]
            f.write_text(json.dumps(rows))
            time.sleep(0.5)
            return rows
        except Exception:  # noqa: BLE001 — 429/timeouts: back off and retry
            time.sleep(5 * (attempt + 1))
    return []


def wd_place(name: str, cache: Path) -> list[dict]:
    """Settlements in CH/FR/IT/DE whose label equals name in de/fr/it/en/la (indexed label lookup)."""
    lit = name.replace('"', "").strip()
    vals = " ".join(f'"{lit}"@{lg}' for lg in ("de", "fr", "it", "en", "la"))
    q = f"""SELECT DISTINCT ?item ?itemLabel ?hls WHERE {{
      VALUES ?l {{ {vals} }}
      ?item rdfs:label ?l .
      ?item wdt:P17 ?c . VALUES ?c {{ wd:Q39 wd:Q142 wd:Q38 wd:Q183 }}
      ?item wdt:P31/wdt:P279* wd:Q486972 .
      OPTIONAL {{ ?item wdt:P902 ?hls }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,fr,it,en". }} }} LIMIT 5"""
    return sparql(q, cache)


def wd_diocese(seat: str, cache: Path) -> list[dict]:
    """The Catholic diocese whose English label is «(Roman Catholic) (Arch)diocese of <seat>»."""
    lit = seat.replace('"', "")
    labels = [f"Roman Catholic Diocese of {lit}", f"Roman Catholic Archdiocese of {lit}", f"Diocese of {lit}",
              f"Archdiocese of {lit}", f"Ancient Diocese of {lit}"]
    vals = " ".join(f'"{x}"@en' for x in labels)
    q = f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
      VALUES ?l {{ {vals} }}
      ?item rdfs:label ?l .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,fr,en". }} }} LIMIT 5"""
    return sparql(q, cache)


def qid(row) -> str:
    return row["item"]["value"].rsplit("/", 1)[-1]


def years_fit(birth, death) -> bool:
    b = int(str(birth)[:4]) if birth and str(birth)[:4].isdigit() else None
    d = int(str(death)[:4]) if death and str(death)[:4].isdigit() else None
    if b and b > 1449:
        return False
    if d and d < 1435:
        return False
    return bool(b or d)


def load_mentions() -> list[dict]:
    out = []
    for f in sorted(REG.glob("*.json")):
        r = json.loads(f.read_text())
        if r.get("prompt") != "regest_v2" or not r.get("data"):
            continue
        d = r["data"]
        for kind in ("persons", "places", "institutions"):
            for e in d.get(kind) or []:
                if not isinstance(e, dict) or not (e.get("name") or e.get("as_written")):
                    continue
                vals = {k: e.get(k) for k in ("as_written", "name", "role", "office", "institution", "diocese", "modern", "type", "place")}
                vals = {k: (None if isinstance(v, str) and v.strip().lower() in NULLS else v) for k, v in vals.items()}
                if kind == "persons" and TITLE_ONLY.match(ascii_key(vals.get("name") or vals.get("as_written") or "")):
                    continue  # an office without a name («episcopus Montisregalis») is not a person
                out.append({"entry": r["id"], "kind": kind, **vals})
    return out


def cluster(mentions: list[dict]) -> list[dict]:
    clusters: dict[str, dict] = {}
    for m in mentions:
        if m["kind"] == "persons":
            k = name_key(m.get("name") or m["as_written"])
            if not k:
                continue
            if len(k.split()) < 2:  # single names only with a diocese or office to anchor them
                anchor = ascii_key(m.get("diocese") or m.get("office") or "")
                if not anchor:
                    continue
                k = f"{k} | {anchor}"
        elif m["kind"] == "places" and (m.get("type") == "diocese" or re.search(r"ens(is|e|i)$", ascii_key(m.get("name") or ""))):
            seat = diocese_seat(m.get("name") or m["as_written"]) or diocese_seat(m["as_written"])
            if not seat:
                continue
            m["kind"], m["seat"] = "dioceses", seat
            k = seat.lower()
        else:
            k = ascii_key(m.get("name") or m["as_written"])
            if len(k) < 3:
                continue
        ck = f"{m['kind']}::{k}"
        c = clusters.setdefault(ck, {"id": None, "kind": m["kind"], "key": k, "mentions": [], "links": [], "grade": "identical"})
        c["mentions"].append(m)
    # near-identical person names with a shared diocese or office -> merge as very_likely
    persons = [c for c in clusters.values() if c["kind"] == "persons" and " | " not in c["key"]]
    persons.sort(key=lambda c: -len(c["mentions"]))
    merged = set()
    for i, a in enumerate(persons):
        if id(a) in merged:
            continue
        ctx_a = {ascii_key(m.get("diocese") or "") for m in a["mentions"]} | {ascii_key(m.get("office") or "") for m in a["mentions"]}
        ctx_a.discard("")
        for b in persons[i + 1:]:
            if id(b) in merged or a["key"].split()[0] != b["key"].split()[0]:
                continue
            if difflib.SequenceMatcher(None, a["key"], b["key"]).ratio() < 0.92:
                continue
            ctx_b = {ascii_key(m.get("diocese") or "") for m in b["mentions"]} | {ascii_key(m.get("office") or "") for m in b["mentions"]}
            if ctx_a & ctx_b:
                a["mentions"] += b["mentions"]
                a.setdefault("variants", []).append(b["key"])
                a["grade"] = "very_likely"
                merged.add(id(b))
    out = [c for c in clusters.values() if id(c) not in merged]
    for n, c in enumerate(sorted(out, key=lambda c: (c["kind"], c["key"]))):
        c["id"] = f"{c['kind'][:3]}{n:05d}"
    return out


def link_person(c: dict, mcp: MCP) -> list[dict]:
    links = []
    name = c["mentions"][0].get("name") or c["mentions"][0]["as_written"]
    if len(name_key(name).split()) < 2:
        return links
    # SSRQ: exact historical name form, one person, attested around the time
    try:
        rows = mcp.call("ssrq", "search_name_index", query=name, type_filter="person", limit=20) or []
        hits = {}
        for row in rows if isinstance(rows, list) else []:
            if name_key(row.get("name_text") or "") == name_key(name):
                hits[row.get("ssrq_id") or row.get("id")] = row
        if len(hits) == 1:
            pid, row = next(iter(hits.items()))
            p = mcp.call("ssrq", "get_person", pid=pid) if pid else None
            fy = (p or {}).get("first_year") if isinstance(p, dict) else None
            ly = (p or {}).get("last_year") if isinstance(p, dict) else None
            if fy and ly and fy <= 1470 and ly >= 1420:
                links.append({"source": "ssrq", "id": pid, "label": row.get("label") or row.get("name_text"),
                              "grade": "identical", "dates": f"{fy}–{ly}",
                              "url": f"https://www.ssrq-sds-fds.ch/persons-db-edit/?query={pid}"})
    except Exception as e:  # noqa: BLE001
        print("ssrq", name, e, file=sys.stderr)
    # Königsfelden: exact name, one person
    try:
        rows = mcp.call("kf", "search_persons", query=name, limit=20) or []
        hits = [r for r in rows if isinstance(r, dict) and name_key(r.get("name") or r.get("label") or "") == name_key(name)]
        if len(hits) == 1:
            h = hits[0]
            links.append({"source": "kf", "id": h.get("id"), "label": h.get("name") or h.get("label"), "grade": "identical"})
    except Exception as e:  # noqa: BLE001
        print("kf", name, e, file=sys.stderr)
    return links


def link_place(c: dict, mcp: MCP, cache: Path) -> list[dict]:
    links = []
    forms = []
    for m in c["mentions"]:
        for f in (m.get("modern"), m.get("name")):
            if f and f not in forms:
                forms.append(f)
    for f in forms[:3]:
        try:
            rows = mcp.call("kf", "search_places", query=f, limit=10) or []
            hits = [r for r in rows if isinstance(r, dict) and ascii_key(f) in
                    {ascii_key(r.get("name_de") or ""), ascii_key(r.get("name_fr") or "")}]
            if len(hits) == 1:
                h = hits[0]
                links.append({"source": "kf", "id": h["id"], "label": h.get("name_de") or h.get("name_fr"), "grade": "identical"})
                if h.get("hls_id"):
                    hid = str(h["hls_id"]).zfill(6)
                    links.append({"source": "hls", "id": hid, "label": h.get("name_de") or h.get("name_fr"),
                                  "grade": "identical", "url": f"https://hls-dhs-dss.ch/de/articles/{hid}/"})
                break
        except Exception as e:  # noqa: BLE001
            print("kf place", f, e, file=sys.stderr)
    for f in forms[:3]:
        rows = wd_place(f, cache)
        ids = {qid(r) for r in rows}
        if len(ids) == 1:
            r = rows[0]
            links.append({"source": "wikidata", "id": qid(r), "label": r.get("itemLabel", {}).get("value"),
                          "grade": "identical", "url": f"https://www.wikidata.org/wiki/{qid(r)}"})
            if r.get("hls") and not any(l["source"] == "hls" for l in links):
                hid = r["hls"]["value"].zfill(6)
                links.append({"source": "hls", "id": hid, "label": r.get("itemLabel", {}).get("value"),
                              "grade": "identical", "url": f"https://hls-dhs-dss.ch/de/articles/{hid}/"})
            break
    return links


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-external", action="store_true")
    ap.add_argument("--limit", type=int, help="link only the N most frequent clusters per kind (testing)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cache = OUT / "cache"
    mcp = MCP(cache / "mcp")
    mentions = load_mentions()
    clusters = cluster(mentions)
    print(f"{len(mentions)} mentions -> {len(clusters)} clusters", flush=True)
    if not args.no_external:
        by_kind = defaultdict(list)
        for c in clusters:
            by_kind[c["kind"]].append(c)
        for kind, cs in by_kind.items():
            cs.sort(key=lambda c: -len(c["mentions"]))
            for n, c in enumerate(cs[: args.limit] if args.limit else cs, 1):
                if kind == "persons":
                    c["links"] = link_person(c, mcp)
                elif kind == "places":
                    c["links"] = link_place(c, mcp, cache)
                elif kind == "dioceses":
                    rows = wd_diocese(c["mentions"][0]["seat"], cache)
                    ids = {qid(r) for r in rows}
                    if len(ids) == 1:
                        c["links"] = [{"source": "wikidata", "id": qid(rows[0]), "label": rows[0].get("itemLabel", {}).get("value"),
                                       "grade": "identical", "url": f"https://www.wikidata.org/wiki/{qid(rows[0])}"}]
                if n % 50 == 0:
                    print(f"  {kind}: {n}/{len(cs)}", flush=True)
    rep = defaultdict(lambda: defaultdict(int))
    for c in clusters:
        rep[c["kind"]]["clusters"] += 1
        rep[c["kind"]]["mentions"] += len(c["mentions"])
        rep[c["kind"]]["in_several_entries"] += len({m["entry"] for m in c["mentions"]}) > 1
        rep[c["kind"]]["very_likely_merged"] += c["grade"] == "very_likely"
        for s in {l["source"] for l in c["links"]}:
            rep[c["kind"]][f"linked_{s}"] += 1
    (OUT / "entities.json").write_text(json.dumps(clusters, ensure_ascii=False))
    (OUT / "report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
