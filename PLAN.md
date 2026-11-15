# Bullarium Felix’ V. – Plan

Stand 15.11.2026. Quelle: Transkribus-Sammlung 53095 «Bollario de Felice», 8 Dokumente (Bände 1–8),
2'699 Aufnahmen. Jede Aufnahme ist eine Mikrofilm-Doppelseite. Text: CITlab-HTR «Generic Model Charter
Scripts XIII–XV» (in Band 1 teils mit Wörterbuch), Status IN_PROGRESS, nirgends korrigiert. Es gibt also
**keine Ground Truth**.

## 1. Website (thodel.github.io/felix_v)

- Bandübersicht, Viewer (Bild aus Transkribus, Zeilen-Overlay), Eintragsliste, Register (Test), Methode.
- Bilder werden nicht kopiert, sondern von `files.transkribus.eu` geladen (Bildschlüssel aus dem Export).
- Text überall als «automatische Erstlesung» markiert.
- Aufbau: `scripts/export_transkribus.py` → `data/export/` → `scripts/segment.py` → `scripts/llm_entries.py`
  → `scripts/build_site.py` → `docs/data/`.

## 2. Lesetest (welches Modell liest besser?)

Stichprobe: 16 Doppelseiten (2 je Band, Seed 1440) = 32 Seitenhälften, an der Textblock-Grenze aus dem
PageXML zugeschnitten (`data/readings/sample.json`, Zuschnitte auf tei unter `datasets:felix-v-sample/pages`).

| Leser | wann | Stand |
|---|---|---|
| CITlab HTR (Transkribus) | vorhanden | Referenz für «Abweichung» |
| qwen3.8-27b (GPUStack) | 15.11. | läuft, siehe `methode.html` |
| gemini-3.8-flash («Gemini Fast») | Woche ab 23.11. | vorbereitet (tei, PR thodel/agentic_historian#877) |
| gemini-4-argon | Woche ab 23.11. | vorbereitet (dto.) |

Ohne Ground Truth misst der Vergleich nur **Abweichung** von CITlab, Abbrüche (Token-Grenze) und
Wiederholungsschleifen. Für ein Urteil «besser» braucht es korrigierte Seiten:
**Vorschlag:** 8 der 32 Hälften (1 je Band) in Transkribus korrigieren und als GT speichern
(≈ 8 × 35 Zeilen). `compare_readings.py` bewertet dann automatisch gegen `data/readings/gt/<stem>.txt`.

## 3. Entitäten → Register (qwen3.8, Text)

Test auf 40 zufälligen Einträgen (`llm_entries.py --task ner --sample 40`): Personen (mit Rolle, Amt,
Diözese), Orte, Institutionen, Daten, ein Satz Zusammenfassung. Ergebnis und Fehlerbilder: `methode.html`.

Nächste Schritte, falls weiterverfolgt:
1. Registriervermerke («ep̄us Brosseran», «Jo. Benenati») als **Schreiber** getrennt erfassen; sie sind
   keine Personen der Urkunde (v1 verwechselt sie).
2. Normalisierung nicht dem Modell überlassen: Orte/Diözesen gegen eine Liste der Diözesen (lateinische
   Adjektive: Gebennensis, Lausanensis, Lugdunensis …), Personen nach Abgleich mit SSRQ/HLS/Human Lineage.
3. Erst nach besserer Lesung (Gemini/Argon, falls besser) im ganzen Bestand laufen lassen.

## 4. Segmentierung nach Datum und Eintrag

**v1 (umgesetzt, regelbasiert):** Ein Eintrag endet mit der Datumszeile. Anker: «Dat(um)» oder ein
Ausstellungsort (Basil-, Lausan-, Gebenn-, Thonon-, Ripaill-), gefolgt innert 3 Zeilen von «nativitate /
millesimo». Danach werden die Fortsetzungszeilen der Datierung und der Registriervermerk angehängt.
Zweites Signal: ein Incipit («Felix episcopus …») ohne vorherige Datumszeile trennt ebenfalls.
Ergebnis: 2'848 Einträge; ≈ 8 % noch über 150 Zeilen (verpasste Datumszeilen).

**Datierung v1 (umgesetzt):** qwen3.8 liest jede Datumszeile in Felder (Ort, Ordinalzahl, Kalenden/
Nonen/Iden, Monat, Jahr, Pontifikatsjahr). Das Tagesdatum rechnet der Code: römische Zählung,
Weihnachtsstil (25.–31.12. gehören zum Vorjahr), Pontifikatsjahre ab der Krönung am 24.7.1440
(gestützt auf die Stichprobe: Okt. 1440 = 1, Nov. 1441 = 2, März 1447 = 7, Okt. 1448 = 9).
Prüfung: passt das Pontifikatsjahr zum Datum → «✓», sonst «⚠ prüfen». «Datum ut supra» übernimmt das
vorangehende Datum.

**v2 (geplant):**
1. Seitenweise Grenzerkennung: das Modell bekommt die nummerierten Zeilen einer Doppelseite und nennt
   die Zeilen, mit denen ein Brief beginnt bzw. die eine Datierung enthalten. Abgleich mit v1; nur
   Abweichungen gehen in die Prüfliste.
2. Chronologische Plausibilität: Register sind weitgehend chronologisch; ein Datum, das von seinen
   Nachbarn um > 1 Jahr abweicht, wird markiert, ein fehlendes aus den Nachbarn eingegrenzt.
3. Sobald eine bessere Lesung vorliegt, Segmentierung auf ihr wiederholen (IDs bleiben über
   `input`-Prüfung in `data/llm/` stabil, nur Geändertes wird neu gelesen).
4. Export je Eintrag (TEI mit Datum, Ort, Registriervermerk, Seitenbereich).
