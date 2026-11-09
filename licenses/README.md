# Lizenzentscheidung vorbereiten

Publikationsstand E05: Der vom Nutzer hochgeladene Forschungsbericht bleibt lokal erhalten, wird mangels dokumentierter Weitergaberechte per .gitignore vom Push ausgeschlossen. Keine fremden Hersteller-PDFs oder CAD-Dateien werden mitveröffentlicht. Die eigenen vereinfachten Referenzmodelle, CAD-Tessellierungen, Zeichnungen und Berechnungen sind entsprechend als eigene Ableitungen aus verlinkten Fakten markiert. Der Bericht muss für eine erneute Quellenlektüre separat vom Rechteinhaber bereitgestellt werden; die Rechengeneratoren verwenden die eigenen strukturierten Parameter und benötigen die PDF nicht zur Ausführung.

Werkzeuge für die neuen Zeichnungen: Python-Standardbibliothek; Autodesk Fusion für native Geometrie/Tessellierung, lokal installierter Microsoft Edge für SVG/HTML→PDF und pypdf für tatsächliche Seiten-/Textprüfung. Diese Anwendungen/Bibliotheken werden nicht gebündelt. PDF-/SVG-Prüfblätter sind noch keine freigegebenen Fertigungszeichnungen. Keine neue Lizenzentscheidung getroffen.

Die vorhandene Root-LICENSE enthält Apache-2.0 und bleibt unverändert. Der Forschungsbericht schlägt Hardware CERN-OHL-W-2.0, Code MIT und Dokumentation CC BY 4.0 vor. Das kollidiert potenziell mit einer pauschalen Interpretation der bestehenden Repositorylizenz. Rechteinhaber müssen Geltungsbereich und Neulizenzierung entscheiden; hier wird keine zusätzliche Lizenz erteilt.

| Gruppe | Vorzubereitende Wahl | Status |
|---|---|---|
| Eigene CAD-/Schaltplanquellen | CERN-OHL-P/W/S-2.0 vergleichen, Offenlegungspflicht festlegen | offen |
| Eigener Code | vorhandenes Apache-2.0 fortführen oder Rechteinhaber entscheidet über MIT | offen |
| Eigene Anleitung / Messgrafiken | CC BY 4.0 prüfen | offen |
| Nutzer-PDF mit Dateianlagen | Urheber und Weitergaberechte dokumentieren | keine Veröffentlichung vor Klärung |
| Herstellerdaten | Faktenauszüge mit Quelle; Datenblätter/CAD nur verlinken | keine fremden Dateien übernommen |

Abhängigkeiten: Generator und Tests nur Python-Standardbibliothek (Python/PSF-Lizenz). Optionaler PDF-Extraktor pypdf 6.12.0 (BSD-3-Clause laut Paket, vor Distribution prüfen), lokal ignoriert; NumPy/SciPy waren vorhanden, werden nicht benötigt. SigmaStudio, REW, FreeCAD und weitere Werkzeuge noch keine eingebundenen Projektabhängigkeiten. Gekaufte Module bleiben Fremdprodukte; deren Firmware-/DSP- und Dokumentationsrechte sind separat zu prüfen. Keine Behauptung einer quelloffenen Modulfirmware.

Referenzen aus Bericht: https://ohwr.org/licences/ , https://opensource.org/license/mit , https://creativecommons.org/licenses/by/4.0/ . Lizenztexte und SPDX-Zuordnung erst nach Entscheidung vollständig ergänzen.
