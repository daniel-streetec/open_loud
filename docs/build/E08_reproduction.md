# E08 – ausgeführte Montageergänzung und Reproduktion

**Nachfolgende Ausbauprüfung hat E08 gesperrt:** Trotz statischer Null-Überschneidung trifft der Akku bei5mm geradem Rückwärtsauszug auf feste Gewindeplatten. Keine Fertigungsfreigabe. Eine aufrechte90°-Drehung und22mm-Anhebung mit geänderter Kammer/Träger/Durchführungen ist als E09-Studie rechnerisch und an46 temporären Kernelpositionen bis225mm geprüft; aktive E08-Konstruktion wurde dabei nicht geändert. Quellen `data/experiments/E09_packaging.json`, `results/service/packaging_comparison.json`, `results/service/E09_battery_service_study.json`. Terminalspektrum14mm und2mm Flächenzugabe sind Annahmen. Plattform, Halter, Kabel und Verpolschutz müssen im echten Folgemodell konstruiert werden.

Stand 2026-11-10, nach dem ersten E08-Checkpoint. Die Ladebuchse hat einen eigenen Halter und vollständige Schraubengegenstücke. Zwei anfängliche Halter-/Scheibenprobleme wurden behoben. Am Orion wurden die Montageohren anhand des offiziellen STEP geprüft: 2 mm, nicht bisher angenommene 3 mm. Vier zylindrische Werkzeugräume Ø8 mm von 2 bis 15 mm über der Montagefläche wurden gegen das Hersteller-CAD auf Überschneidung geprüft. Die publizierte eigene Hülle nutzt nur diese nachgewiesenen Freiräume; Herstellerflächen wurden nicht übernommen.

Aktuelle `power_validation.json`: **0 Überschneidungen im definierten Prüfumfang, 0 Kernel- und 0 Timelinefehler**. Das bedeutet keine vollständige Produktfreigabe: gleiche Komponente, Gurte/Schnallen und Referenzräume sind ausgeschlossen; fehlende Kabelenden, Halter und Schutzteile können nicht geprüft werden. Reale Toleranzen, Montagerichtung, Schraubensicherung und thermische Qualifizierung fehlen. Diese Prüfung wurde nach der Baugruppenaufteilung erneut ausgeführt.

## Befehle für diese Ergänzung

Ausgangspunkt: vorhandenes flaches E08-PowerSystem-Dokument bzw. dessen letzter F3D-Checkpoint. Ältere Erzeugungsschritte stehen in `docs/NEXT_SESSION.md`. Fusion über den lokalen MCP auf Port27182.

```powershell
python -B tools/setup_connection_mounts_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/add_charge_bracket_e08.py
curl.exe -L --fail --max-time 30 'https://www.victronenergy.com/upload/documents/Orion-Tr-110W-120W-Isolated-%28stp%29.STEP' --output .tools/references/orion-small.step
python -B tools/fusion_bridge.py run hardware/mechanical/inspect_vendor_orion.py
python -B tools/record_orion_verification.py
python -B tools/fusion_bridge.py run hardware/mechanical/refine_orion_mount_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/verify_power_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/view_power_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/check_exports_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/inventory_mass_e08.py
python -B tools/draw_charge_bracket_e08.py
python -B tools/reproduce.py
```

Die jetzt ausgeführte Baugruppenstufe folgt **nach** den flachen Ergänzungsskripten:

```powershell
python -B tools/prepare_assemblies_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/organize_assemblies_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/verify_assemblies_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/verify_power_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/inventory_mass_e08.py
python -B tools/generate_modeled_bom_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/view_power_e08.py
python -B tools/fusion_bridge.py run hardware/mechanical/check_exports_e08.py
```

225 physische und referenzierende Teile sind 22 Gruppen eindeutig zugeordnet; Einzelvolumina und Platzierungen sind gegen den flachen Stand geprüft. Acht Hauptgruppen einschließlich separatem externem Ladegerät. Die Wandlergruppe BG43 wird unabhängig vom Träger BG41/BG42 gewartet; vier Trägerschrauben lösen nicht zugleich den Wandler. Konstruktionsergänzungsskripte mit flacher `root.occurrences`-Suche nach dieser Stufe **nicht blind wiederholen**: für einen Neuaufbau die dokumentierte Reihenfolge ab dem flachen E08 ausführen oder die neue Ergänzung bewusst baugruppenfähig schreiben.

`results/power/E08/modeled_bom.csv` ist eine tatsächlich aus dem CAD-Inventar erzeugte Liste mit65 Positionen;58 Einheitskosten sind noch unbekannt. Modellkörper, Kabelrouten und Gurt-Unterteile sind keine ungeprüft zu kaufenden Einzelpositionen. Fehlende Teile werden im JSON explizit aufgelistet. Keine vollständige Einkaufsliste oder Gesamtpreisbehauptung daraus ableiten.

STEP-Datei ausschließlich lokal unter ignoriertem `.tools/`; Herkunft und SHA256 unter `data/verification/orion_mount.json`. Bei geändertem Herstellerdateihash die Prüfung neu beurteilen. Keine pauschale Weitergabeberechtigung unterstellen.

`charge_bracket_review.pdf` und SVG unter `hardware/mechanical/drawings/E08/` sind bemaßte Montageprüfblätter mit echten Koordinaten aus der Parameterbasis. PDF-Seitenzahl und Text wurden automatisiert geprüft, das gerenderte Blatt zusätzlich visuell betrachtet. Es ist keine freigegebene Blechabwicklung; Material/Biegeradius fehlen noch. Edge, Poppler und lokal verfügbares pypdf sind für PDF-Erzeugung und Prüfung nötig; stdlib-Rechnungen bleiben davon unabhängig.

## Weiterer Arbeitsumfang

Verpolschutzvorauswahl siehe `reverse_protection_E08.md`; noch nicht im CAD und Strompfad eingebaut. Reale Klemmenhalter, Zugentlastungen, Sicherungsbefestigungen und Gurtanker bleiben offen. Danach volle Netzliste, geregelte Versorgung mit Schalter und Schutzmodul, Wärmeabfuhr, Montageauszug, E08-Baugruppen, vollständige BOM, Zeichnungen und Akustik-/DSP-Absicherung. Die frühen 300-EUR-/10-kg-Ziele müssen gegen den jetzt wesentlich größeren Akku explizit neu bewertet werden.
