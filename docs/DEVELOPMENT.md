## E08 – Montagehalter und Baugruppen geprüft, 2026-11-10

**Neu erkannter Montageblocker:** Der echte E08-Akku stößt beim geraden Wartungsauszug schon bei5mm an feste Gewindeplatten. Bericht `exports/E08/battery_service_validation.json`. E08 deshalb nicht fertigen. E09-Vorschlag in `data/experiments/E09_packaging.json`: aufrecht um90° gedrehter,22mm angehobener Akku, angepasste Kammer/Plattform/Träger und verlegte Durchführungen. Temporärer Kernelversuch mit2mm zusätzlichem Hüllraum pro Fläche und14mm Polreserve:46 Positionen bis225mm Auszug ohne Treffer (`results/service/E09_battery_service_study.json`). Dies ist eine geprüfte Studie, noch kein gebautes E09-CAD. Als Nächstes vollständig umsetzen, dann sämtliche Anschluss-/Montageprüfungen wiederholen. Kein bloßes Null-Kollisions-Ergebnis mit Montierbarkeit verwechseln.

Neuester Stand ersetzt die unmittelbar folgenden historischen E08-Notizen: Ladebuchsenhalter mit M3-Durchsteckmontage ergänzt, dazu bemaßtes eigenes PDF/SVG-Prüfblatt. Offizielles Orion-STEP lokal importiert, 2-mm-Montageohren und vier freie Ø8-mm-Werkzeugräume geprüft. Daraus eigene konservative Hülle korrigiert; keine fremden Solids publiziert. `data/verification/orion_mount.json` und `licenses/external_material_E08.json` enthalten Herkunft/Hash und Umfang.

225 Teile in22 eindeutig geprüften Gruppen; Einzelvolumina/Platzierungen unverändert. Acht Hauptgruppen einschließlich Akku und externem Ladegerät. BG43-Wandler ist unabhängig von BG41/BG42-Träger zu warten. Aktuelle Kernelprüfung nach Reparenting:0 Überschneidungen im dokumentierten Umfang,0 Kernel-/Timelinefehler; keine vollständige Montierbarkeits- oder Produktfreigabe. F3D-/STEP-Rückimporte bestanden und Fusion gespeichert. Neuaufbau-/Prüfreihenfolge in `docs/build/E08_reproduction.md`; flache Ergänzungsskripte nach Gruppierung nicht blind erneut aufrufen.

17 Rechentests und doppelte byte-identische Reproduktion bestanden. CAD-basierte Modell-BOM erzeugt:65 Positionen,58 Einheitskosten offen; keine vollständige Einkaufsliste. Wichtiger Zielkonflikt:17,02–18,60kg bereits für Holz/Akku/LF/Wandler, weitere Teile fehlen. Noch keine bestätigte leichte Holzplatte auswählen; Vergleich in `docs/build/material_mass_E08.md`. Vier Versorgungskaufteile bereits338,02EUR ohne Versand und Restprodukt. Frühe10kg/300EUR nicht erfüllt.

Prioritäten weiter selbstständig abarbeiten: reale Klemmenhalter/Zugentlastungen, Sicherungshalterbefestigung, Gurtanker, Polabdeckungen und vollständige Anschlussstellen; passende Schutz-/Schaltkette und Kühlung. Pololu5389 ist neue technische Verpolschutzvorauswahl, noch nicht eingebaut. EXP-Tech/Botland.store als geprüfte B2B-Quellen ausgeschlossen; Eckstein-Angebot mit Lieferlandhinweis noch verifizieren. Danach Material-/Massenoptimierung mit belastbaren Reststegen und Montagestellen, Kabelschlaufen/Extraktion, vollständige BOM/Zeichnungen/Explosionen und Akustik-/DSP-Absicherung. Alte Berichte bleiben historische Entwicklungsnachweise. Kein Scheduler aktivieren, keine neue Lizenz festlegen; weitere Arbeit und Push sind beauftragt.

## E08 – laufende Versorgungskonstruktion, 2026-11-10

E07 bleibt Rückfallbasis. Aktives Fusion-Dokument `OPEN_LOUD_A0_E08_PowerSystem` hat Akku/BMS-Hüllmodell, abgetrennte Batteriekammer, Orion-Wandler mit M3-Gegenstücken, externes Ladegerät, internen Ladeanschluss, Sicherungshalter, erweiterten Elektronikträger und fünf berechnete Kabelwege. Kein selbstgebauter Verstärker: WONDOM AA-JA32173. Details `docs/build/power_E08.md` und `data/procurement_E08.json`.

Ausgeführt: Aufbau Gehäuse/Rückwand/Schrauben → `add_power_e08.py` → `add_electronics_e08.py` → `add_harness_e08.py` → `refine_power_e08.py`. Geometrische Nacharbeit ist im letzten Skript enthalten. Zentraldaten vor Berechnungen mit `tools/refine_e08_packaging.py` aktualisiert. `python -B tools/reproduce.py`: 17 Tests bestanden und generierte Rechenergebnisse zweimal byte-identisch. Leistungs-/Laufzeitrechnung und 12 hypothetische Spannungseinbruchfälle unter `results/power/E08/`. Hypothetische Packwiderstände sind keine Herstellerdaten.

