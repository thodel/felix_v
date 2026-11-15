#!/usr/bin/env python3
"""Segment the register volumes into entries (v1: rule-based, on the Transkribus HTR text).

An entry in the register is a copied papal letter that ends with a dating clause
("Dat(um) Basilee, quinto idus januarii, anno a nativitate domini millesimo
quadringentesimo quadragesimo secundo, pontificatus nostri anno secundo"),
usually followed by the registration note (number, "por", scribe's name).

v1 cuts after every dating clause. The clause is the anchor because the HTR
reads it reliably; the incipit "Felix episcopus …" often loses its large initial.

Writes data/export/entries_vol<N>.json:
  {id, vol, start:{page,line}, end:{page,line}, pages:[…], text, clause,
   date:{…rule-based…}, marg:[…]}
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "data/export"

ANCHOR = re.compile(r"(?:^|[\s.,;])(?:dat(?:um|u|\.)?|basil\w*|basl\w*|pasil\w*|tasil\w*|lausan\w*|gebenn\w*|thonon\w*|ripail\w*)\b", re.I | re.U)
YEARWORD = re.compile(r"nativ|natiu|millesim|milles|incarnac|quadringent|quadrag", re.I)
CLAUSE_HINT = re.compile(r"anno|millesim|nativi|pontific|incarnac|kal|non|id(?:us|ib|um)\b", re.I)
SUPRA = re.compile(r"\bDat(?:um)?\.?\s+ut\s+sup", re.I)
INCIPIT = re.compile(r"^\W*(?:F|E)?[eE]?lix\w*\s+(?:e|ep|episc|cler)|^\W*Clix", re.U)
CONTINUES = re.compile(r"^\W*(?:nostri|nri|nr̄i|anno|ano|pontific|ponti|potific|tificat|ficat|millesim|milli|quadr|nativ|natiu|domini|dni|di\b|"
                       r"primo|pmo|p̄mo|secundo|tercio|tertio|quarto|quinto|sexto|septimo|octavo|nono|decimo|suscept|a nobis|nobis|apostolat|officii|kl|kal|non|id|"
                       r"ianu|janu|febr|marc|apri|mai|iun|jun|iul|jul|aug|sept|octo|nove|dece)|millesim|quadrag|pontific|nativit|apostolat", re.I | re.U)
REGNOTE = re.compile(r"✳|\b[xvl]{2,}\b|\bp[oō]r\b|ep[̄]?[uū]s|epus|ep̄us|\bJo\b", re.I | re.U)

MONTHS = {
    "jan": 1, "ian": 1, "feb": 2, "mar": 3, "apr": 4, "aprel": 4, "mai": 5, "may": 5, "jun": 6, "iun": 6,
    "jul": 7, "iul": 7, "aug": 8, "sep": 9, "oct": 10, "okt": 10, "nov": 11, "dec": 12, "dez": 12,
}
ORD = {"primo": 1, "secundo": 2, "tercio": 3, "tertio": 3, "quarto": 4, "quinto": 5, "sexto": 6, "septimo": 7,
       "octavo": 8, "nono": 9, "decimo": 10, "undecimo": 11, "duodecimo": 12, "tredecimo": 13, "decimotercio": 13,
       "quartodecimo": 14, "quintodecimo": 15, "sextodecimo": 16, "septimodecimo": 17, "decimooctavo": 18,
       "decimonono": 19, "pridie": 2}
YEARS = {"nono": 1439, "quadragesimo": 1440, "quadragesimoprimo": 1441, "quadragesimosecundo": 1442,
         "quadragesimotercio": 1443, "quadragesimotertio": 1443, "quadragesimoquarto": 1444,
         "quadragesimoquinto": 1445, "quadragesimosexto": 1446, "quadragesimoseptimo": 1447,
         "quadragesimooctavo": 1448, "quadragesimonono": 1449}
PONT = {"primo": 1, "secundo": 2, "tercio": 3, "tertio": 3, "quarto": 4, "quinto": 5, "sexto": 6, "septimo": 7,
        "octavo": 8, "nono": 9, "decimo": 10}
CORONATION = date(1440, 7, 24)  # pontificate years run from the coronation
ELECTION = date(1439, 11, 5)
ABDICATION = date(1449, 4, 7)


def norm(s: str) -> str:
    s = s.lower().replace("ꝰ", "us").replace("ꝫ", "et").replace("ā", "a").replace("ē", "e").replace("ī", "i")
    s = s.replace("j", "i").replace("v", "u").replace("c", "c")
    return re.sub(r"[^a-z ]", " ", s)


def fuzzy_pick(tok: str, table: dict, cutoff: float = 0.75):
    from difflib import get_close_matches
    m = get_close_matches(tok, list(table), n=1, cutoff=cutoff)
    return table[m[0]] if m else None


def parse_clause(clause: str) -> dict:
    """Rule-based reading of a dating clause; every field may be None. Readings are a first pass."""
    t = norm(clause)
    toks = t.split()
    out: dict = {"place": None, "month": None, "reckoning": None, "day_ord": None, "year": None, "pont": None}
    m = re.search(r"dat(?:um)?\s+([a-z]+)", t)
    if m and m.group(1) not in {"ut", "anno"}:
        out["place"] = m.group(1)
    for i, tk in enumerate(toks):
        if out["reckoning"] is None:
            if tk.startswith("kal") or tk.startswith("cal"):
                out["reckoning"] = "kal"
            elif tk.startswith("non"):
                out["reckoning"] = "non"
            elif re.match(r"id(us|ibus|um)?$", tk):
                out["reckoning"] = "id"
        if out["month"] is None:
            for k, v in MONTHS.items():
                if tk.startswith(k) and len(tk) >= 4 and not tk.startswith("nonas"):
                    out["month"] = v
                    break
        if out["day_ord"] is None and i < 12:
            o = fuzzy_pick(tk, ORD, 0.8)
            if o:
                out["day_ord"] = o
    joined = "".join(toks)
    m = re.search(r"quadr\w{0,12}?gesim(o\w{0,16})", joined)
    if m:
        tail = "quadragesim" + m.group(1)
        best = fuzzy_pick(tail[:22], YEARS, 0.7)
        out["year"] = best
    m = re.search(r"pontific\w*\s+\w+\s+anno\s+(\w+)", t) or re.search(r"anno\s+(\w+)\s*$", t)
    if m:
        out["pont"] = fuzzy_pick(m.group(1), PONT, 0.7)
    out["iso"] = to_iso(out)
    out["check"] = check(out)
    return out


def days_in(month: int, year: int) -> int:
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    return (nxt - timedelta(days=1)).day


def to_iso(d: dict) -> str | None:
    """Roman calendar to ISO. Kalends count back into the previous month. Nativity style: 25–31 Dec
    of 'year' belong to the calendar year before."""
    y, m = d.get("year"), d.get("month")
    if not (y and m):
        return None
    big = m in (3, 5, 7, 10)
    nones, ides = (7, 15) if big else (5, 13)
    n = d.get("day_ord")
    r = d.get("reckoning")
    try:
        if r is None and n:
            return None  # ordinal without reckoning: cannot place it
        if r == "non":
            day = date(y, m, nones) - timedelta(days=(n or 1) - 1)
        elif r == "id":
            day = date(y, m, ides) - timedelta(days=(n or 1) - 1)
        elif r == "kal":
            if not n or n == 1:
                day = date(y, m, 1)
            else:
                # the day lies in the previous month; for January that is December of the
                # written year (nativity style: the year current at the date), corrected below
                pm, py = (m - 1, y) if m > 1 else (12, y)
                day = date(py, pm, days_in(pm, py) + 2 - n)
        else:
            return f"{y}-{m:02d}"
    except ValueError:
        return None
    if day.month == 12 and day.day >= 25:
        day = day.replace(year=day.year - 1)
    return day.isoformat()


def check(d: dict) -> str | None:
    """Pontificate year vs. ISO date: ok, mismatch, or None when one is missing."""
    iso, p = d.get("iso"), d.get("pont")
    if iso and len(iso) == 10 and not (ELECTION <= date.fromisoformat(iso) <= ABDICATION):
        return "range"
    if not iso or not p or len(iso) < 10:
        return None
    day = date.fromisoformat(iso)
    if not (ELECTION <= day <= ABDICATION):
        return "range"  # outside the pontificate: certainly a misreading
    # year 1 runs from the election (5.11.1439, counted "a die suscepti apostolatus officii")
    # to the first anniversary of the coronation; later years from coronation to coronation
    start = ELECTION if p == 1 else CORONATION.replace(year=CORONATION.year + p - 1)
    end = CORONATION.replace(year=CORONATION.year + p)
    return "ok" if start <= day < end else "mismatch"


def linear(vol: dict):
    """(page, line_index_on_page, region_kind, text) in reading order."""
    for p in vol["pages"]:
        k = 0
        for r in p["regions"]:
            lines = [l for l in r["lines"] if l["text"].strip()]
            avg = sum(len(l["text"]) for l in lines) / max(1, len(lines))
            kind = "marg" if len(lines) <= 4 and avg < 28 else "main"
            for l in lines:
                yield p["n"], k, kind, l["text"].strip(), l["id"]
                k += 1


def segment(vol: dict) -> list[dict]:
    rows = list(linear(vol))
    entries, cur, marg = [], [], []
    i = 0
    while i < len(rows):
        page, k, kind, text, lid = rows[i]
        if kind == "marg":
            marg.append({"page": page, "text": text})
            i += 1
            continue
        if INCIPIT.search(text) and len([r for r in cur if r[2] == "main"]) >= 8:
            # a new letter starts although no dating clause closed the previous one
            entries.append(make_entry(vol["vol"], len(entries) + 1, cur, None, marg, None, split="incipit"))
            cur, marg = [], []
        cur.append(rows[i])
        am = ANCHOR.search(" " + text)
        if am or SUPRA.search(text):
            after = (" " + text)[am.start():] if am else text
            window = " ".join([after] + [r[3] for r in rows[i + 1:i + 3] if r[2] == "main"])
            if YEARWORD.search(window) or SUPRA.search(text):
                # take the rest of the clause: up to 3 more main lines while they look like it
                start_at = max(0, am.start() - 1) if am else text.find("Dat")
                clause_lines = [text[start_at:] if start_at >= 0 else text]
                j = i + 1
                reg_note = []
                # the clause continues while lines look like its year / pontificate part
                while j < len(rows) and len(clause_lines) < 5:
                    if rows[j][2] != "main":
                        marg.append({"page": rows[j][0], "text": rows[j][3]})
                        j += 1
                        continue
                    t = rows[j][3]
                    if INCIPIT.search(t):
                        break
                    short_so_far = len(" ".join(clause_lines)) < 60  # «Datum» / «Dat Basilee» at the line end
                    if not CONTINUES.search(t) and not short_so_far:
                        # one short junk line may sit inside the clause if the next line continues it
                        nxt = next((r for r in rows[j + 1:j + 3] if r[2] == "main"), None)
                        if not (len(t) <= 6 and nxt and CONTINUES.search(nxt[3])):
                            break
                    clause_lines.append(t)
                    cur.append(rows[j])
                    j += 1
                # then the registration note: short lines with tally numerals, «por», «ep̄us» + a name
                while j < len(rows) and len(reg_note) < 2:
                    if rows[j][2] != "main":
                        marg.append({"page": rows[j][0], "text": rows[j][3]})
                        j += 1
                        continue
                    t = rows[j][3]
                    if len(t) > 45 or INCIPIT.search(t) or not REGNOTE.search(t):
                        break
                    reg_note.append(t)
                    cur.append(rows[j])
                    j += 1
                clause = " ".join(clause_lines)
                entries.append(make_entry(vol["vol"], len(entries) + 1, cur, clause, marg, " ".join(reg_note) or None))
                cur, marg = [], []
                i = j
                continue
        i += 1
    if cur:
        entries.append(make_entry(vol["vol"], len(entries) + 1, cur, None, marg))
    # "Datum ut supra" inherits the preceding date
    prev = None
    for e in entries:
        if e["clause"] and SUPRA.search(e["clause"]) and prev:
            e["date"] = {**prev, "inherited": True}
        if e["date"].get("iso"):
            prev = {k: v for k, v in e["date"].items() if k != "inherited"}
    return entries


def make_entry(vol: int, n: int, rows, clause, marg, reg_note=None, split="clause") -> dict:
    return {
        "id": f"v{vol}-{n:04d}", "vol": vol,
        "start": {"page": rows[0][0], "line": rows[0][1]}, "end": {"page": rows[-1][0], "line": rows[-1][1]},
        "pages": sorted({r[0] for r in rows}), "lines": len(rows),
        "text": "\n".join(r[3] for r in rows), "clause": clause,
        "date": parse_clause(clause) if clause else {}, "marg": list(marg), "reg": reg_note, "split": split if clause is None else "clause",
    }


def main() -> int:
    stats = []
    for f in sorted(SITE.glob("vol*.json")):
        vol = json.loads(f.read_text())
        ents = segment(vol)
        (SITE / f"entries_vol{vol['vol']}.json").write_text(json.dumps(ents, ensure_ascii=False, separators=(",", ":")))
        n = len(ents)
        iso = sum(1 for e in ents if e["date"].get("iso") and len(e["date"]["iso"]) == 10)
        ym = sum(1 for e in ents if e["date"].get("iso"))
        ok = sum(1 for e in ents if e["date"].get("check") == "ok")
        mis = sum(1 for e in ents if e["date"].get("check") == "mismatch")
        years = sorted(e["date"]["year"] for e in ents if e["date"].get("year"))
        span = f"{years[len(years)//20]}–{years[-1 - len(years)//20]}" if years else "–"
        stats.append({"vol": vol["vol"], "entries": n, "day": iso, "month": ym, "pont_ok": ok, "pont_mismatch": mis, "years_p5_p95": span})
        print(stats[-1])
    (ROOT / "data/segment_stats_v1.json").write_text(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
