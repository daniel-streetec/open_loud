# Interner Ladeanschluss – E08 Montageentwurf

Eigener 2-mm-Aluminiumwinkel, außen 38 mm breit, senkrechte Platte 18 mm hoch, Fuß 19,9 mm tief. AMASS-XT60E-F sitzt intern hinter der Rückwand. Kein äußeres IP40-Loch. Abdeckung zum Laden abnehmen; nur trocken und mit ausgeschaltetem Verstärker laden.

Zentrale Maße: `data/parameters.json`, Gruppe `connection_mounts_e08`. `tools/setup_connection_mounts_e08.py` dokumentiert die Eingaben. Zwei M3×10 mit rückseitiger Scheibe und M3-Mutter befestigen den Stecker im 25-mm-Lochraster; der Kopf liegt direkt am Aluminium. Zwei M3×20 mit Scheiben und Muttern führen durch Fuß und 12-mm-Batteriedach. Kein metrisches Holzgewinde. Rechnerischer Gewindeüberstand 1 mm am Stecker und 2,6 mm am Dach; Toleranzprüfung und geeignete Schraubensicherung bleiben nötig.

Montagefolge: Winkel/Stecker auf Werkbank vormontieren; Fuß ans Dach schrauben; Kabel anlöten, isolieren und zugentlasten; Polarität/Durchgang prüfen; erst danach Akku einsetzen. Die endgültige Montagefreigabe hängt von Polkoordinaten, Steckergehäusekontur, Gegenstecker-/Kabelraum und zugänglicher Schraubverbindung ab.

Der Hersteller nennt einen Ausschnitt mit R3,9. Unsere eigene Halterplatte bekommt bei gleicher Breite/Höhe einen nahezu rechteckigen Laserausschnitt mit geplantem R0,2 und zusätzlicher Eckfreiheit; damit passt auch die konservative rechteckige Gehäusehülle. Das ist eine eigene Halterauslegung, keine Behauptung einer vermessenen Gehäusekontur. Die erste Kernelprüfung fand außerdem zwei Kollisionen großer Frontscheiben mit der Gehäusehülle; deshalb entfallen diese Scheiben, die 5,5-mm-Schraubenköpfe liegen direkt am Aluminium. Der Winkel hat noch idealisierte scharfe Biegeecken; Material, Innenradius und Abwicklung müssen vor Ausgabe einer Fertigungszeichnung festgelegt werden.

Dokumentation der Beschaffungs-/Quellenprobleme: bisherige RET-URL leitet auf `https://media.ret.hu/datasheet/XT60E-F.pdf` um und war beim erneuten Webabruf nicht verfügbar; auch die zweite Zeichnungskopie bei Aksotronik war nicht abrufbar. Vorher dokumentierte Maße bleiben Referenzen, die Quelle ist aktuell nicht erneut bestätigt. Keine neue Datenblattprüfung behaupten.

## Widerspruch zu frühen Zielwerten

Die vier ausgewählten Versorgungsteile in `data/procurement_E08.json` summieren sich bereits auf 338,02 EUR ohne Versand, Sicherungen, Kabel, Verstärker und Gehäuse. Das frühe Forschungsziel 300 EUR für A0 wird mit dieser Versorgung verfehlt. Der Nutzer hat höhere Masse zugunsten von Qualität zugelassen und längere Versorgung priorisiert; daraus folgt keine bestätigte neue Budgetobergrenze. Vollständige Kostensumme und Massenbilanz bleiben zu aktualisieren. Ein Festival von Mittwoch bis Sonntag ist weiterhin kein quantifiziertes Dauerlastprofil.