CAD-Prüfung `verify_power_e08.py` schreibt tatsächliche Kernelüberschneidungen nach `exports/E08/power_validation.json`, nicht als Erfolg umdeuten. STEP/F3D heißen bewusst `checkpoint`; noch kein E08-Rückimportnachweis. Alte `OPEN_LOUD_A0_E08.*` sind nur Gehäuse-Zwischenstand, nicht vollständiger Elektronikausbau. `view_power_e08.py` erzeugt aktuelle Schnittansicht und Austauschdateien. E08 ist derzeit noch flach; E07-Baugruppengliederung nach Ergänzung der Teile übertragen.

Weiterarbeiten, nicht auf Rückfrage warten: verbliebene Wandler-Hüllkonflikte an Montageohren anhand Primärzeichnung klären; reale Klemmenhalter, Kabelschellen, Gurtanker, Ladebuchsenhalter und Sicherungsbefestigung ergänzen; vollständige Anschlusskette mit Verpolschutz/Schalter qualifizieren. Pololu2815 wegen nur6Abei55°C nicht freigegeben. Akku-Polkoordinaten, WAGO-Halterlochpositionen, Kühlung (~20W konservative Wandlerwärme), Sicherungs-Abschaltvermögen und Leitungsdaten offen. Danach Montageauszug, Baugruppenhierarchie, Rückimporte, BOM/Zeichnungen/Explosionen/akustische Absicherung. Nicht fertig behaupten; kein Scheduler aktivieren. User will kontinuierliche eigenständige Bearbeitung und Push.

# Entwicklungsplan und Übergabe

Aktueller Abendstand2026-11-10: **E07-Unterbaugruppen umgesetzt und geprüft**, Details docs/build/assemblies.md.168Komponenten in fünf physischen Hauptbaugruppen plus Referenzräume,247native/245physische STEP-Körper. Vollständiger F3D-Hierarchie-/Parameter-Rückimport und Gesamt-/fünf Baugruppen-STEP-Rückimporte bestanden. Abstände/Geometrie gegenüber E06 unverändert, nativer10mm-Breitenänderungstest bestanden.16Python-Tests. Nutzer hat Arbeit wieder aufgenommen; sämtliche Wiederanlaufprozesse bleiben abgeschaltet. E05/E06-Abschnitte unten sind Vorgeschichte. Nächste technische Priorität bleibt Batterie-/Schutzarchitektur, vollständige Anschlussstellen und Kabelbefestigung auf Basis dieser Baugruppen.

Revision E05, 2026-11-09. Aktueller CAD-Stand: OPEN_LOUD / OPEN_LOUD_A0_E05_WiringFasteners. **Zuerst docs/NEXT_SESSION.md lesen**: dort neueste Nutzerkorrekturen, Wiederanlaufstatus und konkreter weiterer Arbeitsplan. E03 bleibt geprüfte Rückfallbasis; historische E03-Abschnitte unten nicht als neueste Übergabe lesen.

E05-Verkabelung berechnet,42Schrauben/34Scheiben/12Muttern mit Gegenstücken modelliert. Drei anfängliche Kabelkollisionen und zwei fehlerhafte Durchführungsbohrungen behoben; anschließende Kernelprüfung ohne Kabelkollision/Timelinefehler.204Solids, STEP/F3D-Rückimport bestanden und Fusion gespeichert. Vier neue Durchführungs-DXFs; Klemmenhalter, echte Anschlüsse, Wartungsschlaufen und Elektronikschutz bleiben offen. tools/reproduce.py führt auch Wiring-/BOM-/Festivalstudie aus.

Aktuelle höchste Priorität: Festivalversorgung ohne USB-Pflicht neu vergleichen, vollständige elektrische Schutz-/Ladekette und montagefähige Anschlussstellen qualifizieren; danach weitere Montageprüfung, Zeichnungssatz/Explosionen, Beschaffung und Darstellungen gemäß docs/NEXT_SESSION.md. Nutzer hat Commit/Push und Wiederanlauf nach Kontingentreset beauftragt. Keine Lizenzfestlegung oder Bestellung autorisiert.

Aktuelle Nutzerkorrektur: Der überladene E04-Außenversuch wurde verworfen und aus Fusion entfernt; siehe docs/review_E04_rejected.md. Keine selbstgebauten Blechecken, keine große Haube vor dem Port und kein klobiger seitlicher Kabelauslass wieder einführen. Zentrale Parameter stimmen wieder exakt mit dem geprüften E03-Hash überein. Die zwischenzeitliche E04-Studie ist unter data/experiments abgelegt und nicht freigegeben.

Beschaffungsgate: data/procurement_policy.json gilt für jede weitere Auswahl. Privatkundenbezug DE/EU, Standardteile, Einzelstücke oder sinnvolle Kleinmengen, Bruttopreis und Versand sowie aktuelle Lieferbarkeit belegen. Herstellerportal, industrieller Großpack und leerer Steckergehäuse-Datensatz genügen nicht. Zuerst konkrete passende Kaufteil-Ecken und einen kompakten Standardanschluss auswählen; keine neue Außenkonstruktion anhand bloßer Hüllräume erzeugen.

