# Verkabelung und Befestiger E05

Stand 2026-11-09. Reproduzierbare Auslegung und CAD-Vorentwurf, **keine Freigabe zum Bestromen**. Eingangswerte mit Einheit, Quelle und Unsicherheit in `data/parameters.json`, Gruppen `wiring` und `fasteners`; konkrete Bezugsbeobachtungen und Lücken in `data/wiring_procurement.json`. Keine unbekannte Lieferantenangabe wird durch einen berechneten Wert ersetzt.

## Strom und Querschnitt

A0, 15–21 V Versorgung, zwei BTL-Kanäle. Rechenfall gleichzeitiger Sinus: LF 4 Ohm, HF 8 Ohm, Ausgangsspannung 0,9·U/√2, HF höchstens 12,649 Vrms. Dieser HF-Limiter ist **noch nicht implementiert**. Mit konservativ angenommenen 65% Verstärkerwirkungsgrad und 1,8 W Leerlauf ergeben sich 3,62 / 4,31 / 4,82 A bei 15 / 18 / 21 V. Die Herstellerangabe 83% bei 24 V und 2×50 W ist kein Nachweis für diese Betriebspunkte. Für die Leitungsauslegung 6 A DC mit Reserve; 10 A ist nur ein kurzer Prüf-/Einschaltstromfall. Unbegrenzter Verstärkerbetrieb und Lastkurzschluss sind damit nicht freigegeben.

LF-Auslegung 4 Arms: maximale geplante Ausgangsspannung gegen minimale Impedanz 3,6 Ohm geprüft. HF 2,1 Arms: HF-Spannungsgrenze gegen 6,3 Ohm. Nennimpedanz ersetzt keine frequenzabhängige Lastprüfung; die thermische Musikbelastung liegt normalerweise darunter. Die akustische Simulation bleibt maßgeblich für die zulässige Ausgangsspannung je Frequenz.

Für jede Leitung werden beide Adern gerechnet:

`R = 2·L·r20·[1+0,00393·(T−20°C)] + R_Originalkabel + R_Kontakte`

`ΔU=I·R; P_Verlust=I²·R`. Herstellerwiderstand des CLS215 13,3 Ohm/km je Ader statt idealisierten Kupfers. Rechentemperatur 60°C. Kontaktbudget DC insgesamt 30 mOhm, Lautsprecher je 10 mOhm; das sind zu messende Abnahmewerte, keine Datenblattwerte. Dazu pro Zweig ein angenommener 100-mm-Originalkabelabschnitt mit ungünstig angenommenen 0,326 mm² (AWG22). Tatsächliche Länge/Querschnitt/Kontakte am Modul prüfen. Besonders die Originalkabel können den zulässigen Strom begrenzen.

| Zweig | Auslegungsstrom | Kabel | CAD-Mittellinie | Zuschnitt mit Zugaben | Spannungsfall einschließlich angenommener Übergänge |
|---|---:|---|---:|---:|---:|
| Versorgung | 6 A DC | 2×1,5 mm² | 83 mm | 250 mm | 0,311 V |
| LF | 4 Arms | 2×1,5 mm² | 293 mm | 460 mm | 0,153 V |
| HF | 2,1 Arms | 2×1,5 mm² | 182 mm | 350 mm | 0,073 V |

Alle Werte werden aus `tools/generate_wiring.py` erzeugt, siehe `results/wiring/calculation.json` und `harness.csv`. Die Mittellinien enden an **vorläufigen Anschlussstationen**, nicht an nachgewiesenen realen Kontakten. Zuschnitt je Zweig: Mittellinie +100 mm Wartungsreserve +60 mm Anschlusszugabe, auf 10 mm aufgerundet. Kabel zusammen 1,06 m / 84 g; Einkauf 2 m als Meterware, Rest für Muster und Korrekturen. Originalkabel und Stecker zusätzlich.

