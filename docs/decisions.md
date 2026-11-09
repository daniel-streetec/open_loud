# Entscheidungen, Widersprüche und Risiken

Aktuell E05: zentrale Versorgung wird nach Nutzerkorrektur neu verglichen; der kleine Werkzeugakku ist historischer Rechenfall, keine endgültige Auswahl. Festivalreferenz Mittwoch–Sonntag mit bisheriger12V/100Ah-Box; USB ausdrücklich optional. Drei interne2x1,5mm²-Kabelzweige für die bisherige18V-Architektur berechnet und nominale Kabelkollisionen korrigiert. Bei Spannungs-/Akkukonzeptwechsel neu rechnen. Sämtliche metrischen Schrauben haben ein geplantes Gegenstück; Hornmuttern-Wartungszugang, reale Treiberanschlüsse, Klemmenhalter und Packschutz sind weiterhin offen. Einzelheiten docs/build/wiring.md und docs/NEXT_SESSION.md.

| ID | Entscheidung / Befund | Folge / Rücknahme |
|---|---|---|
| D01 | A0/A1 des Berichts statt zuvor unverbindlich erwogenem 10PR300-Vergleich | Quellenkonforme Referenzen; Auswahl nach Messung ändern |
| D02 | Rechenimplementierung neu aus dokumentierten Gleichungen, Standardbibliothek | Keine Abhängigkeit von nicht geklärt lizenziertem PDF-Anlagencode |
| D03 | A1 zusätzlich auf sqrt(50 W × 4 Ohm) begrenzen | Bericht S. 8 empfiehlt Grenze, S. 7 nutzt teils 23,5 V × 0,9 / sqrt(2); beide Fälle berechnen |
| D04 | Keine endgültige Hardware-/Dokumentationslizenz setzen | Vorhandenes Apache-2.0-LICENSE unverändert; MIT-Vorschlag des Berichts ist kein Beschluss |
| C01 | 10FE300 Händler 96 dB statt Hersteller 94 dB; Händler-Lochmaß 133 mm | Herstellerdaten für Auslegung; Lochbild vor Fertigung am Muster prüfen |
| C02 | 10FE200 Händler nennt 233 mm Lochkreis, Hersteller unterscheidet 233,3 mm Ausschnitt und 243,8 mm Lochkreis | Nicht Händlertext in CAD übernehmen |
| C03 | Pollin gleichzeitig 1–3 Werktage und nicht ausreichend verfügbar | Lieferbarkeit unklar, keine bestätigte sofortige Beschaffung |
| C04 | Einhell URL A1 führt zu C1-Titel | Kit-/Laderrevision noch nicht eindeutig |
| C05 | Qts/Vas/Mms/Fs/Cms/Rms/BL sind gerundete, nicht völlig konsistente T/S-Sätze | Modell bevorzugt Fs/Mms/BL/Rms/Re/Sd wie Bericht; Konsistenzfehler ausgeben, keine Mischung ohne Nachweis |
| C06 | Laufzeittabelle des Berichts ist nicht vollständig aus den genannten Extremwerten reproduzierbar | Direkte Intervallrechnung ergibt z.B. A0 laut bis 26,9 W statt 22 W; keine stillschweigende Übernahme der optimistischeren Laufzeit |
| C07 | Geometrisch geschlossene 12-mm-Hülle wiegt vor Ausschnitten 5,75–6,71 kg statt grob 6,1–7,2 kg laut Bericht | Nur exakte Außen-minus-Innen-Volumenrechnung; Verstrebung, Fugen, Ausschnitte und Einbauten separat ergänzen |
| R01 | Packschutz bei Fremdadapter ungeklärt | Elektrischer Aufbau und Veröffentlichung gesperrt bis Nachweis |
| R02 | HF/LF-Richtwirkung und Schallwand fehlen | LF-Modell kann Klang und Maximalpegel des Gesamtsystems nicht freigeben |
| R03 | Kein Hochpass/Limiter im Vergleich | Ungefilterte Spannung kann unter Fb Xmax überschreiten; keine DSP-Einstellfreigabe |
| R04 | Kosten enthalten pauschale Planbeträge | BOM ist Kostenstruktur, noch keine vollständige bestellbare Fertigungs-BOM |
| R05 | Masse und Volumen nur vorläufig | ≤10/11 kg und 34 l müssen im CAD/Wiegen bestätigt werden |
| R06 | Temperatur, Regen, Tragefestigkeit ungemessen | Keine IP-, Sicherheits- oder Outdoor-Freigabe |

Technische Empfehlung E01: A0 für weitere Simulation und variables Muster priorisieren; A1 parallel als abhängiger Versuch. Das ist keine Bestell- oder Baufreigabe.

## E03 – Nutzerpriorität und Konstruktion

- Nutzer akzeptiert begründetes Mehrgewicht für Qualität und verlangt belastbare Ausschnittzonen und Montagezugang. A0 als erster CAD-Träger, kein endgültiger Ausschluss von A1.
- Birkenmultiplex statt MDF; 12-mm-Hülle, 24-mm-laminierte Schallwand, Stahl-Gegenring, 20-mm-Rückleisten. Höhe auf 560 mm erhöht, damit breitere Stege und Montageabstände möglich sind. Steifigkeit und Klebeverbund noch nicht gemessen.
- Rückwand von außen verschraubbar; feste Gewindeplatten statt beim Öffnen loser Muttern. Dichtungsnut vorgesehen, keine IP-Zusage.
- Herstellerpakete/Zeichnungen geprüft; in den geprüften LF-/Hornquellen kein 3D-CAD gefunden. Eigene Einbaumodelle ausdrücklich vereinfacht, keine unbesehen kopierten Fremdmodelle.
- Fusion-Automatismen schnitten zunächst Nachbarkörper mit. Die Exportprüfung entdeckte getrennte Rückleisten; Schnitte werden jetzt auf explizite Zielkörper begrenzt. Durchgehende Leisten und die endgültigen Exporte erneut prüfen.
- E01-Warenkorb ist keine vollständige E03-Kostenfreigabe. Zusätzliche Mechanik in data/mechanical_hardware.json, unbekannte Preise bleiben null.