| Etappe | Status | Ergebnis / Prüftor |
|---|---|---|
| E01 Bestandsaufnahme | erledigt | Bericht vollständig gelesen, Anlageninventar, Anforderungen getrennt |
| E02 Parameter und erste Rechnung | ausgeführt und geprüft | Fünf analytische Tests bestanden; 4203 Frequenzzeilen geprüft; A0/A1 und geschlossene Kontrolle, Energiebandbreiten, generierte BOM; siehe results/validation.json |
| E03 Beschaffung / Versorgung verifizieren | teilweise | LF und ausgewählte HF-Primärquellen geprüft; Modulrevision, BMS am Adapter, Laderdetails und Sicherung offen |
| E04 Akustik absichern | offen | Toleranzen, unabhängige externe BR-Simulation, Mess-T/S, Schallwand/Polaren und DSP |
| E05 Parametrische Konstruktion | erster A0-Vorentwurf umgesetzt | Fusion: 24mm-Schallwand, Stahl-Gegenring, Rückleisten/-Gewindeplatten, Dichtnut, Volumenbuch; STEP/F3D/DXF erzeugt und geprüft. Akku, Gitter, Tragen, Kühlung, Schwerpunkt weiterhin offen |
| E06 Fertigung und Montage | offen | konkrete SKU-BOM, Zuschnitt, Montagefolge und elektrische Prüfungen |
| E07 Prototyp / Freigabe | offen | Prüfplan aus docs/build/validation.md; Rohdaten und Abweichungen |
| E08 Reproduktion / Lizenzentscheidung | offen | Zweitbau, Rechteinventar, Entscheidung pro Artefaktgruppe |

## Nächste Sitzung

Aktualisierung E03: zuerst hardware/mechanical/README.md und docs/build/mechanical_assembly.md lesen. Qualität vor Gewicht ist jetzt Nutzerpriorität. Bauraum 330×560×300 mm (B/H/T), 12-mm-Birkenmultiplex, 24-mm-Schallwand. Unbekannte Mehrkosten in data/mechanical_hardware.json, nicht als 368-EUR-Fertigungssumme ausgeben. Der Fusion-MCP-Server läuft unter localhost:27182/mcp; Health unter /health. Native und STEP-Rückimport sowie DXF-Prüfbericht unter hardware/mechanical/exports/E03/. Die sechs Python-Tests und tools/reproduce.py bleiben Einstieg für Akustik/Parameter.

Dringende nächste Arbeiten: realen LF-Korb gegen 220-mm-Gegenringöffnung und 24-mm-Schallwand prüfen; Horn-/Treibermaßblattrevision bestätigen; Werkzeugzugang mit Schrauben/Muttern und tatsächlichem Akku am Modell und Muster nachweisen; restliche Hardware konkretisieren, Masse/Kosten neu kalkulieren; Akkuhalter, Wartung am Port, Gitter und Tragebefestigung konstruktiv ergänzen. Der Verstärkerblock ist ein unbestätigter Installationsraum. Bestehendes E03-Dokument nicht durch ungeprüftes Neulaufen des Erstgenerators ersetzen.

1. README und dieses Dokument, requirements.md, decisions.md lesen. Tests und Generator laufen lassen.
2. PDF-Anlagen quellen.tsv und lf_modell.csv auditieren, Hashes über Extraktionswerkzeug sichern. Keine fremden Anlagen ohne Rechteklärung veröffentlichen.
3. Originalunterlagen für AA-JA32173 einschließlich Boardrevision beschaffen, 24/26-V-Widerspruch klären; 14,142-V-RMS-Obergrenze A1 beibehalten. DSP-Sicherheit noch nicht implementiert.
4. Pack 4512042: A1/C1-Identität, Ladegerätmodell, Adapter-Abschaltung und Temperaturpfad klären. UVLO/Hysterese, Sicherung, Leitungen und Einschaltstrom konkret auslegen. Bis dahin keine elektrische Bauanleitung freigeben.
5. Weitere HF/Horn- und Händlerdaten verifizieren, Budget vollständig nachführen; Planpositionen auf konkrete Einkaufseinheiten auflösen.
6. CAD-Werkzeug nach Bedarf installieren und Version fixieren, Volumenbilanz vor Zeichnung prüfen. Port A1 beansprucht bereits einen großen Teil der Innentiefe. Keine ungeprüften Fertigungsexporte erzeugen.

## Fortsetzungsregeln

Keine Annahme zum bestätigten Wert umetikettieren. Parameteränderungen nur in data/, Ergebnisse neu generieren. Bau-, Wetterschutz- und Sicherheitsfreigabe erfordert Messdaten; mathematische Referenztests genügen dafür nicht. Benutzerdateien und LICENSE bewahren. Keine automatisch erzeugte Lizenzfestlegung.
