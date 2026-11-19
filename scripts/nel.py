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
  persons  wd-pre1500.resolve_name (offline Wikidata snapshot, died 1439–1500, unique exact match) →
           GND, HLS, VIAF from the Wikidata item; ssrq.search_name_index and kf.search_persons by exact name form
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
from collections import Counter, defaultdict
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


PLACE_FILLERS = {"civitate", "ciuitate", "ciuitas", "civitas", "apud", "in", "de", "dioc", "diocesis", "diocesi", "urbe"}
NOT_SEAT = ("basilic", "spirit", "spiritu")  # «basilica», «Sancti Spiritus» start like Basel and Speyer


def written_seat(as_written: str) -> str | None:
    """The seat a written place form names on its own, word by word; G misread as B or T (Bebenn…, Tebenn…)
    still counts as Geneva."""
    for w in ascii_key(as_written).split():
        if len(w) < 5 or w.startswith(NOT_SEAT):
            continue
        if re.match(r"^[gbtc]ebenn", w):
            return "Geneva"
        seat = diocese_seat(w)
        if seat:
            return seat
    return None


def correct_place(m: dict) -> None:
    """The model sometimes normalises a written form to another place: «Gebennen», «civitate Gebennium» came back
    as name «Basileae», modern «Basel» (39 mentions, 19.11.2026; Basel stands in almost every dating clause).
    Where the written form clearly names one seat and the normalised fields another, the written form wins."""
    ws = written_seat(m["as_written"] or "")
    if not ws:
        return
    name_seat = written_seat(m.get("name") or "")
    modern_seat = diocese_seat(m.get("modern") or "") or (m.get("modern") if m.get("modern") in DIOCESES.values() else None)
    if name_seat == ws:  # the name is right, only the modern field points elsewhere: fix that alone
        if modern_seat and modern_seat != ws:
            m["corrected_from"] = [m.get("name"), m.get("modern")]
            m["modern"] = ws
            m["modern_only"] = True
        return
    if (name_seat and name_seat != ws) or (not name_seat and modern_seat and modern_seat != ws):
        m["corrected_from"] = [m.get("name"), m.get("modern")]
        m["name"], m["modern"] = None, ws


def cluster(mentions: list[dict]) -> list[dict]:
    clusters: dict[str, dict] = {}
    for m in mentions:
        if m["kind"] == "places":
            correct_place(m)
    # for corrected city mentions: the usual Latin key of that seat among the uncorrected ones
    usual: dict = defaultdict(Counter)      # seat -> usual key of the city itself (no adjective)
    seatword: dict = defaultdict(Counter)   # seat -> usual word for it inside compound names (… extra muros Gebennae)
    for m in mentions:
        if m["kind"] == "places" and m.get("name") and not m.get("corrected_from"):
            seat = written_seat(m["as_written"] or "")
            k = ascii_key(m["name"])
            if seat and seat == written_seat(k):
                if len(k.split()) == 1 and not re.search(r"ens(is|e|i)$", k):
                    usual[seat][k] += 1
                for w in k.split()[1:]:
                    if written_seat(w) == seat:
                        seatword[seat][w] += 1
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
            seat = (m.get("modern") if m.get("corrected_from") else None) or diocese_seat(m.get("name") or m["as_written"]) or diocese_seat(m["as_written"])
            if not seat:
                continue
            m["kind"], m["seat"] = "dioceses", seat
            k = seat.lower()
        else:
            rest = [w for w in ascii_key(m["as_written"] or "").split() if w not in PLACE_FILLERS and not written_seat(w)]
            if m.get("corrected_from") and not m.get("modern_only") and rest:  # a convent, a church … outside the city
                old_name = ascii_key((m["corrected_from"][0] or ""))
                sw = seatword[m["modern"]].most_common(1)[0][0] if seatword.get(m["modern"]) else None
                if len(old_name.split()) > 1 and sw:
                    k = " ".join(sw if written_seat(w) else w for w in old_name.split())
                else:
                    k = " ".join(w for w in ascii_key(m["as_written"]).split() if w not in ("apud",))
            elif m.get("corrected_from") and not m.get("modern_only") and usual.get(m["modern"]):
                k = usual[m["modern"]].most_common(1)[0][0]  # the city itself: its usual Latin key
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


# Persons named by office, not by full name, whom the office identifies in 1439–1449. Checked in the
# wd-pre1500 snapshot (19.11.2026); graded «very likely», since the identification rests on the office.
OFFICE_HOLDERS = [
    # (first name key prefix, office contains, place/diocese/institution contains (any of), QID, label, note)
    ("ludouic", "dux", ("", "sabaud", "saband", "savoy"), "Q451408", "Louis I, Duke of Savoy", "dux Sabaudie 1440–1465"),
    ("ludouic", "cardinal", ("arelat",), "Q2711764", "Louis Aleman", "cardinalis Arelatensis 1426–1450"),
]
ROMAN_ORD = re.compile(r"\b(?:PP\.?\s*|papa\s+)?([IVX]+)\b")


