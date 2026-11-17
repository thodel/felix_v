// Interface texts in German, French and Latin. Keys are used by data-i18n attributes and t().
// Values may contain HTML; {name} is replaced by t(key, {name: …}).
const I18N = {
  de: {
    "lang.name": "Deutsch",
    "brand": "Bullarium Felix’ V.",
    "nav.regests": "Regesten", "title.regests": "Regesten",
    "rg.h1": "Regesten", "rg.badge": "automatisch, Entwurf",
    "rg.lede": `Für jeden erkannten Eintrag ein Regest in Deutsch, Französisch und Latein. qwen3.8 (GPUStack der Universität Bern)
      hat es aus der automatischen Lesung geschrieben. Datum und Ausstellungsort stammen nicht vom Modell, sondern aus der
      Datumszeile und den Rechenregeln (siehe <a href="methode.html">Methode</a>), der Registriervermerk aus der Segmentierung.`,
    "rg.note": `<strong>Entwürfe, nicht geprüft.</strong> Die Regesten beruhen auf fehlerhaftem HTR-Text. Namen, Orte und Diözesen
      sind oft falsch aufgelöst (z. B. «Cauri nen dioc» = Taurinensis wurde zu «Chur»). Jedes Regest führt zur Stelle im Bild.`,
    "rg.year": "Jahr", "rg.type": "Rechtsakt", "rg.search": "suchen (Name, Ort, Pfründe …)", "rg.sort": "Sortierung",
    "rg.sort.date": "chronologisch", "rg.sort.reg": "Registerfolge",
    "rg.allvols": "alle Bände", "rg.allyears": "alle Jahre", "rg.alltypes": "alle Rechtsakte",
    "rg.count": "{n} von {total} Regesten", "rg.more": "{n} weitere anzeigen",
    "rg.to": "Empfänger:", "rg.for": "Begünstigt:", "rg.obj": "Gegenstand:", "rg.vac": "Vakanz:", "rg.val": "Wert:",
    "rg.ex": "Exekutoren:", "rg.reg": "Registriervermerk:", "rg.dioc": "Diözese",
    "rg.multi": "Eintrag enthält vermutlich mehrere Briefe (Segmentierung prüfen)", "rg.low": "geringe Sicherheit",
    "rg.export": `Daten: <a href="data/">docs/data/regests&lt;Band&gt;.json</a> im <a href="https://github.com/thodel/felix_v">Repository</a>.`,
    "act.provision": "Provision", "act.collation": "Kollation", "act.expectative": "Expektanz", "act.dispensation": "Dispens",
    "act.indulgence": "Ablass", "act.absolution": "Absolution", "act.confirmation": "Bestätigung", "act.appointment": "Ernennung",
    "act.licence": "Erlaubnis / Fakultät", "act.exemption": "Exemtion", "act.commission": "Kommission / Mandat",
    "act.union": "Union / Inkorporation", "act.protection": "Schutz", "act.safe_conduct": "Geleit", "act.other": "anderes",
    "nav.vols": "Bände", "nav.entries": "Einträge", "nav.register": "Register", "nav.method": "Methode & Tests",
    "vol": "Band", "img": "Aufnahme", "imgs": "Aufnahmen", "lines": "Zeilen", "line": "Zeile", "entries": "Einträge",
    "badge.auto": "automatische Erstlesung", "badge.short": "automatisch",
    "flag.ok": "✓ Pont.-Jahr", "flag.ok.t": "Pontifikatsjahr passt zum Datum",
    "flag.range": "⚠ ausserhalb", "flag.range.t": "Datum liegt ausserhalb des Pontifikats (5.11.1439–7.4.1449): sicher ein Lesefehler",
    "flag.bad": "⚠ prüfen", "flag.bad.t": "Pontifikatsjahr passt nicht zum Datum: Lesefehler prüfen",
    "flag.none": "ungeprüft", "flag.none.t": "Kein Pontifikatsjahr gelesen",
    "flag.supra": "ut supra", "flag.supra.t": "«Datum ut supra»: vom vorangehenden Eintrag übernommen",
    "undated": "undatiert", "loading": "Lade …", "error": "Fehler beim Laden",
    "title.index": "Bullarium Felix’ V.",
    "idx.lede": `Die Register des Gegenpapstes Felix V. (1439–1449), zuvor Herzog Amadeus VIII. von Savoyen
      (<a href="https://hls-dhs-dss.ch/de/articles/012614/2006-04-10/">HLS-Artikel</a>): acht Bände mit Abschriften
      päpstlicher Urkunden, als Mikrofilmaufnahmen in Transkribus (Sammlung «Bollario de Felice»). Jede Aufnahme zeigt eine Doppelseite.`,
    "idx.note": `<strong>Alles hier ist maschinell erzeugt und ungeprüft.</strong> Der Text ist eine Erstlesung der
      Handschriftenerkennung: CITlab HTR aus Transkribus («Generic Model Charter Scripts XIII–XV») und CATMuS Medieval
      (kraken), standardmässig zu einer Lesung kombiniert. Einteilung in Einträge und Datierungen sind ein erster
      automatischer Versuch. Zitieren nur nach dem Bild.`,
    "idx.overview": "Übersicht",
    "idx.th": ["Band", "Aufnahmen", "Zeilen", "Einträge", "datiert", "davon geprüft", "Zeitraum (geprüfte Daten)"],
    "idx.card": "{pages} Aufnahmen · {entries} Einträge", "idx.alt": "Band {v}, eine Doppelseite",
    "idx.checked": `«geprüft» heisst: Das gelesene Pontifikatsjahr passt zum gelesenen Datum (erstes Jahr ab der Wahl am
      5. November 1439, die weiteren ab der Krönung am 24. Juli 1440). Das ist eine Plausibilitätsprüfung, keine Kontrolle
      am Bild. Mehr unter <a href="methode.html">Methode &amp; Tests</a>.`,
    "idx.credits": `Bilder: Transkribus (READ-COOP), direkt von dort geladen. Daten und Code:
      <a href="https://github.com/thodel/felix_v">github.com/thodel/felix_v</a>.`,
    "title.band": "Band {v}, Aufnahme {p}",
    "band.prev": "Vorherige Aufnahme", "band.next": "Nächste Aufnahme",
    "band.reading": "Lesung", "r.k": "Kombiniert (CITlab + CATMuS)", "r.t": "CITlab (Transkribus-HTR)",
    "r.k.multi": "Kombiniert ({n} Lesungen)", "r.unsure": "Leser uneinig: unsicher", "r.note.k.multi": "Mehrheitslesung; gepunktet: Leser uneinig.", "r.note.line": "Zeilenlesung eines einzelnen Modells.",
    "r.c": "CATMuS Medieval (kraken, diplomatisch)", "r.page": "{model} (Seitenlesung, Stichprobe)", "r.missing": "– noch nicht gelesen",
    "r.fromc": "aus CATMuS übernommen", "r.left": "linke Seite", "r.right": "rechte Seite",
    "r.note.k": "Unterstrichen: Wörter, die CATMuS liefert.", "r.note.k.none": "Noch keine CATMuS-Lesung: angezeigt wird CITlab.",
    "r.note.c": "Diplomatisch: Abkürzungen wie in der Handschrift.", "r.note.page": "Seitenlesung ohne Zeilenbezug: keine Verknüpfung mit dem Bild.",
    "band.allbox": "Zeilen im Bild", "band.allbox.t": "Alle erkannten Zeilen im Bild einblenden",
    "band.tab.text": "Text", "band.tab.ent": "Einträge auf dieser Aufnahme",
    "band.notext": "Auf dieser Aufnahme hat die Erkennung keinen Text gefunden.",
    "band.noent": "Keine Einträge erkannt.", "band.lineTitle": "Zeile {n}: im Bild zeigen",
    "band.toEntry": "Zum Anfang des Eintrags", "band.strip": "Aufnahmen",
    "band.span": "Aufnahme {from} · {n} Zeilen",
    "band.help": "Zeile anklicken: im Bild zeigen · ins Bild klicken: Zeile finden · ↑ ↓ Zeilen, ← → Aufnahmen",
    "title.entries": "Einträge",
    "ent.h1": "Einträge", "ent.badge": "automatisch segmentiert",
    "ent.lede": `Ein Eintrag reicht hier vom Ende einer Datumszeile («Datum Basilee …») bis zum Ende der nächsten.
      Das Datum hat qwen3.8 aus der erkannten Datumszeile gelesen; das Tagesdatum (römische Zählung, Jahr nach
      Weihnachtsstil) ist daraus berechnet und gegen das Pontifikatsjahr geprüft.`,
    "ent.onlyBad": "nur «prüfen»", "ent.count": "{n} von {total} Einträgen",
    "ent.open": "Klicken: Eintrag im Viewer öffnen", "ent.preview": "Anfang von {id} im Bild", "band.inentry": "Eintrag {id}: Zeilen hervorgehoben",
    "ent.th": ["Nr.", "Aufnahme", "Datum", "", "Ort", "Anfang · Datumszeile (automatisch)"],
    "title.register": "Register",
    "reg.h1": "Register", "reg.badge": "automatisch",
    "reg.kind.dioceses": "Diözesen", "reg.onlyLinked": "nur verknüpfte", "reg.onlyMulti": "in mehreren Einträgen",
    "reg.th2": ["Name", "Schreibungen im Text", "Angaben", "Verknüpfungen", "Einträge"],
    "reg.grade.identical": "identisch", "reg.grade.very_likely": "sehr wahrscheinlich",
    "reg.grade.merged": "aus fast gleichen Schreibungen mit gleicher Diözese oder gleichem Amt zusammengeführt (sehr wahrscheinlich)",
    "reg.more": "{n} weitere: Filter verwenden",
    "reg.stats2": "{p} Personen ({pl} verknüpft) · {o} Orte ({ol} verknüpft) · {d} Diözesen ({dl} verknüpft) · {i} Institutionen",
    "reg.lede2": `Personen, Orte, Diözesen und Institutionen, die qwen3.8 beim Regestieren aus jedem Eintrag gezogen hat. Gleiche Namen
      im ganzen Korpus sind zusammengeführt. Verknüpft wird mit dem Königsfelden-Register, der Personendatenbank der SSRQ, dem
      HLS, Wikidata und Human Lineage, aber nur bei <strong>identischem</strong> oder <strong>sehr wahrscheinlichem</strong> Treffer.`,
    "reg.note2": `<strong>Automatisch, ungeprüft.</strong> «identisch»: gleiche normalisierte Namensform, ein einziger Kandidat, Daten
      passen. «sehr wahrscheinlich» (≈): fast gleiche Schreibung mit gleicher Diözese oder gleichem Amt, oder ein Treffer, den die
      Normdatei selbst als eindeutig ausweist, mit passenden Lebensdaten. Alles andere bleibt unverknüpft; Lesefehler im Namen
      verhindern also eher eine Verknüpfung, als dass sie eine falsche erzeugen.`,
    "reg.sources": `Quellen der Verknüpfung: Königsfelden (Urkunden und Akten des Klosters Königsfelden), SSRQ (Sammlung Schweizerischer
      Rechtsquellen), HLS (Historisches Lexikon der Schweiz), Wikidata, Human Lineage (CC BY-SA 4.0).`,
    "reg.lede": `Personen, Orte und Institutionen, die qwen3.8 (GPUStack der Universität Bern) aus einer Stichprobe von
      Einträgen gezogen hat, ohne jede Nachkontrolle. Grundlage ist der fehlerhafte HTR-Text; die «normalisierte» Form
      stammt vom Modell und ist oft geraten. Das Register zeigt, was die Methode leistet, und ist kein Arbeitsinstrument.`,
    "reg.kind.persons": "Personen", "reg.kind.places": "Orte", "reg.kind.institutions": "Institutionen",
    "reg.filter": "filtern …", "reg.count": "{n} Namen",
    "reg.th": ["Name (normalisiert vom Modell)", "geschrieben als", "Angaben", "Einträge"],
    "reg.sumH": "Zusammenfassungen der getesteten Einträge", "reg.sumTh": ["Eintrag", "Zusammenfassung (Modell, englisch)"],
    "reg.stats": "{tested} Einträge getestet · {persons} Personen · {places} Orte · {institutions} Institutionen",
    "reg.none": "Noch kein Register erzeugt.",
    "title.method": "Methode und Tests",
    "m.h1": "Methode und Tests",
    "m.lede": `Stand: {date}. Was hier steht, ist ein erster Durchgang. Jede Zahl ist eine Messung an maschinell gelesenem
      Text, ohne korrigierte Vergleichsseiten.`,
    "m.h.source": "Quelle und Erstlesung",
    "m.source": `Transkribus-Sammlung 53095 «Bollario de Felice»: acht Dokumente, 2'699 Aufnahmen von Mikrofilm, jede eine
      Doppelseite des Registers. Der Text stammt aus der Handschriftenerkennung in Transkribus (CITlab HTR, «Generic Model
      Charter Scripts XIII–XV»). Alle Seiten stehen auf IN_PROGRESS, keine ist korrigiert. Die Website lädt die Bilder direkt
      von Transkribus und zeigt den Text unverändert.`,
    "m.h.read": "Lesetest: welches Modell liest besser?",
    "m.read": `Stichprobe: 50 Doppelseiten aus allen acht Bänden (zufällig mit festem Seed; qwen3.8 las die ersten 16), an der Grenze der
      Textblöcke im PageXML in 100 Seitenhälften geschnitten. Jede Hälfte wird gelesen und mit der CITlab-Lesung derselben Hälfte verglichen.`,
    "m.read.note": `Es gibt noch keine korrigierten Seiten. Die «Abweichung von CITlab» sagt deshalb nicht, wer richtig liest:
      Ein Modell, das besser liest als CITlab, weicht ebenfalls ab. Was die Zahlen sicher zeigen: Abbrüche an der
      Token-Grenze, Wiederholungsschleifen und Längenverhältnis (ausgelassener oder erfundener Text).`,
    "m.read.th": ["Leser", "Hälften", "Abweichung von CITlab (CER, Median)", "leer", "abgebrochen", "mit Schleifen", "Länge / CITlab (Median)", "s / Hälfte"],
    "m.read.qwen": `<strong>qwen3.8-27b</strong> (GPUStack, ohne «thinking»): für diese Seiten <strong>nicht brauchbar</strong>.
      Auf der ersten Probe (Band I, Aufnahme 11) liess es die ersten zehn Zeilen aus, geriet in Wiederholungsschleifen
      («D. D. de S. …») und erfand auf der rechten Seite ein «Felix episcopus servus servorum dei», wo der Text mitten im
      Satz weiterläuft. In der Stichprobe brechen die meisten Hälften an der Token-Grenze ab, und die Ausgabe ist mehrfach
      so lang wie die CITlab-Lesung. Geprüft wurden drei Einstellungen (2048 px mit und ohne Wiederholungsstrafe, 3072 px
      auf den Textblock zugeschnitten); keine half.`,
    "m.read.gemini": `<strong>Gemini 3.8 Flash und Gemini 4 Argon</strong> (17.11.2026, 100 Hälften aus 50 Aufnahmen aller
      acht Bände, Prompt <code>felix_register_page_v1.md</code>, geringe Denktiefe): beide lesen die ganze Hälfte, ohne
      Abbruch und ohne Schleifen, und lösen Abkürzungen auf wie CITlab. <strong>Argon</strong> kam nie leer zurück und liegt
      am nächsten bei CITlab (15 %), rund 17 Sekunden pro Hälfte. <strong>Flash</strong> ist schneller (11 s), gab aber 9 von
      100 beschriebenen Hälften leer zurück; ein zweiter Versuch mit denselben Einstellungen holte 5 davon, 4 blieben leer (alle
      vier beginnen mitten im Satz). Flash und Argon stimmen untereinander enger überein (10 %) als jedes von ihnen
      mit CITlab. Beispiel: den Registraturvermerk, den CITlab als «ep̄us Brosseran» liest, liest Gemini als «A. Episcopus
      Grossetanus» (Bischof von Grosseto). Die Gemini-Lesungen dieser 50 Aufnahmen stehen im Betrachter unter «Text» zur
      Wahl.`,
    "m.read.matrix": `Wie weit die Leser untereinander auseinanderliegen (CER der Zeilenlesung, Median über die Hälften,
      die beide gelesen haben; Zeile gegen Spalte gemessen). Eine Gold-Lesung fehlt: Nähe heisst Übereinstimmung, nicht Richtigkeit.`,
    "m.read.vote": "Mehrheitslesung",
    "m.read.gt": `<strong>Für ein echtes Urteil</strong> sollen 8 Hälften (eine je Band) in Transkribus korrigiert werden.
      Dann misst dasselbe Skript die Zeichenfehlerrate jedes Lesers gegen die Korrektur.`,
    "m.read.catmus": `<strong>CATMuS Medieval</strong> (kraken, auf dem ATR-Gateway): liest alle 2'699 Aufnahmen auf den
      Zeilen von Transkribus, rund 3 Sekunden pro Aufnahme. Diplomatisch: Abkürzungszeichen bleiben stehen, u für v. Weicht auf
      der ersten Probe zu 30 % (CER) von CITlab ab, grösstenteils wegen der nicht aufgelösten Abkürzungen.`,
    "m.read.comb": `<strong>Kombinierte Lesung</strong> (Standard im Viewer): Wort für Wort ausgerichtet; wo CITlab und CATMuS
      übereinstimmen, gilt die aufgelöste Form von CITlab. Wo sie abweichen, ersetzt das CATMuS-Wort das CITlab-Wort nur, wenn es
      ausgeschrieben ist (kein Abkürzungszeichen), im gesamten CITlab-Text der acht Bände mindestens fünfmal vorkommt und das
      CITlab-Wort dort selten ist; Namen nur durch sehr häufige Wörter, verkürzte Formen nie. So ersetzt es z. B. «Basler» durch
      «Basilee», «as audienciam» durch «ad audienciam», «courra» durch «contra». Ein Sprachmodell (qwen3.8) als Schiedsrichter
      wurde geprüft und verworfen: es übernahm CITlab Zeile für Zeile. Ersetzte Wörter sind im Viewer unterstrichen.`,
    "m.read.multi": `<strong>Acht Lesungen pro Zeile</strong> (ab 16.11.2026): Neben CITlab lesen auf UBELIX sieben Modelle jede Zeile
      von Transkribus: kraken CATMuS Medieval, TRIDIS v2, CREMMA Medieval und Medieval Latin/French (aufgelöst) sowie TrOCR
      medieval-escriptmask und zwei TrOCR-Modelle auf CATMuS (base, cursiva). Die kombinierte Lesung ist eine Mehrheitsentscheidung
      Wort für Wort: Grundgerüst ist die Lesung, die allen anderen am nächsten steht; jedes Modell stimmt mit einem Gewicht ab, das
      aus seiner Übereinstimmung mit den anderen im selben Band berechnet ist (ein Modell, das diese Hand schlecht liest, zählt
      wenig). Angezeigt wird die Form eines auflösenden Modells. Wörter mit weniger als der Hälfte der Stimmen sind im Viewer
      gepunktet unterstrichen. Bis die acht Lesungen da sind, gilt die vorsichtige Zwei-Leser-Regel unten.`,
    "m.ner.v2": `<strong>Entitäten im ganzen Korpus</strong> (ab 16.11.2026): Personen, Orte, Diözesen und Institutionen zieht qwen3.8 im
      selben Aufruf wie das Regest aus jedem Eintrag, mit der Schreibung im Text; Registriervermerke (Schreiber) und der Papst
      selbst sind ausgenommen. <strong>Verknüpfung</strong> nur bei identischem oder sehr wahrscheinlichem Treffer: innerhalb des
      Korpus bei gleicher normalisierter Namensform (bzw. fast gleicher Schreibung mit gleicher Diözese oder gleichem Amt); nach
      aussen mit Human Lineage (Treffer, den die Normdatei selbst als eindeutig ausweist, mit passenden Lebensdaten; daraus Wikidata
      und HLS), der SSRQ und dem Königsfelden-Register (genaue Namensform, ein einziger Kandidat, Zeit passt), für Orte mit
      Königsfelden und Wikidata (genauer Name, Siedlung in CH/FR/IT/DE; HLS über die HLS-Nummer), für Diözesen über eine feste Liste
      der lateinischen Adjektive. Ergebnis: <a href="register.html">Register</a>. Der Test auf 40 Einträgen unten bleibt als
      Ausgangspunkt stehen.`,
    "m.read.example": "Beispiel nebeneinander", "m.read.view": "Bild ansehen", "m.read.half": "Seitenhälfte",
    "m.read.left": "links", "m.read.right": "rechts", "m.read.dev": "Abw.", "m.read.trunc": "abgebrochen",
    "m.h.ner": "Entitäten und Register (Test)",
    "m.ner": `qwen3.8 hat aus {tested} zufällig gezogenen Einträgen Personen (mit Rolle, Amt, Diözese), Orte, Institutionen
      und Daten gezogen, dazu eine Zusammenfassung in einem Satz. Ergebnis: <a href="register.html">Register (Test)</a>.`,
    "m.ner.shows": "Was der Test zeigt (automatisch geprüft, ohne Abgleich am Bild):",
    "m.ner.1": `<strong>Die Menge stimmt:</strong> {persons} Personen, {places} Orte, {institutions} Institutionen, im Mittel
      {secs} Sekunden pro Eintrag. Pfründen, Diözesen und Pfarreien kommen gut heraus (z. B. Andreas Karoleti, Kaplan in
      Seysiriato, Diözese Lyon).`,
    "m.ner.2": `<strong>Normalisierung ist zweischneidig:</strong> «monasterii Sancti manner agavensi» wird richtig zu
      St-Maurice d’Agaune, «abbati morii Loncedi» aber frei zu «Cluny». Bei {np} Personen, {nl} Orten und {ni} Institutionen
      steht die Form «wie geschrieben» nicht wörtlich im Text; meist sind das über Zeilen zusammengezogene Namen, teils
      Erfindungen («Felix V»).`,
    "m.ner.3": `<strong>Registriervermerke werden zu Personen:</strong> «ep̄us Brosseran», «Jo. Benenati» erscheinen als
      Personen der Urkunde oder sogar als Diözese. {other} Personen haben die Rolle «other». Diese Schreiber gehören in ein
      eigenes Feld.`,
    "m.ner.4": `<strong>Daten im Fliesstext</strong> rechnet das Modell oft falsch um (z. B. 1449 statt 1440). Daten deshalb
      nur über die Datumszeile und die Rechenregeln unten.`,
    "m.ner.assess": `<strong>Einschätzung:</strong> Als Findhilfe brauchbar, als Register erst nach drei Änderungen: Schreiber
      trennen, Orte gegen eine Diözesanliste normalisieren, Personen mit Normdaten abgleichen (SSRQ, HLS, Human Lineage).
      Mit einer besseren Lesung (siehe Lesetest) steigt die Qualität direkt mit.`,
    "m.h.seg": "Segmentierung nach Eintrag und Datum",
    "m.seg.entries": `<strong>Einträge (v1, regelbasiert).</strong> Jede Registerabschrift endet mit einer Datumszeile
      («Datum Basilee … pontificatus nostri anno …») und meist einem Registriervermerk (Zählzeichen und Name des Schreibers).
      Ein Eintrag reicht vom Ende einer Datumszeile bis zum Ende der nächsten. Erkannt wird sie an «Dat(um)» oder einem
      Ausstellungsort, gefolgt von «nativitate / millesimo». Als zweites Signal trennt auch ein Incipit («Felix episcopus …»)
      ohne vorangehende Datumszeile.`,
    "m.seg.date": `<strong>Datum.</strong> qwen3.8 liest die Datumszeile nur in Felder (Ort, Ordinalzahl, Kalenden/Nonen/Iden,
      Monat, Jahr, Pontifikatsjahr). Das Tagesdatum rechnet das Skript: römische Tageszählung, Jahresanfang nach
      Weihnachtsstil, Pontifikatsjahre: das erste ab der Wahl (5. November 1439, «a die suscepti a nobis apostolatus officii»)
      bis zum ersten Jahrestag der Krönung, die weiteren ab der Krönung am 24. Juli 1440. Passt das gelesene Pontifikatsjahr
      zum Datum, gilt das Datum als plausibel (✓). Sonst ist es zu prüfen (⚠), meist wegen eines Lesefehlers.`,
    "m.seg.th": ["Band", "Einträge", "mit Datum", "✓ Pont.-Jahr", "⚠ prüfen", "ohne Datumszeile"],
    "m.seg.next": `<strong>Nächste Schritte (v2).</strong> (1) Das Modell nennt pro Doppelseite die Zeilen, mit denen ein Brief
      beginnt oder die eine Datierung enthalten; nur Abweichungen von v1 kommen auf eine Prüfliste. (2) Die Chronologie der
      Register dient als Plausibilitätsprüfung: Ein Datum, das stark von seinen Nachbarn abweicht, wird markiert. (3) Liest
      Gemini oder Argon deutlich besser, wird auf dieser Lesung neu segmentiert. Ausführlich:
      <a href="https://github.com/thodel/felix_v/blob/main/PLAN.md">PLAN.md</a>.`,
  },

  fr: {
    "lang.name": "Français",
    "brand": "Bullaire de Félix V",
    "nav.regests": "Régestes", "title.regests": "Régestes",
    "rg.h1": "Régestes", "rg.badge": "automatique, brouillon",
    "rg.lede": `Pour chaque entrée reconnue, un régeste en allemand, en français et en latin, rédigé par qwen3.8 (GPUStack de
      l’Université de Berne) à partir de la lecture automatique. La date et le lieu d’émission ne viennent pas du modèle, mais
      de la clause de date et des règles de calcul (voir <a href="methode.html">Méthode</a>) ; la mention d’enregistrement
      vient du découpage.`,
    "rg.note": `<strong>Brouillons non vérifiés.</strong> Les régestes reposent sur un texte HTR fautif. Noms, lieux et diocèses
      sont souvent mal identifiés (p. ex. « Cauri nen dioc » = Taurinensis est devenu « Coire »). Chaque régeste renvoie au
      passage sur l’image.`,
    "rg.year": "Année", "rg.type": "Type d’acte", "rg.search": "chercher (nom, lieu, bénéfice …)", "rg.sort": "Tri",
    "rg.sort.date": "chronologique", "rg.sort.reg": "ordre du registre",
    "rg.allvols": "tous les volumes", "rg.allyears": "toutes les années", "rg.alltypes": "tous les actes",
    "rg.count": "{n} sur {total} régestes", "rg.more": "afficher {n} de plus",
    "rg.to": "Destinataire :", "rg.for": "Bénéficiaire :", "rg.obj": "Objet :", "rg.vac": "Vacance :", "rg.val": "Valeur :",
    "rg.ex": "Exécuteurs :", "rg.reg": "Mention d’enregistrement :", "rg.dioc": "diocèse",
    "rg.multi": "l’entrée contient sans doute plusieurs lettres (vérifier le découpage)", "rg.low": "faible certitude",
    "rg.export": `Données : <a href="data/">docs/data/regests&lt;volume&gt;.json</a> dans le <a href="https://github.com/thodel/felix_v">dépôt</a>.`,
    "act.provision": "Provision", "act.collation": "Collation", "act.expectative": "Expectative", "act.dispensation": "Dispense",
    "act.indulgence": "Indulgence", "act.absolution": "Absolution", "act.confirmation": "Confirmation", "act.appointment": "Nomination",
    "act.licence": "Licence / faculté", "act.exemption": "Exemption", "act.commission": "Commission / mandat",
    "act.union": "Union / incorporation", "act.protection": "Protection", "act.safe_conduct": "Sauf-conduit", "act.other": "autre",
    "nav.vols": "Volumes", "nav.entries": "Entrées", "nav.register": "Index", "nav.method": "Méthode et tests",
    "vol": "Volume", "img": "Image", "imgs": "images", "lines": "lignes", "line": "Ligne", "entries": "entrées",
    "badge.auto": "première lecture automatique", "badge.short": "automatique",
    "flag.ok": "✓ an. pont.", "flag.ok.t": "L’année de pontificat concorde avec la date",
    "flag.range": "⚠ hors pontificat", "flag.range.t": "La date tombe hors du pontificat (5.11.1439–7.4.1449) : erreur de lecture certaine",
    "flag.bad": "⚠ à vérifier", "flag.bad.t": "L’année de pontificat ne concorde pas avec la date : vérifier la lecture",
    "flag.none": "non vérifié", "flag.none.t": "Aucune année de pontificat n’a été lue",
    "flag.supra": "ut supra", "flag.supra.t": "« Datum ut supra » : date reprise de l’entrée précédente",
    "undated": "sans date", "loading": "Chargement …", "error": "Erreur de chargement",
    "title.index": "Bullaire de Félix V",
    "idx.lede": `Les registres de l’antipape Félix V (1439–1449), auparavant Amédée VIII, duc de Savoie
      (<a href="https://hls-dhs-dss.ch/fr/articles/012614/2006-04-10/">article du DHS</a>) : huit volumes de copies d’actes
      pontificaux, sous forme de microfilms numérisés dans Transkribus (collection « Bollario de Felice »). Chaque image
      montre une double page.`,
    "idx.note": `<strong>Tout ce qui figure ici est produit par la machine et n’a pas été vérifié.</strong> Le texte est une
      première lecture par reconnaissance d’écriture : CITlab HTR de Transkribus (« Generic Model Charter Scripts XIII–XV »)
      et CATMuS Medieval (kraken), combinées par défaut en une seule lecture. Le découpage en entrées et les datations sont
      un premier essai automatique. Ne citer que d’après l’image.`,
    "idx.overview": "Vue d’ensemble",
    "idx.th": ["Volume", "Images", "Lignes", "Entrées", "datées", "dont vérifiées", "Période (dates vérifiées)"],
    "idx.card": "{pages} images · {entries} entrées", "idx.alt": "Volume {v}, une double page",
    "idx.checked": `« vérifiée » signifie : l’année de pontificat lue concorde avec la date lue (première année à partir de
      l’élection du 5 novembre 1439, les suivantes à partir du couronnement du 24 juillet 1440). C’est un contrôle de
      vraisemblance, non une vérification sur l’image. Voir <a href="methode.html">Méthode et tests</a>.`,
    "idx.credits": `Images : Transkribus (READ-COOP), chargées directement depuis ce service. Données et code :
      <a href="https://github.com/thodel/felix_v">github.com/thodel/felix_v</a>.`,
    "title.band": "Volume {v}, image {p}",
    "band.prev": "Image précédente", "band.next": "Image suivante",
    "band.reading": "Lecture", "r.k": "Combinée (CITlab + CATMuS)", "r.t": "CITlab (HTR de Transkribus)",
    "r.k.multi": "Combinée ({n} lectures)", "r.unsure": "Lecteurs en désaccord : incertain", "r.note.k.multi": "Lecture majoritaire ; en pointillé : lecteurs en désaccord.", "r.note.line": "Lecture ligne par ligne d’un seul modèle.",
    "r.c": "CATMuS Medieval (kraken, diplomatique)", "r.page": "{model} (lecture de page, échantillon)", "r.missing": "– pas encore lue",
    "r.fromc": "repris de CATMuS", "r.left": "page de gauche", "r.right": "page de droite",
    "r.note.k": "Soulignés : mots fournis par CATMuS.", "r.note.k.none": "Pas encore de lecture CATMuS : affichage de CITlab.",
    "r.note.c": "Diplomatique : abréviations comme dans le manuscrit.", "r.note.page": "Lecture de page sans lien avec les lignes : pas de liaison avec l’image.",
    "band.allbox": "Lignes sur l’image", "band.allbox.t": "Afficher toutes les lignes reconnues sur l’image",
    "band.tab.text": "Texte", "band.tab.ent": "Entrées sur cette image",
    "band.notext": "La reconnaissance n’a trouvé aucun texte sur cette image.",
    "band.noent": "Aucune entrée reconnue.", "band.lineTitle": "Ligne {n} : la montrer sur l’image",
    "band.toEntry": "Aller au début de l’entrée", "band.strip": "Images",
    "band.span": "Image {from} · {n} lignes",
    "band.help": "Cliquer une ligne : la montrer sur l’image · cliquer l’image : trouver la ligne · ↑ ↓ lignes, ← → images",
    "title.entries": "Entrées",
    "ent.h1": "Entrées", "ent.badge": "découpage automatique",
    "ent.lede": `Une entrée va ici de la fin d’une clause de date (« Datum Basilee … ») à la fin de la suivante. qwen3.8 a lu
      la date dans la clause reconnue ; le jour (comput romain, année selon le style de la Nativité) en est calculé, puis
      contrôlé par l’année de pontificat.`,
    "ent.onlyBad": "seulement « à vérifier »", "ent.count": "{n} sur {total} entrées",
    "ent.open": "Cliquer : ouvrir l’entrée dans la visionneuse", "ent.preview": "Début de {id} sur l’image", "band.inentry": "Entrée {id} : lignes mises en évidence",
    "ent.th": ["N°", "Image", "Date", "", "Lieu", "Début · clause de date (automatique)"],
    "title.register": "Index",
    "reg.h1": "Index", "reg.badge": "automatique",
    "reg.kind.dioceses": "Diocèses", "reg.onlyLinked": "seulement liés", "reg.onlyMulti": "dans plusieurs entrées",
    "reg.th2": ["Nom", "Graphies du texte", "Indications", "Liens", "Entrées"],
    "reg.grade.identical": "identique", "reg.grade.very_likely": "très probable",
    "reg.grade.merged": "réuni à partir de graphies presque identiques avec le même diocèse ou la même fonction (très probable)",
    "reg.more": "{n} de plus : utiliser le filtre",
    "reg.stats2": "{p} personnes ({pl} liées) · {o} lieux ({ol} liés) · {d} diocèses ({dl} liés) · {i} institutions",
    "reg.lede2": `Personnes, lieux, diocèses et institutions que qwen3.8 a relevés dans chaque entrée en rédigeant les régestes. Les noms
      identiques dans tout le corpus sont réunis. Les liens renvoient au registre de Königsfelden, à la base de personnes de la SSRQ,
      au DHS, à Wikidata et à Human Lineage, mais seulement en cas de correspondance <strong>identique</strong> ou
      <strong>très probable</strong>.`,
    "reg.note2": `<strong>Automatique, non vérifié.</strong> « identique » : même forme normalisée du nom, un seul candidat, dates
      compatibles. « très probable » (≈) : graphie presque identique avec le même diocèse ou la même fonction, ou une correspondance
      que le fichier d’autorité lui-même donne comme univoque, avec des dates compatibles. Le reste n’est pas lié ; une erreur de
      lecture dans un nom empêche donc plutôt un lien qu’elle n’en crée un faux.`,
    "reg.sources": `Sources des liens : Königsfelden (chartes et actes du couvent de Königsfelden), SSRQ (Collection des sources du
      droit suisse), DHS (Dictionnaire historique de la Suisse), Wikidata, Human Lineage (CC BY-SA 4.0).`,
    "reg.lede": `Personnes, lieux et institutions que qwen3.8 (GPUStack de l’Université de Berne) a extraits d’un échantillon
      d’entrées, sans aucun contrôle. La base est le texte HTR fautif ; la forme « normalisée » vient du modèle et est
      souvent devinée. L’index montre ce que la méthode peut fournir ; ce n’est pas un instrument de travail.`,
    "reg.kind.persons": "Personnes", "reg.kind.places": "Lieux", "reg.kind.institutions": "Institutions",
    "reg.filter": "filtrer …", "reg.count": "{n} noms",
    "reg.th": ["Nom (normalisé par le modèle)", "graphie du texte", "Indications", "Entrées"],
    "reg.sumH": "Résumés des entrées testées", "reg.sumTh": ["Entrée", "Résumé (modèle, en anglais)"],
    "reg.stats": "{tested} entrées testées · {persons} personnes · {places} lieux · {institutions} institutions",
    "reg.none": "Aucun index n’a encore été produit.",
    "title.method": "Méthode et tests",
    "m.h1": "Méthode et tests",
    "m.lede": `État au {date}. Ce qui suit est un premier passage. Chaque chiffre est une mesure sur du texte lu par la
      machine, sans pages corrigées pour comparaison.`,
    "m.h.source": "Source et première lecture",
    "m.source": `Collection Transkribus 53095 « Bollario de Felice » : huit documents, 2 699 images de microfilm, chacune une
      double page du registre. Le texte provient de la reconnaissance d’écriture de Transkribus (CITlab HTR, « Generic Model
      Charter Scripts XIII–XV »). Toutes les pages sont au statut IN_PROGRESS, aucune n’est corrigée. Le site charge les
      images directement depuis Transkribus et affiche le texte tel quel.`,
    "m.h.read": "Test de lecture : quel modèle lit le mieux ?",
    "m.read": `Échantillon : 50 doubles pages des huit volumes (tirées au hasard avec une graine fixe ; qwen3.8 a lu les 16 premières), coupées en 100 demi-pages
      à la limite des blocs de texte du PageXML. Chaque demi-page est lue puis comparée à la lecture CITlab de la même
      demi-page.`,
    "m.read.note": `Il n’existe pas encore de pages corrigées. L’« écart avec CITlab » ne dit donc pas qui lit juste : un
      modèle qui lit mieux que CITlab s’en écarte aussi. Ce que les chiffres montrent sûrement : les arrêts à la limite de
      jetons, les boucles de répétition et le rapport de longueur (texte omis ou inventé).`,
    "m.read.th": ["Lecteur", "Demi-pages", "Écart avec CITlab (CER, médiane)", "vides", "interrompues", "avec boucles", "Longueur / CITlab (médiane)", "s / demi-page"],
    "m.read.qwen": `<strong>qwen3.8-27b</strong> (GPUStack, sans « thinking ») : <strong>inutilisable</strong> pour ces pages.
      Sur le premier essai (volume I, image 11), il a omis les dix premières lignes, est tombé dans des boucles de répétition
      (« D. D. de S. … ») et a inventé sur la page de droite un « Felix episcopus servus servorum dei » là où le texte
      continue au milieu d’une phrase. Dans l’échantillon, la plupart des demi-pages s’arrêtent à la limite de jetons, et la
      sortie est plusieurs fois plus longue que la lecture CITlab. Trois réglages ont été essayés (2048 px avec et sans
      pénalité de répétition, 3072 px recadré sur le bloc de texte) ; aucun n’a aidé.`,
    "m.read.gemini": `<strong>Gemini 3.8 Flash et Gemini 4 Argon</strong> (17.11.2026, 100 demi-pages tirées de 50 images des
      huit volumes, prompt <code>felix_register_page_v1.md</code>, réflexion faible) : les deux lisent la demi-page entière,
      sans arrêt ni boucle, et développent les abréviations comme CITlab. <strong>Argon</strong> n’a jamais rendu de page vide
      et est le plus proche de CITlab (15 %), environ 17 secondes par demi-page. <strong>Flash</strong> est plus rapide (11 s),
      mais a rendu vides 9 demi-pages écrites sur 100 ; un second essai avec les mêmes réglages en a récupéré 5, 4 sont restées vides
      (toutes quatre commencent au milieu d’une phrase). Flash et Argon s’accordent davantage entre eux (10 %) qu’avec CITlab.
      Exemple : la mention d’enregistrement que CITlab lit « ep̄us Brosseran », Gemini la lit « A. Episcopus Grossetanus »
      (évêque de Grosseto). Les lectures Gemini de ces 50 images sont proposées dans la visionneuse sous « Texte ».`,
    "m.read.matrix": `Écart entre les lecteurs (CER, médiane sur les demi-pages lues par les deux ; la ligne mesurée contre la
      colonne). Il manque une lecture de référence : proximité veut dire accord, non exactitude.`,
    "m.read.vote": "lecture majoritaire",
    "m.read.gt": `<strong>Pour un vrai jugement</strong>, 8 demi-pages (une par volume) doivent être corrigées dans
      Transkribus. Le même script mesurera alors le taux d’erreur de caractères de chaque lecteur par rapport à la
      correction.`,
    "m.read.catmus": `<strong>CATMuS Medieval</strong> (kraken, sur la passerelle ATR) : lit les 2 699 images sur les lignes
      de Transkribus, environ 3 secondes par image. Diplomatique : les signes d’abréviation restent, u pour v. Sur le premier essai,
      écart de 30 % (CER) avec CITlab, surtout à cause des abréviations non développées.`,
    "m.read.comb": `<strong>Lecture combinée</strong> (par défaut dans la visionneuse) : alignement mot à mot ; là où CITlab et
      CATMuS concordent, la forme développée de CITlab est retenue. Là où ils divergent, le mot de CATMuS ne remplace celui de
      CITlab que s’il est écrit en toutes lettres (sans signe d’abréviation), s’il apparaît au moins cinq fois dans tout le texte
      CITlab des huit volumes et si le mot de CITlab y est rare ; les noms seulement par des mots très fréquents, jamais par des
      formes tronquées. Ainsi « Basler » devient « Basilee », « as audienciam » « ad audienciam », « courra » « contra ». Un
      modèle de langue (qwen3.8) comme arbitre a été essayé puis écarté : il recopiait CITlab ligne par ligne. Les mots remplacés
      sont soulignés dans la visionneuse.`,
    "m.read.multi": `<strong>Huit lectures par ligne</strong> (dès le 16.11.2026) : outre CITlab, sept modèles lisent sur UBELIX chaque
      ligne de Transkribus : kraken CATMuS Medieval, TRIDIS v2, CREMMA Medieval et Medieval Latin/French (développé), ainsi que
      TrOCR medieval-escriptmask et deux modèles TrOCR entraînés sur CATMuS (base, cursiva). La lecture combinée est un vote
      majoritaire mot à mot : la base est la lecture la plus proche de toutes les autres ; chaque modèle vote avec un poids calculé
      d’après son accord avec les autres dans le même volume (un modèle qui lit mal cette main pèse peu). On affiche la forme d’un
      modèle qui développe les abréviations. Les mots qui obtiennent moins de la moitié des voix sont soulignés en pointillé. Tant
      que les huit lectures manquent, la règle prudente à deux lecteurs ci-dessous s’applique.`,
    "m.ner.v2": `<strong>Entités dans tout le corpus</strong> (dès le 16.11.2026) : personnes, lieux, diocèses et institutions sont relevés
      par qwen3.8 dans le même appel que le régeste, avec la graphie du texte ; les mentions d’enregistrement (scribes) et le pape
      lui-même sont exclus. <strong>Liens</strong> seulement en cas de correspondance identique ou très probable : dans le corpus,
      même forme normalisée du nom (ou graphie presque identique avec le même diocèse ou la même fonction) ; vers l’extérieur, Human
      Lineage (correspondance que le fichier d’autorité donne comme univoque, dates compatibles ; de là Wikidata et le DHS), la SSRQ
      et le registre de Königsfelden (forme exacte du nom, un seul candidat, époque compatible) ; pour les lieux Königsfelden et
      Wikidata (nom exact, localité en CH/FR/IT/DE ; DHS par son numéro) ; pour les diocèses une liste fixe des adjectifs latins.
      Résultat : <a href="register.html">Index</a>. Le test sur 40 entrées ci-dessous reste comme point de départ.`,
    "m.read.example": "Exemple côte à côte", "m.read.view": "Voir l’image", "m.read.half": "Demi-page",
    "m.read.left": "gauche", "m.read.right": "droite", "m.read.dev": "écart", "m.read.trunc": "interrompue",
    "m.h.ner": "Entités et index (test)",
    "m.ner": `qwen3.8 a extrait de {tested} entrées tirées au hasard des personnes (avec rôle, fonction, diocèse), des lieux,
      des institutions et des dates, ainsi qu’un résumé d’une phrase. Résultat : <a href="register.html">Index (test)</a>.`,
    "m.ner.shows": "Ce que montre le test (contrôle automatique, sans vérification sur l’image) :",
    "m.ner.1": `<strong>La quantité est là :</strong> {persons} personnes, {places} lieux, {institutions} institutions, en
      moyenne {secs} secondes par entrée. Bénéfices, diocèses et paroisses ressortent bien (p. ex. Andreas Karoleti,
      chapelain à Seysiriato, diocèse de Lyon).`,
    "m.ner.2": `<strong>La normalisation est à double tranchant :</strong> « monasterii Sancti manner agavensi » devient à juste
      titre Saint-Maurice d’Agaune, mais « abbati morii Loncedi » devient librement « Cluny ». Pour {np} personnes, {nl} lieux
      et {ni} institutions, la forme « telle qu’écrite » ne figure pas mot pour mot dans le texte ; ce sont surtout des noms
      réunis par-dessus une fin de ligne, parfois des inventions (« Felix V »).`,
    "m.ner.3": `<strong>Les mentions d’enregistrement deviennent des personnes :</strong> « ep̄us Brosseran », « Jo. Benenati »
      apparaissent comme personnes de l’acte, voire comme diocèse. {other} personnes ont le rôle « other ». Ces scribes
      doivent figurer dans un champ à part.`,
    "m.ner.4": `<strong>Les dates dans le corps du texte</strong> sont souvent mal converties par le modèle (p. ex. 1449 au lieu
      de 1440). Les dates ne sont donc tirées que de la clause de date, selon les règles de calcul ci-dessous.`,
    "m.ner.assess": `<strong>Appréciation :</strong> utilisable comme aide à la recherche ; comme index seulement après trois
      changements : séparer les scribes, normaliser les lieux d’après une liste des diocèses, rapprocher les personnes de
      fichiers d’autorité (SSRQ, DHS, Human Lineage). Une meilleure lecture (voir le test de lecture) améliore directement la
      qualité.`,
    "m.h.seg": "Découpage par entrée et par date",
    "m.seg.entries": `<strong>Entrées (v1, par règles).</strong> Chaque copie du registre se termine par une clause de date
      (« Datum Basilee … pontificatus nostri anno … ») et le plus souvent par une mention d’enregistrement (chiffre de
      comptage et nom du scribe). Une entrée va de la fin d’une clause de date à la fin de la suivante. La clause est
      reconnue à « Dat(um) » ou à un lieu d’émission, suivi de « nativitate / millesimo ». Second signal : un incipit
      (« Felix episcopus … ») sans clause de date qui le précède sépare aussi.`,
    "m.seg.date": `<strong>Date.</strong> qwen3.8 se contente de lire la clause en champs (lieu, ordinal, calendes/nones/ides,
      mois, année, année de pontificat). Le jour est calculé par le script : comput romain, début d’année selon le style de
      la Nativité ; années de pontificat : la première à partir de l’élection (5 novembre 1439, « a die suscepti a nobis
      apostolatus officii ») jusqu’au premier anniversaire du couronnement, les suivantes à partir du couronnement du
      24 juillet 1440. Si l’année de pontificat lue concorde avec la date, celle-ci est jugée vraisemblable (✓) ; sinon elle
      est à vérifier (⚠), le plus souvent à cause d’une erreur de lecture.`,
    "m.seg.th": ["Volume", "Entrées", "avec date", "✓ an. pont.", "⚠ à vérifier", "sans clause de date"],
    "m.seg.next": `<strong>Étapes suivantes (v2).</strong> (1) Le modèle indique, pour chaque double page, les lignes où
      commence une lettre ou qui contiennent une date ; seuls les écarts avec v1 vont sur une liste de contrôle. (2) La
      chronologie des registres sert de contrôle de vraisemblance : une date qui s’écarte fortement de ses voisines est
      signalée. (3) Si Gemini ou Argon lit nettement mieux, le découpage est refait sur cette lecture. En détail :
      <a href="https://github.com/thodel/felix_v/blob/main/PLAN.md">PLAN.md</a> (en allemand).`,
  },

  la: {
    "lang.name": "Latine",
    "brand": "Bullarium Felicis V",
    "nav.regests": "Regesta", "title.regests": "Regesta",
    "rg.h1": "Regesta", "rg.badge": "machinaliter, adumbratio",
    "rg.lede": `Pro unaquaque littera agnita regestum Theodisce, Francogallice, Latine, quod qwen3.8 (GPUStack Universitatis
      Bernensis) ex lectione machinali conscripsit. Dies et locus datae non a machina, sed ex clausula datae et regulis
      computandi sumuntur (vide <a href="methode.html">Ratio</a>), nota registrationis ex divisione.`,
    "rg.note": `<strong>Adumbrationes non recognitae.</strong> Regesta textu HTR mendoso nituntur. Nomina, loca, dioeceses saepe
      perperam resolvuntur (exempli gratia «Cauri nen dioc» = Taurinensis in «Curiam» versum est). Quodque regestum ad locum
      in imagine ducit.`,
    "rg.year": "Annus", "rg.type": "Genus actus", "rg.search": "quaere (nomen, locum, beneficium …)", "rg.sort": "Ordo",
    "rg.sort.date": "ordine temporum", "rg.sort.reg": "ordine regesti",
    "rg.allvols": "omnes tomi", "rg.allyears": "omnes anni", "rg.alltypes": "omnia genera",
    "rg.count": "{n} ex {total} regestis", "rg.more": "{n} plura ostendere",
    "rg.to": "Destinatarius:", "rg.for": "Beneficiarius:", "rg.obj": "Res:", "rg.vac": "Vacatio:", "rg.val": "Valor:",
    "rg.ex": "Executores:", "rg.reg": "Nota registrationis:", "rg.dioc": "dioecesis",
    "rg.multi": "littera fortasse plures epistulas continet (divisio inspicienda)", "rg.low": "parum certum",
    "rg.export": `Data: <a href="data/">docs/data/regests&lt;tomus&gt;.json</a> in <a href="https://github.com/thodel/felix_v">repositorio</a>.`,
    "act.provision": "Provisio", "act.collation": "Collatio", "act.expectative": "Gratia expectativa", "act.dispensation": "Dispensatio",
    "act.indulgence": "Indulgentia", "act.absolution": "Absolutio", "act.confirmation": "Confirmatio", "act.appointment": "Nominatio ad officium",
    "act.licence": "Licentia / facultas", "act.exemption": "Exemptio", "act.commission": "Commissio / mandatum",
    "act.union": "Unio / incorporatio", "act.protection": "Protectio", "act.safe_conduct": "Salvus conductus", "act.other": "aliud",
    "nav.vols": "Tomi", "nav.entries": "Litterae", "nav.register": "Index", "nav.method": "Ratio et experimenta",
    "vol": "Tomus", "img": "Imago", "imgs": "imagines", "lines": "versus", "line": "Versus", "entries": "litterae",
    "badge.auto": "prima lectio machinalis", "badge.short": "machinaliter",
    "flag.ok": "✓ annus pont.", "flag.ok.t": "Annus pontificatus cum die congruit",
    "flag.range": "⚠ extra pontificatum", "flag.range.t": "Dies extra pontificatum (5.11.1439–7.4.1449) cadit: certe error lectionis",
    "flag.bad": "⚠ inspiciendum", "flag.bad.t": "Annus pontificatus cum die non congruit: lectio inspicienda",
    "flag.none": "non probatum", "flag.none.t": "Annus pontificatus lectus non est",
    "flag.supra": "ut supra", "flag.supra.t": "«Datum ut supra»: dies ex littera praecedente sumptus",
    "undated": "sine die", "loading": "Legitur …", "error": "Data legi non potuerunt",
    "title.index": "Bullarium Felicis V",
    "idx.lede": `Regesta antipapae Felicis V (1439–1449), qui antea Amedeus VIII dux Sabaudiae fuit
      (<a href="https://hls-dhs-dss.ch/de/articles/012614/2006-04-10/">lexicon historicum Helvetiae</a>): octo tomi, quibus
      litterae papales exscriptae continentur, ex imaginibus microfilmatis in Transkribus (collectio «Bollario de Felice»).
      Quaeque imago binas paginas oppositas exhibet.`,
    "idx.note": `<strong>Omnia hic a machina facta neque recognita sunt.</strong> Textus est prima lectio ab arte scripturae
      agnoscendae facta: CITlab HTR ex Transkribus («Generic Model Charter Scripts XIII–XV») et CATMuS Medieval (kraken),
      quae per defaltam in unam lectionem coniunguntur. Divisio in litteras diesque assignati primus conatus machinalis sunt. Nihil nisi ex imagine citetur.`,
    "idx.overview": "Conspectus",
    "idx.th": ["Tomus", "Imagines", "Versus", "Litterae", "datae", "ex his probatae", "Tempus (dies probati)"],
    "idx.card": "{pages} imagines · {entries} litterae", "idx.alt": "Tomus {v}, binae paginae",
    "idx.checked": `«probatae» significat annum pontificatus lectum cum die lecto congruere (annus primus ab electione die
      5 mensis Novembris 1439, ceteri a coronatione die 24 mensis Iulii 1440). Haec est probatio verisimilitudinis, non
      collatio cum imagine. Plura sub <a href="methode.html">Ratio et experimenta</a>.`,
    "idx.credits": `Imagines: Transkribus (READ-COOP), inde directe allatae. Data et codex:
      <a href="https://github.com/thodel/felix_v">github.com/thodel/felix_v</a>.`,
    "title.band": "Tomus {v}, imago {p}",
    "band.prev": "Imago prior", "band.next": "Imago sequens",
    "band.reading": "Lectio", "r.k": "Coniuncta (CITlab + CATMuS)", "r.t": "CITlab (HTR Transkribus)",
    "r.k.multi": "Coniuncta ({n} lectiones)", "r.unsure": "Lectores dissentiunt: incertum", "r.note.k.multi": "Lectio plurium; punctis notata: lectores dissentiunt.", "r.note.line": "Lectio versuum unius exemplaris.",
    "r.c": "CATMuS Medieval (kraken, diplomatica)", "r.page": "{model} (lectio paginae, specimen)", "r.missing": "– nondum lecta",
    "r.fromc": "ex CATMuS sumptum", "r.left": "pagina sinistra", "r.right": "pagina dextra",
    "r.note.k": "Linea subducta: verba quae CATMuS praebet.", "r.note.k.none": "Nondum lectio CATMuS exstat: ostenditur CITlab.",
    "r.note.c": "Diplomatica: compendia ut in codice.", "r.note.page": "Lectio paginae sine versibus: cum imagine non coniungitur.",
    "band.allbox": "Versus in imagine", "band.allbox.t": "Omnes versus agnitos in imagine ostendere",
    "band.tab.text": "Textus", "band.tab.ent": "Litterae in hac imagine",
    "band.notext": "In hac imagine machina nullum textum invenit.",
    "band.noent": "Nullae litterae agnitae.", "band.lineTitle": "Versus {n}: in imagine ostendere",
    "band.toEntry": "Ad initium litterae", "band.strip": "Imagines",
    "band.span": "Imago {from} · {n} versus",
    "band.help": "Versum preme: in imagine ostenditur · imaginem preme: versus invenitur · ↑ ↓ versus, ← → imagines",
    "title.entries": "Litterae",
    "ent.h1": "Litterae", "ent.badge": "machinaliter divisae",
    "ent.lede": `Littera hic a fine unius clausulae datae («Datum Basilee …») usque ad finem sequentis pertinet. Diem ex clausula
      agnita qwen3.8 legit; dies mensis (more Romano computatus, anno a nativitate Domini incipiente) inde calculatur et cum
      anno pontificatus confertur.`,
    "ent.onlyBad": "tantum «inspiciendum»", "ent.count": "{n} ex {total} litteris",
    "ent.open": "Preme: litteram in inspectore aperire", "ent.preview": "Initium {id} in imagine", "band.inentry": "Littera {id}: versus notati",
    "ent.th": ["Num.", "Imago", "Dies", "", "Locus", "Initium · clausula datae (machinaliter)"],
    "title.register": "Index",
    "reg.h1": "Index", "reg.badge": "machinaliter",
    "reg.kind.dioceses": "Dioeceses", "reg.onlyLinked": "tantum coniuncta", "reg.onlyMulti": "in pluribus litteris",
    "reg.th2": ["Nomen", "Formae in textu", "Notae", "Nexus", "Litterae"],
    "reg.grade.identical": "idem", "reg.grade.very_likely": "valde verisimile",
    "reg.grade.merged": "ex formis paene eisdem cum eadem dioecesi vel eodem officio coniunctum (valde verisimile)",
    "reg.more": "{n} plura: filtro utere",
    "reg.stats2": "{p} personae ({pl} coniunctae) · {o} loca ({ol} coniuncta) · {d} dioeceses ({dl} coniunctae) · {i} instituta",
    "reg.lede2": `Personae, loca, dioeceses, instituta, quae qwen3.8 in regestis conscribendis ex singulis litteris excerpsit. Nomina
      eadem per totum corpus coniunguntur. Nexus fiunt cum indice Campi Regis (Königsfelden), cum tabula personarum SSRQ, cum HLS,
      Wikidata, Human Lineage, sed tantum ubi res <strong>eadem</strong> vel <strong>valde verisimilis</strong> est.`,
    "reg.note2": `<strong>Machinaliter, non recognitum.</strong> «idem»: eadem forma nominis normata, unus candidatus, tempora
      congruunt. «valde verisimile» (≈): forma paene eadem cum eadem dioecesi vel eodem officio, vel candidatus quem ipsa tabula
      auctoritatis univocum declarat, temporibus congruentibus. Cetera non coniunguntur; error lectionis in nomine igitur potius
      nexum impedit quam falsum facit.`,
    "reg.sources": `Fontes nexuum: Königsfelden (Urkunden und Akten des Klosters Königsfelden), SSRQ (Sammlung Schweizerischer
      Rechtsquellen), HLS (Historisches Lexikon der Schweiz), Wikidata, Human Lineage (CC BY-SA 4.0).`,
    "reg.lede": `Personae, loca, instituta, quae qwen3.8 (GPUStack Universitatis Bernensis) ex selectis litteris extraxit, nulla
      recognitione adhibita. Fundamentum est textus HTR mendosus; forma «normalis» a machina proficiscitur et saepe
      coniectura est. Index ostendit quid haec ratio praestare possit, nec instrumentum ad laborandum est.`,
    "reg.kind.persons": "Personae", "reg.kind.places": "Loca", "reg.kind.institutions": "Instituta",
    "reg.filter": "quaere …", "reg.count": "{n} nomina",
    "reg.th": ["Nomen (a machina normatum)", "ut scriptum est", "Notae", "Litterae"],
    "reg.sumH": "Summaria litterarum probatarum", "reg.sumTh": ["Littera", "Summarium (machina, Anglice)"],
    "reg.stats": "{tested} litterae probatae · {persons} personae · {places} loca · {institutions} instituta",
    "reg.none": "Nondum index factus est.",
    "title.method": "Ratio et experimenta",
    "m.h1": "Ratio et experimenta",
    "m.lede": `Status die {date}. Quae hic leguntur, primus cursus sunt. Omnis numerus in textu a machina lecto mensus est,
      nullis paginis emendatis ad comparandum.`,
    "m.h.source": "Fons et prima lectio",
    "m.source": `Collectio Transkribus 53095 «Bollario de Felice»: octo documenta, 2699 imagines microfilmatae, quarum quaeque
      binas paginas regesti exhibet. Textus ab arte scripturae agnoscendae in Transkribus provenit (CITlab HTR, «Generic
      Model Charter Scripts XIII–XV»). Omnes paginae in statu IN_PROGRESS sunt, nulla emendata. Situs imagines directe ex
      Transkribus affert textumque immutatum ostendit.`,
    "m.h.read": "Experimentum legendi: quod exemplar melius legit?",
    "m.read": `Specimen: 50 paginae binae ex omnibus octo tomis (fortuito sed semine fixo electae; qwen3.8 primas 16 legit), ad terminos
      textus in PageXML in 100 dimidias paginas sectae. Quaeque dimidia legitur et cum lectione CITlab eiusdem dimidiae confertur.`,
    "m.read.note": `Nondum paginae emendatae exstant. «Discrepantia a CITlab» igitur non indicat quis recte legat: exemplar quod
      melius quam CITlab legit, et ipsum discrepat. Quod numeri certo ostendunt: abruptiones ad terminum signorum (tokens),
      iterationes, rationem longitudinis (textum omissum vel fictum).`,
    "m.read.th": ["Lector", "Dimidiae", "Discrepantia a CITlab (CER, mediana)", "vacuae", "abruptae", "cum iterationibus", "Longitudo / CITlab (mediana)", "sec. / dimidia"],
    "m.read.qwen": `<strong>qwen3.8-27b</strong> (GPUStack, sine «thinking»): ad has paginas <strong>inutile</strong>. In primo
      experimento (tomus I, imago 11) decem primos versus omisit, in iterationes incidit («D. D. de S. …») et in pagina dextra
      «Felix episcopus servus servorum dei» finxit, ubi textus media sententia pergit. In specimine plurimae dimidiae ad
      terminum signorum abrumpuntur, et quod redditur multo longius est quam lectio CITlab. Tres modi probati sunt (2048 px
      cum poena iterationis et sine ea, 3072 px ad textum resecti); nullus profuit.`,
    "m.read.gemini": `<strong>Gemini 3.8 Flash et Gemini 4 Argon</strong> (die 17 Novembris 2026, centum dimidiae ex quinquaginta
      imaginibus omnium octo tomorum, praeceptum <code>felix_register_page_v1.md</code>, cogitatio parva): ambo totam dimidiam
      legunt, sine abruptione et sine iterationibus, et compendia solvunt ut CITlab. <strong>Argon</strong> numquam vacuum
      reddidit et ad CITlab proxime accedit (15 %), circiter 17 secundis per dimidiam. <strong>Flash</strong> celerior est
      (11 s), sed novem ex centum dimidiis scriptis vacuas reddidit; altero conatu isdem modis quinque redditae sunt, quattuor vacuae
      manserunt (omnes media sententia incipiunt). Flash et Argon inter se magis consentiunt (10 %) quam
      uterque cum CITlab. Exemplum: notam registri, quam CITlab «ep̄us Brosseran» legit, Gemini «A. Episcopus Grossetanus»
      (episcopus Grossetanus) legit. Lectiones Gemini harum quinquaginta imaginum in inspectore sub «Textus» eligi possunt.`,
    "m.read.matrix": `Quantum lectores inter se discrepent (CER, mediana dimidiarum quas ambo legerunt; versus contra columnam
      mensus). Lectio certa deest: propinquitas consensum significat, non veritatem.`,
    "m.read.vote": "lectio communis",
    "m.read.gt": `<strong>Ut vere iudicari possit</strong>, octo dimidiae (singulae ex singulis tomis) in Transkribus emendandae
      sunt. Tum idem programma errores litterarum cuiusque lectoris ad emendationem metietur.`,
    "m.read.catmus": `<strong>CATMuS Medieval</strong> (kraken, in porta ATR): omnes 2699 imagines in versibus Transkribus
      legit, circiter 3 secundis in singulas imagines. Diplomatica: signa compendiorum manent, u pro v. In primo experimento a
      CITlab 30 % (CER) discrepat, maxime ob compendia non resoluta.`,
    "m.read.comb": `<strong>Lectio coniuncta</strong> (in inspectore per defaltam): verba singula inter se ordinantur; ubi CITlab
      et CATMuS consentiunt, forma resoluta CITlab valet. Ubi discrepant, verbum CATMuS verbum CITlab tantum substituit, si plene
      scriptum est (sine signo compendii), si in toto textu CITlab octo tomorum saltem quinquies occurrit et verbum CITlab ibi
      rarum est; nomina tantum verbis frequentissimis, formae truncatae numquam. Sic «Basler» in «Basilee», «as audienciam» in
      «ad audienciam», «courra» in «contra» mutatur. Exemplar linguae (qwen3.8) ut arbiter probatum et reiectum est: CITlab
      versum post versum exscripsit. Verba substituta in inspectore linea subducuntur.`,
    "m.read.multi": `<strong>Octo lectiones in singulos versus</strong> (a die 16 Novembris 2026): praeter CITlab septem exemplaria in UBELIX
      quemque versum Transkribus legunt: kraken CATMuS Medieval, TRIDIS v2, CREMMA Medieval, Medieval Latin/French (resolutum),
      atque TrOCR medieval-escriptmask et duo exemplaria TrOCR in CATMuS exercita (base, cursiva). Lectio coniuncta est suffragium
      plurium verbum post verbum: fundamentum est lectio ceteris proxima; quodque exemplar suffragatur pondere ex consensu cum
      ceteris in eodem tomo computato (exemplar quod hanc manum male legit, parum valet). Ostenditur forma exemplaris compendia
      resolventis. Verba quae minus quam dimidiam partem suffragiorum habent, punctis subducuntur. Donec octo lectiones adsint,
      cauta regula duorum lectorum infra posita valet.`,
    "m.ner.v2": `<strong>Nomina per totum corpus</strong> (a die 16 Novembris 2026): personas, loca, dioeceses, instituta qwen3.8 eodem
      actu quo regestum ex unaquaque littera excerpit, cum forma textus; notae registrationis (scriptores) et ipse papa excluduntur.
      <strong>Nexus</strong> tantum ubi res eadem vel valde verisimilis est: intra corpus eadem forma nominis normata (vel forma
      paene eadem cum eadem dioecesi vel eodem officio); extra cum Human Lineage (candidatus quem tabula ipsa univocum declarat,
      temporibus congruentibus; inde Wikidata et HLS), cum SSRQ et indice Campi Regis (forma nominis exacta, unus candidatus, tempus
      congruens); loca cum Campo Regis et Wikidata (nomen exactum, locus in CH/FR/IT/DE; HLS per numerum); dioeceses per indicem
      fixum adiectivorum Latinorum. Effectus: <a href="register.html">Index</a>. Experimentum in 40 litteris infra ut initium
      manet.`,
    "m.read.example": "Exemplum iuxtapositum", "m.read.view": "Imaginem videre", "m.read.half": "Dimidia pagina",
    "m.read.left": "sinistra", "m.read.right": "dextra", "m.read.dev": "discr.", "m.read.trunc": "abrupta",
    "m.h.ner": "Nomina et index (experimentum)",
    "m.ner": `qwen3.8 ex {tested} litteris fortuito electis personas (cum munere, officio, dioecesi), loca, instituta, dies
      extraxit, addito summario unius sententiae. Effectus: <a href="register.html">Index (experimentum)</a>.`,
    "m.ner.shows": "Quid experimentum ostendat (machinaliter probatum, non cum imagine collatum):",
    "m.ner.1": `<strong>Copia sufficit:</strong> {persons} personae, {places} loca, {institutions} instituta, mediocriter {secs}
      secundae in singulas litteras. Beneficia, dioeceses, parochiae bene eruuntur (exempli gratia Andreas Karoleti,
      capellanus in Seysiriato, dioecesis Lugdunensis).`,
    "m.ner.2": `<strong>Normatio anceps est:</strong> «monasterii Sancti manner agavensi» recte in monasterium Sancti Mauricii
      Agaunensis vertitur, «abbati morii Loncedi» autem temere in «Cluniacum». In {np} personis, {nl} locis, {ni} institutis
      forma «ut scripta» non ad verbum in textu exstat; plerumque nomina sunt trans finem versus coniuncta, interdum ficta
      («Felix V»).`,
    "m.ner.3": `<strong>Notae registrationis in personas vertuntur:</strong> «ep̄us Brosseran», «Jo. Benenati» ut personae
      litterae vel etiam ut dioecesis apparent. {other} personis munus «other» datum est. Hi scriptores in campum proprium
      pertinent.`,
    "m.ner.4": `<strong>Dies in contextu</strong> machina saepe perperam convertit (exempli gratia 1449 pro 1440). Dies igitur
      tantum ex clausula datae et regulis infra positis sumuntur.`,
    "m.ner.assess": `<strong>Iudicium:</strong> ad inveniendum utile, ut index tantum tribus mutationibus factis: scriptores
      seiungendi, loca ad indicem dioecesium normanda, personae cum tabulis auctoritatis conferendae (SSRQ, HLS, Human
      Lineage). Meliore lectione (vide experimentum legendi) qualitas statim crescit.`,
    "m.h.seg": "Divisio per litteras et dies",
    "m.seg.entries": `<strong>Litterae (v1, ex regulis).</strong> Quodque exemplum regesti clausula datae finitur («Datum
      Basilee … pontificatus nostri anno …»), plerumque addita nota registrationis (numero et nomine scriptoris). Littera a
      fine unius clausulae usque ad finem sequentis pertinet. Clausula agnoscitur verbo «Dat(um)» vel loco datae, quem
      «nativitate / millesimo» sequitur. Altero signo etiam incipit («Felix episcopus …») sine clausula praecedente
      dividit.`,
    "m.seg.date": `<strong>Dies.</strong> qwen3.8 clausulam tantum in partes legit (locum, numerum ordinalem, kalendas/nonas/
      idus, mensem, annum, annum pontificatus). Diem mensis programma calculat: more Romano, anno a nativitate Domini
      incipiente; anni pontificatus: primus ab electione (die 5 Novembris 1439, «a die suscepti a nobis apostolatus
      officii») usque ad primum anniversarium coronationis, ceteri a coronatione die 24 Iulii 1440. Si annus pontificatus
      lectus cum die congruit, dies verisimilis habetur (✓); sin minus, inspiciendus est (⚠), plerumque ob errorem
      lectionis.`,
    "m.seg.th": ["Tomus", "Litterae", "cum die", "✓ annus pont.", "⚠ inspiciendum", "sine clausula datae"],
    "m.seg.next": `<strong>Gradus sequentes (v2).</strong> (1) Machina in singulis paginis binis versus nominat, quibus littera
      incipit vel qui datam continent; tantum quae a v1 discrepant, in indicem inspiciendorum referuntur. (2) Ordo temporum
      regestorum ad verisimilitudinem probandam adhibetur: dies a vicinis valde discrepans notatur. (3) Si Gemini vel Argon
      multo melius legit, divisio ex illa lectione renovatur. Fusius: <a href="https://github.com/thodel/felix_v/blob/main/PLAN.md">PLAN.md</a>
      (Theodisce).`,
  },
};

const MONTHS_L = {
  de: ["", "Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."],
  fr: ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
  la: ["", "Ian.", "Febr.", "Mart.", "Apr.", "Mai.", "Iun.", "Iul.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."],
};
