"""Restore the lost initial of «Felix episcopus …» at the start of a line.

The large initial F of every letter is usually outside the recognised line, so the readings start
with «elix», «Nelix», «Relix», «elx», «Clix», «elie» … followed by «episcopus / eps / ep̄us». Measured
on all readings 17.11.2026: about 2,000 such line starts.

Rule (strict, so ordinary lines like «in eisdem», «ab eis», «nostro epio», «eidem episcopo» or the
registration note «G epus Dibelden» stay untouched):
  first word: letters only at most 6, ending like Felix (…lix, …lx, …lie, …lio, …lip, …lis, …lre,
              …lii, …luo, …eux, optionally a trailing o), not a Latin function word
  second word: begins with «ep» (episcopus, eps, ep̄us, epo, eptis …), or is «eis / clercus /
              clerius» followed by «etc» (ꝫc, ec)
Then the first word becomes «Felix».
"""
from __future__ import annotations

import re
import unicodedata

FIRST = re.compile(r"^(?:[a-z]{0,3}l[iy]?x|[a-z]{0,2}lx|[a-z]{0,3}li[eoips]|[a-z]{0,2}lre|[a-z]{0,2}lii|[a-z]{0,2}luo|[a-z]?eux)o?$")
WEAK = re.compile(r"^[a-z]{0,2}[eo]l(?:e|o|ir|us|rx)?$")
STOP = {"illis", "aliis", "alio", "alie", "filie", "filio", "filii", "filiis", "tali", "talis", "illi", "ille", "nobilis", "felis"}


def _key(tok: str) -> str:
    s = unicodedata.normalize("NFKD", tok)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z]", "", s)


def fix_incipit(text: str) -> tuple[str, int]:
    """Return (text, delta): the line with «Felix» restored, and the change in length of the first
    word (0 if nothing changed), so that character spans after it can be shifted."""
    m = re.match(r"^(\W*)(\S+)(\s+)(\S+)(?:\s+(\S+))?", text or "")
    if not m:
        return text, 0
    lead, w1, sp, w2, w3 = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5) or ""
    k1, k2, k3 = _key(w1), _key(w2), _key(w3)
    if not k1 or len(k1) > 6 or k1 in STOP:
        return text, 0
    if k1 == "felix":
        if w1[0].isupper():
            return text, 0
    elif not FIRST.match(k1):
        # rarer damaged forms (ele, elo, el, elir, olir, elus, Jelrx, Jelir) only before «episc…» or «… etc.»,
        # so that «vel ep…» stays «vel»
        if not (WEAK.match(k1) and (k2.startswith("episc") or k3 in {"etc", "c", "ec"})):
            return text, 0
    etc = k3 in {"etc", "c", "ec", "et"}
    second_ok = k2.startswith("ep") or (k2 in {"eis", "clercus", "clerius", "clericus"} and etc)
    if not second_ok:
        return text, 0
    new = "Felix"
    out = lead + new + text[len(lead) + len(w1):]
    return out, len(new) - len(w1)


def fix_line(text: str, spans: list) -> tuple[str, list, bool]:
    """fix_incipit plus span bookkeeping: spans inside the replaced first word are dropped, later ones shifted."""
    new, delta = fix_incipit(text)
    if new == text:
        return text, spans, False
    first_end_old = len(text) - len(text.lstrip()) + (len(text.lstrip().split()[0]) if text.strip() else 0)
    out = []
    for a, b in spans or []:
        if b <= first_end_old:
            continue
        out.append([a + delta, b + delta])
    return new, out, True
