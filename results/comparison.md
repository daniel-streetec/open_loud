# Erster Konzeptvergleich E01

Generiert mit `python simulation/run.py`. Lineares LF-Modell, keine Messung, keine Bau-/DSP-Freigabe.

| Konzept | F3 / F6 / F10 Hz | SPL-Grenze 50 / 63 Hz, dB, 2π/1m | Port effektiv / physisch cm |
|---|---|---|---|
| A0 | 73.3 / 60.4 / 47.5 | 103.1 / 106.9 | 22.8 / 16.1 |
| A0-sealed-control | 82.6 / 66.1 / 51.8 | 100.9 / 104.9 | 0.0 / 0.0 |
| A1 | 61.0 / 49.0 / 40.2 | 106.1 / 109.0 | 30.4 / 23.1 |

A1 ist auf 14,142 Vrms gekappt. CSV enthält zusätzlich das ungekappte Berichtsszenario und jede einzelne frequenzabhängige Grenze. Pn dient nur als unvalidierter Kupferverlust-Proxy; kein thermischer Nachweis.

| Konzept | Material / erster Bau inkl. Programmer EUR | davon Planbeträge EUR | Masse laut Bericht kg |
|---|---|---|---|
| A0 | 368.34 / 394.14 | 92.00 | 8–10, unbestätigt |
| A1 | 445.23 / 471.03 | 104.00 | 10–12, unbestätigt |

Kosten und Tragemassen dieser Tabelle sind E01-Referenzans?tze. Verst?rkte E03-Mechanik ist darin nicht vollst?ndig kalkuliert; siehe data/mechanical_hardware.json und hardware/mechanical/README.md.

Beide nutzen vorläufig H/B/T 560/360/340 mm. Geometrisch innen 56.91 l vor Einbauten; reine Hülle vor Ausschnitten 6.98–8.14 kg. Keine vollständige Verdrängungs- oder Schwerpunktbilanz.

| Konzept / Lastprofil | mittlere Akkuaufnahme W | Laufzeitbereich h |
|---|---|---|
| A0 / background | 2.6–4.6 | 12.6–25.3 |
| A0 / normal | 4.3–11.5 | 5.0–15.2 |
| A0 / loud | 10.0–26.9 | 2.2–6.5 |
| A0 / near_max | 20.2–45.4 | 1.3–3.2 |
| A1 / background | 3.1–5.7 | 10.1–21.0 |
| A1 / normal | 4.9–13.9 | 4.2–13.1 |
| A1 / loud | 11.1–32.0 | 1.8–5.8 |
| A1 / near_max | 22.2–53.7 | 1.1–2.9 |

Laufzeiten setzen 58–65 Wh nutzbar voraus. Keine Entladekurve, Zelltemperatur oder Alterung modelliert. A1-Wandler-Idle 0,3 W ist eine zusätzliche ungemessene E01-Annahme. Gleiche mittlere elektrische Audioleistung bedeutet nicht gleichen akustischen Nutzpegel.

A0 vermeidet den Wandler und bleibt erste Referenz, überschreitet aber den 300-EUR-Materialansatz. A1 bietet mehr modellierten Tiefbass, gefährdet das 11-kg-Ziel und benötigt Wandler-/Packprüfung. Beide benötigen gemessene Polaren, DSP-Schutz, thermische Prüfung und konkrete Schutzbauteile. Keine endgültige Konzeptauswahl.

Pack-Spitzenrechnung: `pack_stress.csv` löst eine hypothetische Konstantleistungsbelastung mit 0,05/0,2 Ohm Packwiderstand. Unterspannungsfälle sind Ausfallindikatoren; 15 V ist kein freigegebener Zellschutzwert. 75 W Audio ist nur ein Versorgungs-Stressfall, keine sichere HF-Dauerleistung.
