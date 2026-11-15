# Bullarium Felix’ V.

Website: **https://thodel.github.io/felix_v/**

Die Register des Gegenpapstes Felix V. (1439–1449, zuvor Herzog Amadeus VIII. von Savoyen,
[HLS](https://hls-dhs-dss.ch/de/articles/012614/2006-04-10/)) in acht Bänden, als Mikrofilmaufnahmen
in Transkribus (Sammlung 53095 «Bollario de Felice», 2'699 Doppelseiten).

**Alles ist maschinell erzeugt und ungeprüft:** der Text ist die HTR-Erstlesung aus Transkribus
(CITlab, «Generic Model Charter Scripts XIII–XV»), Einträge, Daten und Register sind automatische Versuche.
Die Bilder werden von Transkribus (IIIF) geladen und nicht hier gespeichert.

## Aufbau

| Schritt | Skript | Ergebnis |
|---|---|---|
| Export aus Transkribus | `scripts/export_transkribus.py` | `data/raw/` (PageXML), `data/export/` (nicht im Repo) |
| Segmentierung in Einträge | `scripts/segment.py` | `data/export/entries_vol<N>.json` |
| Datum lesen / Entitäten (qwen3.8, GPUStack) | `scripts/llm_entries.py --task date\|ner` | `data/llm/` |
| Lesetest (Seitenhälften) | `scripts/read_vlm.py`, `scripts/compare_readings.py` | `data/readings/` |
| Website-Daten | `scripts/build_site.py` | `docs/data/` |

```bash
uv venv .venv && uv pip install --python .venv/bin/python pillow
.venv/bin/python scripts/export_transkribus.py          # TRANSKRIBUS_USER/PASSWORD aus --env
.venv/bin/python scripts/segment.py
set -a; . ~/.gpustack.env; set +a
.venv/bin/python scripts/llm_entries.py --task date
.venv/bin/python scripts/build_site.py
```

Plan und offene Punkte: [PLAN.md](PLAN.md).