Grenze DC 3% von 15 V (=0,45 V); Lautsprecher 5% der nominalen ohmschen Lastspannung bei Auslegungsstrom. Zusätzlich Wärme-Screening der Leitungsschleife höchstens 1,2 W/m bei 6 A: daraus etwa 1,39 mm² Mindestquerschnitt, gewählt 1,5 mm². **Diese selbst gesetzte Verlustgrenze ist keine Strombelastbarkeitstabelle.** Wärmeabgabe, Bündelung und Kontaktwärme müssen am Muster geprüft werden. Zulässiger thermischer Widerstand für 20 K Erwärmung beträgt bei der DC-Leitung etwa 18 K·m/W; eine bessere Kühlung wird nicht einfach unterstellt. Kein unbegründeter allgemeiner „1,5 mm² verträgt X A“-Wert.

Eine Kabelsorte vereinfacht Einkauf, Ersatz und Anschlüsse; beim HF-Zweig entsteht ein geringer Masseaufschlag. PVC-Rundmantel nominal 7 mm. Keine CCA-Leitung. 28 mm Biegeradius als Planungsannahme (4×OD), Hersteller-Mindestwert unbekannt; reale Verlegung auf Knickfreiheit prüfen. Im CAD sind Mantelsegmente enthalten; einzelne Litzen, Abisolierungen und Wartungsschlaufen sind nicht nachgebildet.

## Verbindungen und Durchführungen

Versorgung: Akkuadapter → möglichst akkunahe Sicherung im Pluszweig → DC-Schalter → nachgewiesene Unterspannungs-/Verpolschutzfunktion → J8. Lage des Akkuadapters, UVLO, Schalter, Halter und Einschaltstrom sind offene Freigabepunkte; deshalb ist der CAD-Versorgungszweig eine interne Längenreserve. Der ungesicherte Akkuabschnitt muss so kurz wie möglich bleiben; Ziel höchstens 50 mm bis Sicherung, konkret erst mit dem Adapter belegbar. Ladegerät ausschließlich am vorgesehenen Herstellerakku; JAB-Modul enthält keine Ladeschaltung.

J8 laut WONDOM-Unterlage: Pin1 VCC, Pin2 GND. J10: Pin1 R+, Pin2 L−, Pin3 R−, Pin4 L+. Paare daher **1/3 und 4/2**. Keine gemeinsame Lautsprechermasse, kein Minus an Akku-GND. Vorläufig L=LF, R=HF; Zuordnung erst nach Boardrevision/Pin1-Blickrichtung und DSP-Kanaltest beschriften. Keine benachbarten Pins blind als Paar verwenden. Vor HF-Anschluss HF-Hochpass und Spannungsbegrenzung am Lastwiderstand nachweisen.

Originalstecker und passende Originalkabel des Moduls beibehalten. Übergang zu 1,5 mm² mit je zwei WAGO 221-2411 (sechs Stück insgesamt) im trockenen Wartungsraum. Herstellerdatenblatt: feindrähtige Leiter 0,2–4 mm², 11 mm Abisolierung. Keine Lötverzinnung unter Federklemmen. Nach Montage Sichtprüfung und Zugprobe. WAGO 221-2522 als schraubbarer Zweifachhalter geplant; Befestigungsposition und Kleinmengenbeschaffung noch offen. Keine losen Verbinder im schwingenden Gehäuse. WAGO-Verbindungen sind weder verpolsicher kodierte Steckverbinder noch wettergeschützte Anschlüsse: Zweig und beide Pole dauerhaft kennzeichnen, spannungsfrei warten. Keine generischen XT30-„30 A“-Angaben übernehmen: überprüftes AMASS-Datenblatt nennt 15 A und passt nicht automatisch zu 1,5-mm²-Lötbechern.

