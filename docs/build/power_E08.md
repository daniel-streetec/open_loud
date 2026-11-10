# E08 – Versorgung und Einbau, Entwicklungsstand 2026-11-10

Kein freigegebenes Produkt. E08 ersetzt die kleine Werkzeugakku-Planung durch einen gekauften 4S-LFP-Akku mit integriertem BMS. Verstärker und DSP bleiben das fertige WONDOM JAB3+ AA-JA32173; keine eigene Verstärkerentwicklung.

## Gewählte Kette und Beschaffung

| Teil | Grundlage / Bezugsquelle | Beobachteter Bruttopreis, Stand 2026-11-10 | Status |
|---|---|---|---|
| EREMIT MICRO GEN7 BASIS 12 V 50 Ah | [Hersteller](https://www.eremit.de/p/12v-50ah-lifepo4-micro-gen-7-basis-beguenstigte-pv-verwendung-0-ust) | 219,90 EUR, 3–5 Tage; regulärer Endkundenpreis, keine PV-Steuerbefreiung angenommen | Auswahl; Pole und Kurzschlussdaten offen |
| Victron Orion-Tr 12/24-5, ORI122410110 | [Herstellerdatenblatt](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-DC-DC-converters-isolated-100-250-400W-EN.pdf), [Maßzeichnung](https://www.victronenergy.com/upload/documents/Orion-Tr-110W-120W-Isolated.PDF), [Händler](https://www.ferroberlin.de/hersteller/victron-energy/dc-dc-spannungswandler/) | 80,92 EUR; 2 Stück, 3–4 Tage | Auf 20,0 V einstellen, NICHT auf nominal 24 V belassen |
| EREMIT 14,6 V / 5 A LFP-Lader | [Hersteller und Shop](https://www.eremit.de/p/12v-5a-lifepo4-ladegeraet-entstoert) | 34,90 EUR, 2–5 Tage | Extern; nicht über Orion laden |
| AMASS XT60E-F | [Herstellerzeichnung als Lieferantenkopie](https://www.ret.hu/media/product/39159/666752/XT60E-F.pdf), [Einzelhandel](https://vgr-rc.de/p/amass-xt60e-f-xt60e-f-montierbare-xt60e-buchsensteckverbinder-fuer-rc-drohne-flugzeug-fpv-renndrohne) | 2,30 EUR, 1–2 Tage | IP40: ausschließlich hinter abgenommener Rückwand, trocken laden |

Versand zusätzlich; keine Bestellung erfolgt. Diese Tabelle ist noch keine vollständige Einkaufsfreigabe. Herstellerdateien werden nicht ins Repository übernommen; CAD-Hüllmodelle sind eigene Nachzeichnungen mit Unsicherheitskennzeichnung.

Akku → F1 15 A → Verpolschutz **noch auszuwählen** → Orion → F3 5 A → JAB3+. Separate Ladekette: interner XT60 → F2 7,5 A → Akku. Sicherungswerte sind Kandidaten, bis Einschaltstrom, Temperatur und Abschaltvermögen gegen den tatsächlichen Akku geprüft sind. BMS ersetzt keine Leitungsabsicherung. Orion-Unterspannungsabschaltung bei 7 V schützt keinen 4S-LFP-Akku; Akkuschutz beruht auf dessen zu qualifizierendem BMS.

## Berechnungen und Montage

`python -B tools/calculate_power_e08.py` erzeugt Energie-/Lastszenarien. 640 Wh nominal, 480–576 Wh angenommene nutzbare Energie. Keine Übertragung der alten Festivalerfahrung auf ungemessenen Dauerbetrieb. LF 12 Vrms und HF 10 Vrms sind Kalibrierziele, keine bereits installierten DSP-Limiter. Worst-Case-Wandlerwärme liegt rechnerisch bei rund 20 W: geschlossene Kammer ohne nachgewiesenen Wärmepfad ist thermisch nicht freigegeben.

`python -B tools/calculate_harness_e08.py` erzeugt Radien, Zuschnittlängen und warme Widerstände. Hauptversorgung: zwei einzeln isolierte 4-mm²-Adern; geregelte Versorgung und Lautsprecher: 2×1,5 mm². Reserven sind enthalten, aber noch nicht vollständig im CAD abgelegt. Strombelastbarkeit, Lieferanten-Außendurchmesser und reale Anschlusslitzen separat prüfen. BTL-Lautsprecherminus niemals mit Versorgungsmasse verbinden.

Akkuhüllmaß 195×170×130 mm, 4,9 kg. Eigene abgedichtete Kammer mit Montagefreiraum, Dach und Rückleistenaussparungen. Gurtanker und exakte Polabdeckungen noch nicht freigegeben. Vergrößerter Elektronikträger 152×126×2 mm mit M3-Abstandhaltern, Schrauben und Gegenstücken; metrische Schrauben greifen nicht direkt ins Holz. Orion mit durchgesteckten M3-Schrauben und Muttern an der Trennwand. Anschlussklemmen benötigen zusätzliche reale Befestigung und Zugentlastung.

## Verworfen / offen

Pololu 2815 wurde geprüft, aber nicht als Verpolschutz gewählt: [Hersteller](https://www.pololu.com/product/2815) nennt 16 A erst bei bis zu 150 °C und nur 6 A bei 55 °C unter seinen Versuchsbedingungen. Das rechtfertigt keine ungeprüfte Auswahl für 12 A im geschlossenen Holzgehäuse.

Offen: robustes Schalt-/Verpolschutzteil, Gurtanker, Halter für Ladebuchse und Sicherungen, Klemmen und Kabelschellen, vollständige Anschluss-Pinliste, Akku-Polkoordinaten, Kühlung, reale Kabelführung samt Wartungsschlaufen, Kollisionsbehebung und Auszugprüfung, E08-Baugruppenhierarchie, Export-Rückimporte, aktualisierte vollständige BOM und Zeichnungssatz. Spritzwasser-, Sicherheits- und Leistungsfreigabe bleiben unbewiesen.
