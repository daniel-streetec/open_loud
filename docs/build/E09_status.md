# E09 – Wartungsraum und elektrische Auslegung

E09 ist eine separate Entwicklungsrevision, noch kein vollständiges Produkt. E08 bleibt als dokumentierter Fehlerstand erhalten: statisch passend, aber der Akku kollidierte beim Wartungsauszug schon nach5mm mit festen Gewindeplatten.

## Parameter und Konstruktion

Gemeinsame Eingabebasis für E09-CAD, Verkabelungs- und Versorgungsrechnung ist `data/experiments/E09_parameters.json`. Sie wird durch `tools/prepare_e09_cad.py` aus dem eingefrorenen E08-Stand und versionierten E09-Entscheidungen erzeugt. Die weiterhin vorhandene `data/parameters.json` ist **E08**, nicht unbemerkt mit dem neuen Modell verwechseln. E09 liegt bewusst separat, bis der vollständige Aufbau qualifiziert ist.

Der aufrechte50Ah-Akku ist in der Draufsicht90° gedreht und22mm angehoben. Zwei25mm hohe Holzauflagen sitzen direkt auf dem Gehäuseboden; darauf3mm Pad. Kammer bis240mm Höhe mit zusätzlicher rechter Trennwand. Der Elektronikträger misst180×102×2mm, das JAB-PCB ist nach hinten versetzt. Durchführungen, Sicherungshalter, Wandlerlage und Kabelwege sind angepasst. Der interne Ladebuchsenhalter ist34mm breit, sein Fuß29,9mm tief; alle M3-Verbindungen haben echte Gegenstücke. Material/Biegeradius und mechanische Prototypfreigabe bleiben offen.

228 Teile sind22 Gruppen zugeordnet. Der Wandler wird unabhängig vom JAB-Träger gewartet. Noch keine reale Bestückungsplatine nachgebaut: JAB3+ bleibt das gekaufte WONDOM-Modul. Kaufteile sind eigene, gekennzeichnete Maßhüllen; das Hersteller-STEP des Orion wurde nur lokal zur Passungsprüfung benutzt.

Die nominale Ausbauprüfung wurde bis225mm gerechnet. Zusätzlich prüft `check_battery_envelope_e09.py` den **durchgehenden rechteckigen Bewegungsraum** bis227mm: seitliche2mm-Zugabe, zusätzliche14mm Polreserve plus2mm obere Zugabe, die untere Padfläche als Auflagedatum. Der Box-Sweep ist für eine achsparallele Verschiebung geometrisch exakt. Seine Eingabehülle ist eine Annahme und kein vermessenes Akku-/Polmodell. Der jeweils tatsächliche Ergebnisstatus steht in `exports/E09/battery_continuous_envelope.json`; nicht allein aus der Existenz dieses Skripts auf Erfolg schließen.

## Versorgung und Klangrechnung

Die alte Rechnung mit4-/8-Ohm-Nennlast war kein ausreichender Last-Worst-Case. E09 berücksichtigt LF mit0,9×nominalem Re als Sensitivität, HF mit dokumentierten6,3Ohm Mindestimpedanz, warme Kabel, Kontaktbudgets, geplanten Verpolschutzverlust und konstante Leistungsaufnahme bei Spannungseinbruch. Die0,9-Re-Annahme ist keine zertifizierte Bauteiltoleranz.

Vorläufige Ziele: LF10,5Vrms, HF10Vrms;20V Wandlerausgang. Daraus konservativ56,71W Audio-Lastgrenze,89,65W benötigte Wandlerausgangsleistung und etwa10,35% Reserve zur100-W-Planungsgrenze. Bei10V am Akku ergeben sich rund11,55A und9,77V am Wandler. Diese Limiter sind **nicht aufgespielt oder kalibriert**. Geplanter Pololu5389 ist weiterhin nicht verbaut; sein warmer Widerstand ist nur als Verlustreserve berücksichtigt.