LF durch den Boden des Wartungsraums bei x275/z240 mm; HF durch die senkrechte Trennwand bei x275/y460 mm. Kein zusätzlicher äußerer Kabelauslass. Referenz: LAPP 53017210, M16×1,5, Gewindelänge12 mm, Klemmbereich3,5–8 mm. Das 7-mm-Kabel liegt 1 mm unter der Obergrenze; M12 mit 7-mm-Grenze hätte keine Reserve. Bohrung16,5 mm; innenseitig28-mm-Entlastung5 mm tief, verbleibende Holzstärke7 mm. Alle Fräsflächen versiegeln. Annahme Dichtung0,5 + Holz7 + flache Metallmutter3 =10,5 mm, verbleibender Gewindevorrat1,5 mm. Eine 5-mm-Kunststoffmutter passt **nicht** in diese Auslegung. Metallmutter-Referenz LAPP SKINDICHT SM-M M16, Herstellermaß3 mm; exakte aktuelle Artikelvariante und Privatkundenquelle offen.

Die LAPP-Kaufteile im CAD sind vereinfachte Maßreferenzen. Händler-Einzelpreis und Lagerbestand wurden gefunden, Privatkundenberechtigung aber nicht vollständig bestätigt; B2B-only/Großpack-Angebote ausdrücklich verworfen. Keine Beschaffungsfreigabe für diese Referenzen. Dichtwirkung am rauen/versiegelten Holz, Zugentlastung und akustische Leckage prüfen; eine IP-Angabe des Kaufteils verleiht dem Lautsprecher keine IP-Klasse.

Treiberseitige Kontakte am Muster vermessen, dann passende vollisolierte Kontakte für 1,5 mm² auswählen; keine ungeprüfte Annahme „6,3-mm-Flachstecker“. Leitungsclips verschraubt, Zielabstand≤100 mm, mindestens20 mm Abstand zu beweglichen Treiberteilen, keine Leitungen auf scharfen Metallkanten. Tatsächliche Klemmen-, Clip- und Wartungsschlaufenpositionen müssen noch ins CAD eingearbeitet werden.

## Schrauben und Montage

E05 enthält 42 Schrauben, 34 Scheiben und 12 Muttern. Zusätzlich zwei Gegenmuttern der Durchführung. Normale handelsübliche A2-Maschinenschrauben, Einzelnachkauf belegt. Schraubenschaft/Gewinde als Nennhülle, keine modellierte Gewindehelix. Nicht freigegebene Holzkopf- und Mutternmaße sind gekennzeichnet.

- LF: acht M5×45 ISO4762, je zwei M5-Scheiben und eine ISO4032-M5-Mutter. Klemmpaket8-mm-Flansch+24-mm-Holz+3-mm-Stahl+2×1-mm-Scheibe+4,7-mm-Mutter=41,7 mm. Etwa3,3 mm Gewindeüberstand; eine zusätzliche Dichtung reduziert ihn entsprechend. Schrauben nicht in dünnen Holzsteg gewindeschneiden.
- Horn: vier M4×40 ISO4762, je zwei Scheiben und eine DIN934-M4-Mutter. Paket34,3 mm, etwa5,7 mm Überstand. Zunächst montieren, solange Zugang zum Hornraum offen ist; späterer Mutternzugang durch LF-Öffnung/mit Werkzeug muss noch am Muster bewiesen oder durch Standard-Käfig-/Einschlagmutter verbessert werden.
- Rückwand: zehn M5×40, je eine Scheibe; greifen in vorhandene5-mm-Gewindeplatten. 12-mm-Rückwand+20-mm-Leiste+5-mm-Platte+1-mm-Scheibe=38 mm; 2 mm Überstand. Pilotbohrungen4,2 mm **vor Montage M5 schneiden**. Keine zusätzlichen Muttern nötig.
- Gewindeplatten: zwanzig Holzschrauben2,5×12 mit nicht senkendem Kopf als gekennzeichnete Kandidaten; 5-mm-Platte lässt7 mm Holzeingriff. Kopfform/Hersteller und Haltbarkeit noch prüfen. Kein unkontrolliertes Durchschrauben der Rückwand.

