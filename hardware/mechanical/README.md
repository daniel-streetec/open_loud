# Fusion-Konstruktion E03

Aktiver Stand: **OPEN_LOUD / OPEN_LOUD_A0_E03_Concept**, Fusion 2705.1.15. E02 bleibt als vorheriger Vorentwurf erhalten. Bauraum E03 B/H/T **330/560/300 mm** ohne vorstehende Treiberflansche, Schraubenköpfe, Griff oder Akku. Keine Fertigungsfreigabe.

Der Nutzer hat am 2026-11-09 Qualität und montierbare, stabile Details gegenüber dem bisherigen Gewichtsziel priorisiert. Deshalb 40 mm mehr Höhe, 12-mm-Birkenmultiplex für die Hülle und eine aus zwei Lagen laminierte **24-mm-Schallwand**. MDF ist nicht ausgewählt. Die größere Höhe schafft rund 24 mm Holzsteg zwischen LF- und Portausschnitt und rund 41 mm zwischen LF- und Hornausschnitt. Diese Abstände sind geometrisch geprüft, nicht statisch abgenommen.

Ein **3-mm-Stahlring, außen 280 / innen 220 mm**, hinter dem Tieftöner verteilt die Klemmkräfte der acht M5-Befestigungen. Seine Innenkontur bietet am Schraubenloch etwa 9 mm verbleibenden Stahlsteg. Der reale Korb muss vor Fertigung dagegen geprüft werden; das jetzige Korbmodell ist ein vereinfachter Kegelstumpf. Die dünne radiale Holzzone zwischen LF-Ausschnitt und Lochkreis wird ausdrücklich nicht als tragfähige Einzelbefestigung ohne Gegenring freigegeben.

Die Rückwand erhält vier 20×20-mm-Montageleisten, zehn von außen zugängliche M5-Durchgangspositionen und zehn innen befestigte 5-mm-Stahl-Gewindeplatten. Zwei kleine Halteschrauben je Platte verhindern, dass beim Öffnen lose Muttern oder Platten in die Box fallen. Die M5-Kernlöcher sind als 4,2-mm-Pilot modelliert; Gewinde nach dem Bohren schneiden, Werkstoff und Werkzeugempfehlung vor Fertigung bestätigen. Eine umlaufende 4-mm-breite, 1-mm-tiefe Dichtungsnut ist als eigener Bearbeitungsgang dokumentiert. Das ist noch kein Wetterschutznachweis.

## Dateien und Prüfung

- [Aktuelles F3D](exports/E03/OPEN_LOUD_A0_E03.f3d), [STEP](exports/E03/OPEN_LOUD_A0_E03.step)
- [Innenansicht](exports/E03/OPEN_LOUD_A0_E03_inside.png), [Front](exports/E03/OPEN_LOUD_A0_E03_front.png)
- [Zuschnittliste](exports/E03/cutlist_DRAFT.csv) und DXFs unter exports/E03/
- fusion_validation.json: tatsächliche Körper, Skizzen, Kollisionen, Parametertest und Massenschätzung
- step_roundtrip.json / native_roundtrip.json: tatsächlicher Rückimport in Fusion
- cad_validation.json: nachgelagerte Prüfung der DXF-Einheiten, Konturen, Maße und Bohrungszahlen sowie Hashes

`cad_validation.json` erst nach erfolgreichem Endlauf als Nachweis verwenden. Exportdateien tragen DRAFT; Werkzeugzugaben, Schnittfugen, Schraubenkopfsenkungen, Feintoleranzen und ein optimierter Plattenzuschnitt fehlen. Die alte Zwei-Platten-Kalkulation ist für E03 noch nicht durch einen Zuschnittplan belegt.

Endprüfung dieser Sitzung: 33 Volumenkörper, 71 Benutzerparameter beim nativen Rückimport, 128 vollständig bestimmte Konstruktionsskizzen vor Erzeugung der Exportskizzen, keine gemeldeten Timelinefehler oder Kollisionen. 26 DXFs geprüft, daraus 25 eigene Fertigungsteile plus separater Dichtungs-Nutgang. Rechnerische Holzmasse bei 600–700 kg/m³: 7,49–8,74 kg; Stahl-Gegenring etwa 0,55 kg und Gewindeplatten zusammen etwa 0,30 kg bei angenommener Stahldichte. Treiber, Akku und übrige Hardware kommen hinzu. Das ist ein bewusst robuster Erstprototyp, noch kein nachgewiesenes Qualitätsoptimum oder fertiges Tragegewicht.