def by_office(c: dict, mcp: MCP) -> list[dict]:
    ms = c["mentions"]
    first = name_key(ms[0].get("name") or ms[0]["as_written"]).split()
    first = first[0] if first else ""
    offices = " ".join((m.get("office") or "") for m in ms).lower()
    where = " ".join(" ".join(filter(None, (m.get("institution"), m.get("diocese")))) for m in ms).lower()
    for pre, off, places, q, label, note in OFFICE_HOLDERS:
        if first.startswith(pre) and off in offices and any(x in where for x in places if x) | ("" in places and not where.strip()):
            return [{"source": "wikidata", "id": q, "label": label, "grade": "very_likely",
                     "url": f"https://www.wikidata.org/wiki/{q}", "desc": f"{t_by_office} {note}"}]
    # earlier popes cited in the letters: name + ordinal, unique in the snapshot, described as pope
    if "papa" in offices or "pp" in offices:
        for m in ms:
            raw = m.get("name") or m["as_written"]
            o = ROMAN_ORD.search(raw)
            if not o or not first:
                continue
            base = {"ioann": "Iohannes", "iohann": "Iohannes", "johann": "Iohannes", "bonifa": "Bonifacius",
                    "martin": "Martinus", "eugen": "Eugenius", "clemen": "Clemens", "gregor": "Gregorius",
                    "urban": "Urbanus", "innocen": "Innocentius", "benedic": "Benedictus", "nicola": "Nicolaus"}
            nm = next((v for k, v in base.items() if first.startswith(k.replace("j", "i"))), None)
            if not nm:
                continue
            r = mcp.call("wd-pre1500", "resolve_name", name=f"{nm} {o.group(1)}", century=0, limit=3)
            if isinstance(r, dict) and r.get("status") == "match" and r.get("candidates"):
                cand = r["candidates"][0]
                if cand.get("score", 0) >= 0.85 and "pope" in (cand.get("description") or "").lower():
                    return [{"source": "wikidata", "id": cand["qid"], "label": cand.get("label"), "grade": "identical",
                             "url": f"https://www.wikidata.org/wiki/{cand['qid']}", "desc": cand.get("description"),
                             "dates": f"{cand.get('birth_year') or '?'}–{cand.get('death_year')}"}]
    return []


t_by_office = "identified by office:"


def link_person(c: dict, mcp: MCP) -> list[dict]:
    links = by_office(c, mcp)
    if links:
        return links
    name = c["mentions"][0].get("name") or c["mentions"][0]["as_written"]
    if len(name_key(name).split()) < 2:
        return links
    # Wikidata via the offline snapshot of persons who died before 1500: only a unique match on the
    # exact name (status «match», score >= 0.9), died in the 15th century and alive in 1439, and only for
    # a person attested in two entries or more without a regnal number: a single mention is too often a
    # misreading («Lumnto Xi g Epus» became «Ludovicus XI») or a namesake (19.11.2026)
    several = len({m["entry"] for m in c["mentions"]}) >= 2
    try:
        if not several or ROMAN_ORD.search(name):
            raise LookupError("single entry or regnal number")
        r = mcp.call("wd-pre1500", "resolve_name", name=name, century=15, limit=3)
        if isinstance(r, dict) and r.get("status") == "match" and r.get("candidates"):
            cand = r["candidates"][0]
            dy, by = cand.get("death_year"), cand.get("birth_year")
            if cand.get("score", 0) >= 0.9 and dy and dy >= 1439 and (not by or by <= 1430):
                grade = "identical" if cand.get("score", 0) >= 1.0 else "very_likely"
                links.append({"source": "wikidata", "id": cand["qid"], "label": cand.get("label"), "grade": grade,
                              "url": f"https://www.wikidata.org/wiki/{cand['qid']}",
                              "dates": f"{by or '?'}–{dy}", "desc": cand.get("description")})
    except LookupError:
        pass
    except Exception as e:  # noqa: BLE001
        print("wd-pre1500", name, e, file=sys.stderr)
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
    compound = len(c["key"].split()) > 1  # a convent, a church … : its modern field names the city, not the place
    for m in c["mentions"]:
        for f in ((m.get("name"),) if compound else (m.get("modern"), m.get("name"))):
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


