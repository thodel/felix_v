#!/usr/bin/env python3
"""Combined reading of CITlab (H) and CATMuS Medieval (C), word by word, without a language model.

Both readers read the same Transkribus lines (same order, checked by count). H expands
abbreviations but often substitutes a wrong dictionary word; C is diplomatic (abbreviation
signs, u for v) and closer to the letters, but garbles letters too.

Per line:
  1. Tokens of H and C are aligned on a normalised form (lower case, u/v, i/j, no diacritics).
  2. Where they agree, H's token stands (it is expanded and has H's punctuation).
  3. Where they differ word for word, C's word replaces H's word only if
       - C's word is written out in full (letters only, no abbreviation sign), and
       - it is attested: it occurs at least MIN_FREQ times in the whole H text of the eight
         volumes, and more often than H's word there.
     A group of H words that C reads as a different number of words is replaced only if
     every C word in the group passes the same test and the group is not longer than 3 words.
  4. Words that C has and H lacks are not added; words that H has and C lacks stay.
So the combined reading is H, corrected where C clearly reads a real word that H missed.
Every replaced word is recorded as a character span (src "C").

Lexicon: frequencies of normalised H tokens over all volumes (data/combined/lexicon.json).
Output: data/combined/<docId>_p<NNNN>.json = {"lines": [{"i", "text", "c": [[start, end], …]}], "stats": …}
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
CAT = ROOT / "data/catmus"
OUT = ROOT / "data/combined"
MIN_FREQ = 5
VERSION = "combine_rules_v3"
PLAIN = re.compile(r"^[A-Za-z]+$")


def key(tok: str) -> str:
    s = unicodedata.normalize("NFKD", tok)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("j", "i").replace("v", "u")
    return re.sub(r"[^a-z]", "", s)


def core(tok: str) -> str:
    """The word without surrounding ASCII punctuation. Combining marks (abbreviation signs) stay,
    so that a word like «nõ» is not mistaken for the plain word «no»."""
    return re.sub(r"^[.,;:!?()\[\]/¶'\"]+|[.,;:!?()\[\]/¶'\"]+$", "", tok)


def attested_better(cw: str, hw: str, lex: Counter) -> bool:
    """C's word replaces H's word only if C's is written out in full and attested, and H's word is
    rare in H's own text (a likely misreading) or far rarer than C's."""
    kc, kh = key(cw), key(hw)
    if not PLAIN.match(cw) or len(kc) < 2 or lex[kc] < MIN_FREQ:
        return False
    if len(kc) < 0.75 * len(kh) or (len(kc) < len(kh) and kh.startswith(kc)):
        return False  # C cut the word short (abbreviation stub such as «Geor» for «Georg»)
    if hw[:1].isupper() and lex[kc] < 50:
        return False  # names: only replaced by a very common word (e.g. «Basler» → «Basilee»)
    return lex[kh] < MIN_FREQ or lex[kc] >= 10 * lex[kh]


def build_lexicon() -> Counter:
    lex: Counter = Counter()
    for f in EXP.glob("vol*.json"):
        for p in json.loads(f.read_text())["pages"]:
            for r in p["regions"]:
                for l in r["lines"]:
                    lex.update(k for k in (key(t) for t in l["text"].split()) if len(k) > 1)
    return lex


def combine_line(h: str, c: str, lex: Counter) -> tuple[str, list[list[int]], int]:
    ht, ct = h.split(), c.split()
    if not ht or not ct:
        return h.strip(), [], 0
    hk, ck = [key(t) for t in ht], [key(t) for t in ct]
    out: list[tuple[str, bool]] = []  # (token, from_c)
    sm = difflib.SequenceMatcher(None, hk, ck, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal" or op == "delete":
            out += [(t, False) for t in ht[i1:i2]]
        elif op == "insert":
            continue
        else:  # replace
            hs, cs = ht[i1:i2], ct[j1:j2]
            if len(hs) == len(cs):
                for hw, cw in zip(hs, cs):
                    cwc = core(cw)
                    ok = attested_better(cwc, core(hw), lex)
                    out.append((restyle(hw, cwc), True) if ok else (hw, False))
            else:
                cores = [core(w) for w in cs]
                ok = (len(cs) <= 3 and all(PLAIN.match(w) and len(key(w)) > 1 and lex[key(w)] >= MIN_FREQ for w in cores)
                      and all(lex[key(core(w))] < MIN_FREQ for w in hs))
                if ok:
                    for n, w in enumerate(cores):
                        out.append((restyle(hs[0] if n == 0 else "", w) + (trailing(hs[-1]) if n == len(cores) - 1 else ""), True))
                else:
                    out += [(t, False) for t in hs]
    text, spans, pos = [], [], 0
    for tok, from_c in out:
        if text:
            pos += 1
        if from_c:
            spans.append([pos, pos + len(tok)])
        text.append(tok)
        pos += len(tok)
    return " ".join(text), spans, len(spans)


def trailing(tok: str) -> str:
    m = re.search(r"\W+$", tok)
    return m.group(0) if m else ""


def restyle(hw: str, cw: str) -> str:
    """C's word in H's conventions: H's capitalisation and punctuation, v/j as H would write them."""
    w = cw.lower()
    hc = core(hw)
    if hc[:1].isupper():
        w = w[:1].upper() + w[1:]
    lead = re.match(r"^\W*", hw).group(0) if hw else ""
    return lead + w + (trailing(hw) if hw and len(core(hw)) else "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vols", type=int, nargs="*")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    lex = build_lexicon()
    (OUT / "lexicon.json").write_text(json.dumps(dict(lex.most_common()), ensure_ascii=False))
    total = Counter()
    for f in sorted(EXP.glob("vol*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        vol = json.loads(f.read_text())
        if args.vols and vol["vol"] not in args.vols:
            continue
        st = Counter()
        for p in vol["pages"]:
            cf = CAT / f"{vol['docId']}_p{p['n']:04d}.json"
            if not cf.exists():
                st["no_catmus"] += 1
                continue
            hl = [l["text"].strip() for r in p["regions"] for l in r["lines"]]
            cl = [(l.get("text") or "").strip() for l in json.loads(cf.read_text())["lines"]]
            if len(hl) != len(cl):
                st["line_count_mismatch"] += 1
                continue
            lines = []
            for i, (h, c) in enumerate(zip(hl, cl)):
                if not h:
                    continue
                text, spans, n = combine_line(h, c, lex)
                st["words"] += len(text.split())
                st["from_c"] += n
                lines.append({"i": i, "text": text, "c": spans})
            st["pages"] += 1
            (OUT / f"{vol['docId']}_p{p['n']:04d}.json").write_text(json.dumps(
                {"version": VERSION, "lines": lines}, ensure_ascii=False))
        total += st
        print(f"vol {vol['vol']}: {dict(st)}", flush=True)
    print("total", dict(total), f"share from CATMuS: {total['from_c'] / max(1, total['words']):.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
