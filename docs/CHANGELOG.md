# Änderungsstand

## E05 – 2026-11-09

Strom-/Querschnittsauslegung für drei Kabelzweige mit Temperatur, Hin-/Rückleitung, Originalpigtail-Annahme, Kontaktbudgets und Verlusten implementiert.2x1,5mm², Zuschnitt250/460/350mm. Reproduzierbare CSV/JSON und strukturierte Ergänzungs-BOM.95zusätzliche Fusion-Komponenten einschließlich42Schrauben,34Scheiben,12Muttern, Durchführungen und Kabelmänteln; keine neue äußere Panzerverkleidung. Gewindeeingriff/Gegenstücke ausdrücklich dokumentiert, weitere Montage-/Kontaktpunkte offen.

Erste Kernelprüfung fand drei Kabelkollisionen und zwei fehlgeschlagene Y-Schnitte. Korrigiert und erneut geprüft: keine Kabelkollisionen oder Timelinefehler, acht LF-Gelenkwerkzeugwege bestanden.204Körper; STEP und F3D tatsächlich rückimportiert, native71Parameter erhalten. Fusion gespeichert. Keine physische Gesamtmontage-, Elektro- oder Wetterfreigabe.

Nutzer stellt kleinen Werkzeugakku infrage; Festivalvergleich12V/100Ah aus bisheriger anderer Box, USB ausdrücklich keine Pflicht. Neue ausführbare Batterie-/Energieszenarien, reguläre Endkundenpreise statt unzulässiger0%-PV-Preise. Technischer Vollständigkeitsplan und autorisierter nächtlicher Codex-Wiederanlauf mit festem Sitzungsbezug, Sperre gegen Doppelstarts, Deadline und Protokoll angelegt;13Tests bestanden. Nachtlauf noch nicht nachgewiesen.

## E04-Studie zurückgenommen – 2026-11-09

Elektronik-/Montage-/Wasserpfadstudie erstellt, aber Außenanbauten vom Nutzer als überdimensioniert abgelehnt. Eigenbau-Ecken, Leisten, große Porthaube und Kabelabdeckung aus der aktiven Konstruktion entfernt; unsaved E04 nur unter ignoriertem .tools/rejected archiviert und geschlossen. E03 wieder aktiv. Masterparameter bytegleich zu geprüftem E03 wiederhergestellt, E04-Generator gesperrt. Ungeprüfte Kabelwege und Prüfberichte eindeutig als verworfene Studie gekennzeichnet.

Nutzer legt Privatkundenbeschaffung und Standardteile als Freigabekriterium fest. Beschaffungsrichtlinie maschinenlesbar in data/procurement_policy.json. Keine exklusive B2B-Abhängigkeit oder Großverpackung für einen Einzelbau. Endkundenquelle, Menge, Bruttopreis, Versand und Verfügbarkeit müssen je Teil belegt werden.

## E03 – 2026-11-09

Fusion-MCP auf Port 27182 geprüft und lokaler Client eingerichtet; Projekt OPEN_LOUD angelegt, A0 E02 und anschließend verstärkten E03-Vorentwurf erstellt. Nach Nutzerpriorisierung von Qualität/Montage auf 560mm Höhe, 24mm laminierte Schallwand, Stahl-Gegenring, 20mm Rückleisten und zehn feste Gewindeplatten umgestellt. Montagefolge, zusätzliche Hardwarekandidaten und Modellherkunft dokumentiert. Herstellerpaket LF enthält nur drei PDFs; B&C-Maßblatt ausgewertet, keine fremden CAD-Dateien übernommen.

Exportprüfungen entdeckten zwei unbeabsichtigt mitgeschnittene Rückleisten; Schnittteilnehmer auf Fachboden begrenzt und Features sauber neu angelegt. Endstand hat vier durchgehende Rückleisten. Fusion-Expressionsfehler bei Flächen-/Volumenreferenzen im separaten Test belegt, betroffene Maße aus Python-SI-Quelle übertragen. Frühere fehlgeschlagene Skriptläufe nicht als Erfolg gewertet.

STEP und F3D tatsächlich rückimportiert, Volumen-/Körper-/Parametervergleich und Timelineprüfung durchgeführt. DXF-Prüfung umfasst mm-Einheit, geschlossene Konturen, Zuschnittmaße und Montagebohrungen; Details und endgültiger Status in exports/E03/*validation.json. Fertigungs- und Sicherheitsfreigabe bleiben offen. Root-Lizenz unverändert; keine Bestellung oder öffentliche Veröffentlichung.

Ausgeführter Endstand: 33 Körper, 71 native Parameter, 128 vollständig bestimmte Konstruktionsskizzen, keine Kollisionen/Timelinefehler; 26 DXFs geprüft, 25 eigene Fertigungsteile gelistet. Sechs analytische Python-Tests bestanden; Akustik-/Energie-/Kosten-Ausgaben in zwei Läufen byteidentisch. F3D nutzt unter anderem ZIP-Kompression 93, deren CRC-Prüfung Python 3.13 hier nicht unterstützt; stattdessen tatsächlicher nativer Import samt Modellprüfung. Git-Dateien noch nicht committed.

## E01 – 2026-11-09

Bestandsaufnahme nach Nutzer-Upload des Phase-1-PDF; Anforderungen, Ziele, Annahmen und Entscheidungen getrennt. PDF-Dateianlagen inventarisiert, eingebetteten Modellcode und BOM gelesen, keinen eingebetteten Code ausgeführt. Primärquellen für zwei LF-Kandidaten sowie ausgewählte HF-/Horn- und Packdaten geprüft; Preise für LF und Akku erneut abgerufen. Widersprüche und ungeklärte Liefer-/Schutzangaben protokolliert.

Zentrale JSON-Parameterbasis und strukturierte vorläufige Kosten-BOM eingerichtet. Neues ausführbares LF-Netzwerkmodell, A0/A1 plus geschlossener Referenzfall, Ql-/Rail-Szenarien, Energieintervalle und hypothetische Pack-Spitzenlastrechnung. CSV/JSON/Markdown mit Eingangs- und Quellcodehashes erzeugt. Keine Bau-, Sicherheits-, Wetter- oder Lizenzfreigabe; keine Bestellung oder Veröffentlichung.

Tatsächlich ausgeführte Endprüfung: `python tools/reproduce.py` unter Python 3.13.7. Fünf analytische Referenztests bestanden, 4203 Frequenzzeilen auf Grenzen und endliche Werte geprüft, BOM-Materialsummen reproduziert, zwei vollständige Generierungsläufe byteidentisch. `git diff --check` ohne Befund; neue Dateien sind noch nicht committed. Erste Generatorausführung scheiterte am Zugriff auf verschachtelte Lastprofile; korrigiert und vollständig erneut ausgeführt.

Offen bleiben E03–E08 gemäß DEVELOPMENT.md: weitere Primärquellen/Revisionen und konkrete Schutzbauteile, externer BR-Quercheck, Messdaten/DSP, CAD und Fertigungsexporte einschließlich tatsächlicher Geometrieprüfung, vollständige bestellbare BOM, Montageanleitung, Prototypentests und Lizenzentscheidung. README und DEVELOPMENT.md sind Einstieg für die nächste Sitzung.
