# Unterbaugruppen E07

Die Struktur bildet Montage und Wartung ab. Quelle ist `data/assembly_structure.json`; jedes vorhandene Teil muss genau einer Regel entsprechen. Unbekannte oder doppelt zugeordnete Teile brechen den Generator ab. E07 wird aus einer separaten Kopie des gesicherten E06-Archivs erzeugt. Geometrie, Bauteilnamen und native Feature-Historie bleiben erhalten; ganze Komponenten werden umgeordnet, nicht als neue Körper nachgebaut.

| Baugruppe | Inhalt | Montage-/Wartungsgrenze |
|---|---|---|
| OL-100 Gehäuse | Holzstruktur; feste Rückwand-Gewindeplatten und Holz-Halteschrauben; feste Elektronikstützen; Kabeldurchführungen | Bleibt bei Wartung bestehen. Die verleimte Schallwand gehört hierher. |
| OL-200 Frontbestückung | Tieftöner mit Gegenring und kompletter Verschraubung; Horn/Treiber und Hornbefestigung; Bassreflexrohr | Schallwand bleibt am Gehäuse. Untergruppen OL-210/220/230 lassen sich einzeln betrachten und prüfen. Das ist keine Behauptung einer gemeinsam entnehmbaren Frontplatte. |
| OL-300 Service-Rückwand | Rückwand, zehn lösbare Schrauben und Scheiben | Die Gewindeplatten und deren Halteschrauben bleiben am Gehäuse. Dichtung fehlt weiterhin als qualifiziertes Kaufteil. |
| OL-400 Elektronikmodul | Entnehmbarer Träger samt oberen Service-Schrauben; Verstärker/DSP mit Platinen-Abstandshaltern und Befestigern | Vor Entnahme Verkabelung lösen, obere Trägerschrauben entfernen. Untere Stützen bleiben am Gehäuse. Kabelschlaufen/Anschlüsse sind noch offen. |
| OL-500 Kabelbaum | Interne DC-, LF- und HF-Leitungen | Fest eingebaute Durchführungen sind im Gehäuse. Klemmen, Clips und reale Endkontakte sind noch zu ergänzen; keine abgeschlossene Kabelkonfektion behaupten. |
| REF-900 Referenzräume | Ausgeblendete alte Verstärkerreserve und Komponenten-Freiraum | Keine physischen Kaufteile; ausdrücklich aus der Einkaufs-BOM ausgeschlossen. |

Gehäuse untergliedert sich in OL-110 Holzstruktur, OL-120 feste Rückwandgewinde, OL-130 Elektronikstützen und OL-140 Durchführungen. Elektronikmodul in OL-410 Träger und OL-420 Verstärker/DSP.

Akkuversorgung OL-600 und Schutz/Tragen OL-700 sind im Strukturdatensatz als **geplant, nicht modelliert** geführt. Es werden keine leeren CAD-Baugruppen als fertig konstruierte Module ausgegeben. Akku-/BMS-/Laderauswahl, Horn-Treiber-Verbindung, Dichtungen, Gitter, Griff und fertige Ecken bleiben offene Konstruktion.

Die bisherigen Bauteilnamen bleiben zur Rückverfolgung erhalten. Baugruppen haben eigene Teilenummern OL-xxx. E05/E06-Herkunft im Namen ist eine Revision des erzeugenden Teils, keine separate physische Baugruppe. In neuen Skripten Komponenten rekursiv mit `root.allOccurrences` beziehungsweise `assemblies.leaf_occurrences(root)` suchen; `root.occurrences` enthält in E07 nur noch Baugruppen.

## Prüfungen und Reproduktion

1. `python -B tools/reproduce.py` – Rechenquellen/Tests/Ergebnisse.
2. `python -B tools/fusion_bridge.py run hardware/mechanical/prepare_assemblies_e07.py` – neue Kopie und E06-Referenzinventar. Bei schon geöffnetem E07 nicht nochmals importieren.
3. `python -B tools/fusion_bridge.py run hardware/mechanical/organize_assemblies_e07.py` – jede Komponente genau einmal umordnen.
4. `python -B tools/fusion_bridge.py run hardware/mechanical/verify_assemblies_e07.py` – Namen/Körper/Volumen/Lage/Parameter mit Baseline vergleichen, native Breitenänderung und Rücksetzen prüfen, Timeline prüfen und Exporte erstellen.

Danach tatsächliche STEP-/F3D-Rückimportprüfung ausführen. Erfolgreiche Hierarchieprüfung ersetzt keine neue Passungs-, Elektrik-, Sicherheits- oder Wetterfreigabe. Native Features bleiben parametrisch; die aus JSON regenerierten E05/E06-Basisgeometrien werden durch Umordnen nicht plötzlich live-parametrisch. Das Modell ist keine kinematische Gelenksimulation.

`python -B tools/fusion_bridge.py run hardware/mechanical/check_exports_e07.py` prüft das native Archiv einschließlich Hierarchie und Parameter, den Gesamt-STEP und fünf separat exportierte physische Hauptbaugruppen. Der Gesamt-STEP enthält245physische Hüllkörper; das native Modell zusätzlich zwei ausgeblendete, nichtphysische Referenzkörper. Der erste Rückimportvergleich entdeckte diese Differenz; der Prüfer vergleicht deshalb ausdrücklich die physische Teilmenge und verschweigt keine verlorenen Körper. Ergebnisse in `export_validation.json`; bei Fehlschlag kein erfolgreicher Gesamtstatus.

`python -B tools/generate_assembly_bom.py` aggregiert die Modellmengen je Unterbaugruppe und Artikelreferenz. Die native Fusion-Datei und die Gesamtansicht unter `exports/E07/` enthalten die vollständige Struktur; einzelne STEP-Dateien liegen unter `exports/E07/subassemblies/`. Fertigungszeichnungen aus E05 bleiben geometrische Vorentwürfe und werden durch diese Umstrukturierung nicht automatisch vollständig bemaßt.

`assembly_parts.csv` enthält die vollständige Zuordnung, `assembly_bom.csv` die Baugruppenzugehörigkeit mit bekannten Artikelreferenzen und Kennzeichnung nichtphysischer Reserven. Fehlende Beschaffungsdaten bleiben offen; diese Struktur-BOM ersetzt noch keine vollständige Einkaufsliste mit Endkundenpreisen.

Abschließender Dateiaudit: `python -B tools/check_assembly_outputs.py`. Er prüft vollständige Zuordnung/Mengen, vorhandene native/STEP-Prüfberichte, sechs STEP-Dateien und Quell-/Artefakthashes. Baugruppenansichten mit `capture_assemblies_e07.py`; Sichtbarkeit wird danach wiederhergestellt.
