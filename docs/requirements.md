# Bestandsaufnahme und Anforderungsextraktion

Stand 2026-11-09. Alle 17 Seiten des Phase-1-Berichts sowie die eingebetteten Dateien `modell.py` und `stueckliste.csv` wurden gelesen. Anlageninventar: zusätzlich `lf_modell.csv`, `nutzwert.csv`, `quellen.tsv`, `Content Credentials`. Diese weiteren Anlagen sind inventarisiert, noch nicht inhaltlich auditiert. Kein fremder Code wurde ausgeführt oder übernommen. Keine AGENTS.md oder weiteren Projektanweisungen im Checkout oder den geprüften übergeordneten Verzeichnissen gefunden. Git-Ausgangsstand `f3e4196`, Branch main; anfangs nur LICENSE versioniert, Bericht vom Nutzer hinzugefügt.

## Anforderungen aus Nutzerauftrag

Reproduzierbares Entwicklungspaket; zentrale Parameter mit Einheiten/Quellen/Unsicherheit; Primärquellenprüfung; mindestens zwei Gesamtkonzepte; ausführbare Akustik samt Hub/Port/elektrischen Grenzen; Lastszenarien und Energie; anschließend parametrische CAD- und Fertigungsdaten; strukturierte vollständige BOM; Montage und messbare Abnahme; getrennte Lizenzvorbereitung; nachvollziehbare Entscheidungen. Vorläufige Modelle gelten nicht als Messung oder Freigabe.

## Ziele aus Forschungsbericht (noch keine nachgewiesenen Eigenschaften)

| ID | Ziel / Planungsansatz | Fundstelle |
|---|---|---|
| R01 | Aktive Mono-Box, zwei Wege, 10 Zoll + Horn, reparierbar | S. 1, 4, 9 |
| R02 | A0 Materialziel 300 EUR; vollständiger Warenkorb bisher darüber | S. 1, 11, 14 |
| R03 | A1 erster Bau inklusive Programmer höchstens 500 EUR | S. 14 |
| R04 | A0 höchstens 10 kg; A1 höchstens 11 kg | S. 14 |
| R05 | A0 F6 höchstens 63 Hz; A1 höchstens 52 Hz, bei moderatem Pegel | S. 14 |
| R06 | A1 mindestens +2 dB bei 50 Hz gegenüber A0 unter gleichen Messbedingungen | S. 14 |
| R07 | 100 Hz–10 kHz auf Achse ±3 dB, 1/6-Oktavglättung; bis ±30 Grad H kein zusätzlicher Einbruch >5 dB zwischen 1–4 kHz | S. 2 |
| R08 | 34 l netto; ungefähr H/B/T 520/330/300 mm, 12 mm Multiplex | S. 12, vorläufiger Bauraum, kein verbindliches Größenmaximum |
| R09 | Historischer Berichtsvorschlag: 18-V-/4-Ah-Werkzeugakku, 72 Wh. Vom Nutzer zur Neubewertung gestellt; nicht mehr bevorzugte Versorgung | S. 10; Nutzerkorrektur 2026-11-09 |
| R10 | Elektronik getrennt, Wartungszugang, Tragen mit Gegenplatten, Regenabweisung | S. 12 |

Ein Mindestlaufzeitziel und ein verbindlicher absoluter System-Maximalpegel sind nicht festgelegt. Die vier Lastprofile auf S. 10 sind Modellannahmen, keine Laufzeitanforderung. Die Tabelle auf S. 1 nennt A1 10–12 kg, das spätere Ziel ist ≤11 kg: Ziel und Prognose getrennt führen. Die 500-EUR-Grenze enthält einen Programmer, das 300-EUR-Materialziel nicht (S. 11/14); Messgeräte und Entwicklungskosten jeweils separat.

## Annahmen

Nutzerkorrektur zur Versorgung (2026-11-09): Die bisherige **andere** Box hält mit12V/100Ah-LFP locker ein Festival Mittwoch–Sonntag einschließlich zusätzlichem Handyladen durch. Das ist der praktische Vergleichsfall, keine Messung dieses Entwurfs und keine bekannte Zahl kontinuierlicher Musikstunden. Nutzer bezweifelt Nutzen/Preis kleiner Werkzeugakkus und bevorzugt keine Bosch-Pro-Festlegung; fertige Akkublöcke und prismatische Zellen samt vollständiger Schutz-/Ladekette neu vergleichen. **USB/Handyladen ist ausdrücklich KEINE Anforderung**, nur eine mögliche spätere Option. Laufzeitberechnung der Basisbox ohne USB. Kapazitätsentscheidung bleibt bis zum Nutzungs-/Lastvergleich offen. Siehe data/battery_study.json und results/battery/comparison.md.