Anzugsmoment folgt erst aus Flanschbelastbarkeit und Dichtungsversuch; kein Stahl-Schraubmoment unbesehen auf Holz und Kunststoffhorn übertragen. Kreuzweise anziehen, Druckstellen und Risse prüfen. Gewindesicherung/Losdrehen im Vibrationsversuch prüfen, Dichtflächen frei von Kleber halten. Front zugängliche Schraubenköpfe bleiben ohne Gitter exponiert; Endschutz/Gitter weiterhin offen.

## Abnahme vor Bestromen

1. Tatsächliche Originalkabel, Kontakte, Treiberanschlüsse und Boardrevision protokollieren; Stromfähigkeit und Zuordnung freigeben. Fehlende Sicherungs-/Adapter-/UVLO-Daten schließen.
2. Kabel ausmessen, Zuschnitt korrigieren, Schlaufen/Clips im offenen Gehäuse trocken montieren. Kein Einklemmen beim zehnmaligen Öffnen/Schließen; Rückwand komplett abnehmbar. Alle Klemmen erreichbar und gegen Bewegung fixiert.
3. Spannungsfrei Durchgang jedes Pols und Isolation zwischen DC/LF/HF und Metallteilen prüfen; keine Verbindung BTL− zu DC−. Jede Leitung markieren. Crimpzugprüfung nach Kontakt-Hersteller, keine willkürliche universelle Prüfkraft.
4. Strombegrenztes Labornetzteil, zunächst ohne Treiber. Polarität/Kanalzuordnung und DSP an Lastwiderständen. HF erst nach Filter-/Limiterprüfung anschließen.
5. DC-Zweig bei6 A, LF4 Arms, HF2,1 Arms jeweils60 Minuten und gleichzeitig im realistischen Gehäuse prüfen. Umgebung40°C Prüfziel; Leiter und Kontaktgehäuse≤60°C und unter sämtlichen niedrigeren Herstellergrenzen. Temperatur mit Thermoelement messen, thermisches Gleichgewicht≤1 K Änderung in15 Minuten. ΔU und Kontaktbudgets aus Ergebnisdatei einhalten; Pigtails gesondert messen. Abweichung: Querschnitt, Verbindung oder Kühlung ändern.
6. Einschaltstrom/-dauer und Ausschaltspitzen messen; Sicherungskurve, DC-Schalter, Kurzschluss-Abschaltung und Packschutz koordinieren. Unbestätigte Akku-Kurzschlussversuche nicht als normalen Prototypentest durchführen.
7. Verschraubungen am Kabel zugentlastet, keine Mantelquetschung/Knicke; akustische Leckage gegenüber verschlossenem Referenzzustand≤0,5 dB Abweichung im LF-Bereich. Spritzwasser-/Regenversuch erst nach eigenem Prüfaufbau, danach spannungsfrei Feuchtekontrolle. Kein Wetterschutznachweis allein aus CAD.

## Reproduktion

`python -B tools/generate_wiring.py`

`python -B -m unittest discover -s tests -v`

Fusion: `python -B tools/fusion_bridge.py run hardware/mechanical/build_wiring_e05.py` klont ausschließlich das versionierte E03-Archiv in ein neues Dokument. Nicht erneut ausführen, solange ein E05-Dokument offen ist. Anschließend `verify_wiring_e05.py`; der Prüfer bricht bei Kabelkollisionen/Timelinefehlern ab, statt erfolgreiche Exporte vorzutäuschen. Änderungs- und Reparaturskripte sind gegebenenfalls zusätzlich auszuführen, siehe `docs/DEVELOPMENT.md`. E03 wird nicht überschrieben.

`python -B tools/generate_wiring_bom.py` verbindet CAD-Stückzahlen, Kabelzuschnitt und Beschaffungsdaten. Dies ist eine Ergänzungs-BOM; unbekannte Preise und offene Elektronik verhindern eine belastbare Gesamtbestellsumme.