def merge_by_qid(clusters: list[dict]) -> list[dict]:
    """Person or place clusters linked to the same Wikidata item are one person or place: merge them (largest first)."""
    first: dict = {}
    out = []
    for c in sorted(clusters, key=lambda c: -len(c["mentions"])):
        city = c["kind"] == "places" and len(c["key"].split()) == 1  # only a city itself, never a convent in it
        q = next((f"{c['kind']}:{l['id']}" for l in c["links"] if l["source"] == "wikidata"), None) if c["kind"] == "persons" or city else None
        if q and q in first and city:
            a = first[q]
            initials = {a["key"][:1]} | {ascii_key(l.get("label") or "")[:1] for l in a["links"]}
            if c["key"][:1] not in initials:
                # the written form has nothing of the city («dolodro», «intramontibus» → Lausanne): the link came
                # from the model's modern field alone, so it is dropped and the form stays on its own
                c["links"] = []
                out.append(c)
                continue
        if q and q in first:
            a = first[q]
            a["mentions"] += c["mentions"]
            a.setdefault("variants", []).append(c["key"])
            a["links"] += [l for l in c["links"] if (l["source"], l["id"]) not in {(x["source"], x["id"]) for x in a["links"]}]
            a["grade"] = "very_likely"
            continue
        if q:
            first[q] = c
        out.append(c)
    return sorted(out, key=lambda c: c["id"])


def seat_point(seat: str | None, cache: Path) -> list | None:
    """Coordinates of a bishop's seat (a settlement with exactly this label in de/en/fr/it)."""
    if not seat:
        return None
    lit = seat.replace('"', "")
    vals = " ".join(f'"{lit}"@{lg}' for lg in ("de", "en", "fr", "it"))
    rows = sparql(f"""SELECT DISTINCT ?item ?coord WHERE {{ VALUES ?l {{ {vals} }} ?item rdfs:label ?l .
      ?item wdt:P31/wdt:P279* wd:Q486972 . ?item wdt:P625 ?coord . ?item wdt:P17 ?c .
      VALUES ?c {{ wd:Q39 wd:Q142 wd:Q38 wd:Q183 wd:Q40 }} }} LIMIT 5""", cache)
    if len({qid(r) for r in rows}) != 1:
        return None
    m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", rows[0]["coord"]["value"])
    return [round(float(m.group(2)), 5), round(float(m.group(1)), 5)] if m else None


def authorities(clusters: list[dict], cache: Path) -> None:
    """For every Wikidata link: GND (P227), HLS (P902), VIAF (P214) as further links, and coordinates
    (P625, for a diocese the coordinates of its seat P159/P36) for the map."""
    qids = sorted({l["id"] for c in clusters for l in c["links"] if l["source"] == "wikidata"})
    facts: dict = {}
    for i in range(0, len(qids), 80):
        vals = " ".join(f"wd:{q}" for q in qids[i:i + 80])
        rows = sparql(f"""SELECT ?item ?gnd ?hls ?viaf ?coord ?scoord WHERE {{
          VALUES ?item {{ {vals} }}
          OPTIONAL {{ ?item wdt:P227 ?gnd }} OPTIONAL {{ ?item wdt:P902 ?hls }} OPTIONAL {{ ?item wdt:P214 ?viaf }}
          OPTIONAL {{ ?item wdt:P625 ?coord }} OPTIONAL {{ ?item wdt:P159|wdt:P36 ?seat . ?seat wdt:P625 ?scoord }} }}""", cache)
        for r in rows:
            f = facts.setdefault(qid(r), {})
            for k in ("gnd", "hls", "viaf", "coord", "scoord"):
                if k in r and k not in f:
                    f[k] = r[k]["value"]
    def point(wkt):
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", wkt or "")
        return [round(float(m.group(2)), 5), round(float(m.group(1)), 5)] if m else None
    for c in clusters:
        for l in [l for l in c["links"] if l["source"] == "wikidata"]:
            f = facts.get(l["id"], {})
            have = {x["source"] for x in c["links"]}
            if f.get("gnd") and "gnd" not in have:
                c["links"].append({"source": "gnd", "id": f["gnd"], "label": l.get("label"), "grade": l["grade"],
                                   "url": f"https://d-nb.info/gnd/{f['gnd']}"})
            if f.get("hls") and "hls" not in have:
                hid = f["hls"].zfill(6)
                c["links"].append({"source": "hls", "id": hid, "label": l.get("label"), "grade": l["grade"],
                                   "url": f"https://hls-dhs-dss.ch/de/articles/{hid}/"})
            if f.get("viaf") and "viaf" not in have:
                c["links"].append({"source": "viaf", "id": f["viaf"], "label": l.get("label"), "grade": l["grade"],
                                   "url": f"https://viaf.org/viaf/{f['viaf']}"})
            if c["kind"] == "dioceses" and "coord" not in c:  # the medieval seat, not today's (Basel → Solothurn)
                pt = seat_point(c["mentions"][0].get("seat"), cache)
                if pt:
                    c["coord"] = pt
            if c["kind"] in ("places", "dioceses") and "coord" not in c:
                pt = point(f.get("coord")) or point(f.get("scoord"))
                if pt:
                    c["coord"] = pt


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
    if not args.no_external:
        clusters = merge_by_qid(clusters)
        authorities(clusters, cache)
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