Alle metrischen Schrauben müssen ein konstruiertes Gegenstück und nachgewiesenen Zugang besitzen (Mutter, Gewindeplatte, geeignete Gewindemuffe/Einschlagmutter). Nicht unmittelbar ins Holz einschrauben. Schraubenverbindungen vollständig in CAD, Montagefolge und BOM führen; konkrete Einkaufsmengen für Endnutzer.

A0 als reversible Rechenreferenz, A1 als Bassversuch; keine endgültige Auswahl. Idealer Halbraum, kalte Kleinsignalparameter, Ql=7 und Qp=20 sowie Port-Peak 17 m/s aus Bericht S. 7–8. Verlust- und Energieannahmen bleiben ungemessen. Fehlende Herstellertoleranzen werden als unbekannt geführt, nicht als Nullunsicherheit.

## Offene Entscheidungen

Aktualisierung durch Nutzer am 2026-11-09: Mehrgewicht ist zulässig, wenn es wesentliche Qualitätsvorteile bringt. Stabilität an Ausschnitten und Montierbarkeit sind ausdrücklich zu berücksichtigen. Die bisherigen 10/11-kg-Ziele sind damit Vergleichswerte statt harter Ausschlussgrenzen. Ein neues Gesamtgewichtsmaximum wurde nicht festgelegt. E03 untersucht daher 24-mm-Schallwand und 560 mm Höhe; kein stillschweigender Nachweis der früheren Gewichtsziele.

Weitere Nutzerkorrektur 2026-11-09: Keine überdimensionierte Außenverkleidung, selbst zusammengesetzten Blechecken, frontseitige Spritzhaube oder klobigen Kabelauslass. Der E04-Außenversuch wurde zurückgenommen; E03 ist wieder sichtbare CAD-Basis. Kantenschutz nur als passend geprüftes fertiges Kaufteil.

Beschaffung ist ein Freigabekriterium: Standardteile bevorzugen, für Privatkunden in Deutschland/EU ohne exklusiven B2B-Zugang erhältlich, einzeln oder in sinnvollen Kleinmengen. Keine Großverpackungen als Nachbauvoraussetzung. Für jedes Kaufteil konkrete Endkundenquelle, Bestellmenge, Bruttopreis und Versandbedingungen mit Datum prüfen; Herstellerdaten allein sind kein Beschaffungsnachweis. Ungeprüfte Kandidaten bleiben ungeprüft. Eigene DIY-Fertigungsteile bleiben m?glich, wenn technisch n?tig und nachvollziehbar herstellbar; sie d?rfen nicht als leicht beschaffbare Standard-Kaufteile ausgegeben werden. Industrielle Gro?verpackungen sind keine zul?ssige Nachbauvoraussetzung.

Kein Nutzerentscheid blockiert die erste Rechnung. Vor Bestell-/Baufreigabe: Budgetumfang bestätigen, falls neue Preise das Ziel überschreiten; Hornübergang messen; Akku-Schutz am Fremdadapter belegen; genaue Modulrevision/Spannungsfreigabe und UVLO spezifizieren. Laufzeitziel vor Optimierung am gemessenen Nutzpegel bestimmen. Lizenzentscheidung beim Rechteinhaber belassen.

## Werkzeuge und Datenlücken

Windows PowerShell; Git verfügbar, Sandbox meldet abweichenden Eigentümer. Lesender Workaround nur pro Aufruf: `git -c safe.directory=C:/Repositories/open_loud ...`, keine globale Git-Konfiguration geändert. Python 3.13.7, NumPy/SciPy vorhanden; Matplotlib, pytest, CadQuery und die geprüften Befehle FreeCAD/OpenSCAD fehlen. Poppler `pdftotext` vorhanden: lieferte zunächst über mehrere Abfragen keine Ausgabe, bei späterer Abfrage vollständigen Text mit Exit 0; daher doch nutzbar. pypdf 6.12.0 nach Netzwerkfreigabe in `.tools/python` installiert, dort für Sandbox nicht lesbar; PDF-Lektüre gelang mit freigegebenem Python-Aufruf und `-X utf8`. Rechenpaket bewusst nur mit Standardbibliothek.

Keine gemessenen T/S, FRD/ZMA, Polaren, DSP-Projekte, Schutzschaltung, mechanisch geprüften Einbaumaße oder Pack-Innenwiderstände vorhanden. Kein CAD-Export erzeugt oder als geprüft bezeichnet. Rechte an PDF und eingebetteten Anlagen nicht dokumentiert: Veröffentlichung bis Rechteklärung zurückstellen.