## Reproduzieren

Fusion und MCP auf localhost:27182 starten; ab Repositorywurzel:

```powershell
python -B tools/fusion_bridge.py run hardware/mechanical/build_fusion_e03.py
python -B tools/fusion_bridge.py run hardware/mechanical/assemble_fusion_e03.py
python -B tools/fusion_bridge.py run hardware/mechanical/finalize_fusion_e03.py
python -B tools/fusion_bridge.py run hardware/mechanical/check_step_roundtrip_e03.py
python -B tools/fusion_bridge.py run hardware/mechanical/check_native_roundtrip_e03.py
python -B tools/fusion_bridge.py run hardware/mechanical/save_fusion.py
python -B tools/check_cad_exports.py
```

Der Generator bricht ab, wenn das Zieldokument bereits existiert. Zur erneuten unabhängigen Reproduktion zuerst im Skript einen neuen Dokumentnamen wählen und die dazugehörigen Prüfscripts entsprechend anpassen; keine bestehende Benutzerarbeit löschen. Zum Nachführen des existierenden eigenen E03-Dokuments nach Parameteränderungen `assemble_fusion_e03.py` und die nachfolgenden Schritte verwenden. Dichtungsnut und zwei Eckausklinkungen sind abgeleitete, fixierte Konturen: nach Änderungen von Breite/Leisten/Fachlage vollständig neu erzeugen. Der geprüfte Breitentest betrifft den Gehäuseparameter und stellt den Ursprungswert wieder her, keine automatische Komplettoptimierung.

## Parameter und Grenzen

Numerische Quelle: data/parameters.json. `layout.py` bilanziert den geplanten Netto-Luftraum von 34 l aus Bruttoinnenraum, Laminierung, Rohr, Gegenring, unteren Rückwandleisten/Gewindeplatten, HF-Hüllzylinder, Hersteller-Verdrängungen und Fachreserve. Das obere Fach ist als gesamte ausgeschlossene Zone einschließlich dortiger Einbauten angesetzt; diese werden nicht erneut abgezogen. Kleine Bohrungen, Klebstoff, Kabel, Dichtungen und reale Toleranzen verbleiben als Bilanzunsicherheit. 34 l ist eine Entwurfsschätzung, kein gemessenes Volumen.

Die Fusion-API dieser Installation skaliert einige Referenzen auf Flächen-/Volumenparameter falsch (reproduzierbarer Test in probe_units.py). Daher werden Portdurchmesser/-länge und Fachposition aus SI-Daten in Python berechnet und als explizite Längenparameter übertragen. Längenparameter steuern die bemaßten Skizzen und Features. Bei zentraler Änderung muss die Volumenbilanz erneut nachgeführt werden.

Der STEP-Rückimport wird mit relativer Volumentoleranz 1e-6 geprüft. Eine frühere absolute 1e-5-cm³-Grenze war für den gekrümmten Horn-Hüllkörper zu eng; der beobachtete Unterschied lag bei etwa 0,003 cm³ auf rund 15.000 cm³ Gesamtvolumen. Keine Abweichung wird als exakte Bit-Reproduktion ausgegeben. F3D enthält sämtliche Benutzerparameter und den Konstruktionsverlauf und wurde tatsächlich wieder in Fusion geöffnet. Python kann das ZIP-Verzeichnis lesen, unterstützt aber die verwendete Kompressionsmethode nicht für eine vollständige CRC-Prüfung; diese wird ausdrücklich nicht behauptet.

Verstärker und Verkabelung sind bisher lediglich ein ausdrücklich unbestätigter Installationsraum, kein maßgetreues JAB3+-Modell. Akkuhalter, Akku, Gitter, Griff, Gurte, thermische Anbindung und elektrische Durchführung fehlen noch. Gesamtschwerpunkt und Tragebefestigungen sind deshalb nicht freigegeben. Quellen und Modellherkunft: provenance.json.
