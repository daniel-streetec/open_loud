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