Thermik ist ein echter Entwicklungsblocker: rund23,2–23,6W geschätzte Wandlerwärme im konservativen Dauerlastfall, dazu etwa32,3W Verstärkerwärme bei der angenommenen65%-Effizienz. Keine ausreichende Wärmeabfuhr der geschlossenen Holzkammer nachgewiesen. Ein niedrigerer Musikmittelwert entbindet nicht von der Spitzen-/Dauerlastprüfung. Keine ungedichteten Lüftungslöcher als ungeprüfte Spritzwasserlösung hinzufügen.

Offline-DSP-Vorschlag: Butterworth4-Hochpass40Hz, elektrischer LR4-Übergang2,5kHz nach DE10-Herstellerempfehlung. Im linearen LF-Modell: etwa3,14mm Spitzenhub gegenüber4,62mm geometrischer Xmax-Referenz,8,87m/s maximale Portgeschwindigkeit undF6≈61Hz relativ180–250Hz. Das ist eine Näherung ohne Parameterstreuung, Nichtlinearitäten, Hornmessung, Schallwand/Polaren oder kalibrierten Pegel. Keine akustisch abgestimmte Gesamtfrequenzgangkurve behaupten. Allgemeine Float-Biquads sind weder SigmaStudio-Image noch geprüfte ADAU1701-Parameterdatei.

`results/dsp/E09/LF_protection.pdf`, SVG und PNG sind tatsächlich mit Matplotlib erzeugte wissenschaftliche Plots. Zwei erneute Renderdurchläufe waren byte-identisch; PDF-Seite/Text und gerendertes Bild wurden geprüft. Neue unabhängige Tests decken Filter-Referenzformeln und Energieerhaltung über beide Leitungsstrecken ab.20 Tests bestanden.

## Weiterarbeit

Zuerst komplette lösbare Batterieanschlüsse samt packnaher Sicherung, Ringösen-/Polschutz, Zugentlastungen und echten Klemmenhaltern ausarbeiten. Auswahl und Endkundenangebote für XT90S-Serviceverbinder und fertige AdamHall4072-Ecken siehe `service_connections_E09.md`; noch nicht modelliert. Für Tragepunkte, Gurtanker, Horn-Treiber-Verbindung, Verpolschutz und Schalter fehlen ebenfalls endgültige Montagedetails. Akku-Polkoordinaten, BMS-Fehlerstromdaten, Sicherungskoordination und Kühlung bleiben Prüfpflicht.

Das bisherige Holz ist deutlich zu schwer für das frühe10kg-Ziel. Die neue Kammer erhöht die Holzmenge auf etwa16,59L; selbst vor Metall/Kabeln/Gitter/Tragen liegt die Teilmasse deutlich darüber. Material-/Massenoptimierung ist als Nächstes nötig, ohne Schallwandausschnitte oder Trage-/Akkuanker zu schwächen. Bekannte HF-/Hornmassen werden in der aktualisierten Inventur zusätzlich eingerechnet. Keine komplette Stückliste oder finalen Produktpreis aus der Modell-BOM ableiten.

## Reproduktion

```powershell
python -B tools/prepare_e09_cad.py
python -B tools/calculate_harness_e09.py
python -B tools/calculate_supply_e09.py
python -B tools/calculate_dsp_e09.py
python -B tools/reproduce.py
python -m pip install --target .tools/python -r tools/requirements-visual.txt
python -B tools/check_plot_reproduction_e09.py
python -B tools/draw_charge_bracket_e09.py
```

CAD-Neuaufbau in ein **neues leeres** E09-Dokument: `build_case_e09.py`, dann über `tools/run_e09_stages.py` nacheinander rear/fasteners/power/electronics/charge/orion/harness. Anschließend Prüfreports wirklich lesen: Skripterfolg ist keine geometrische Freigabe. Nach Korrekturen die Baugruppen mit `prepare_e09_assembly_stages.py`, `prepare_assemblies_e09.py`, `organize_assemblies_e09.py` erzeugen; nur einmal reparenten. Danach Inventur, Baugruppenprüfung, statische Kernelprüfung, durchgehenden Akku-Sweep und native/STEP-Rückimporte ausführen. Charge-Halter-Updates unterstützen inzwischen verschachtelte Baugruppen und prüfen Lösch-Rückgabewerte; alte flache Ergänzungsskripte nicht blind im gruppierten Modell wiederholen.
