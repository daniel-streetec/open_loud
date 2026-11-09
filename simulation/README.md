# LF- und Versorgungsmodell E01

`python simulation/run.py` erzeugt CSV, JSON und Markdown in results/. Nur Python-Standardbibliothek, keine Installation erforderlich. Vorher `python -m unittest discover -s tests -v`, nachher `python tools/check_outputs.py`. Alle Einheiten der Parameterbasis sind explizit, intern SI. Eingangsspannung/-strom und komplexe Geschwindigkeit RMS, Hub/Portgeschwindigkeit Peak. Ein Treiber pro Basszweig.

## Gleichungen und Gültigkeit

Nach Bericht S. 8: Cms=1/(ws² Mms), Cab=Vb/(rho c²), Map=1/(wb² Cab), Zp=Map(wb/Qp+jw), Zbox=1/(jwCab+wbCab/Ql+1/Zp). Geschlossen ausschließlich Cab. Zm=Rms+j(wMms−1/wCms)+Sd² Zbox. I=V/(Re+BL²/Zm), v=BL I/Zm. Up=−Sd v Zbox/Zp. p=j rho w(Sd v+Up)/(2 pi r). Le standardmäßig null wie Bericht; keine nicht belegte frequenzunabhängige Hersteller-Sensitivity auf die LF-Kurve addiert.

Halbraum bedeutet idealisierte starre Bodenfläche und kohärente Quell-/Spiegelquellen. Kein zusätzlicher 6-dB-Bodenbonus auf diese Ergebnisse. Leckfluss wird im Modell dissipiert und nicht als zweite Schallquelle addiert. Port- und Konusabstände/Strahlungsimpedanzen fehlen. Interpretation ungefähr bis 200–250 Hz, keine Systemantwort bis 20 kHz. Normierung als arithmetisches dB-Mittel der logarithmisch verteilten Stützstellen 180–250 Hz; F3/6/10 als letzte aufwärts gerichtete Kreuzung unter 180 Hz.

Pro Frequenz kleinste Grenze aus 0,9 Rail/sqrt(2), vorläufiger 14,142-V-RMS-Boardkappung, geometrischem Xmax, 17-m/s-Port-Peak und sqrt(Pn/Re)/|I bei 1 V|. Pn aus AES-Rating ist **keine belegte Kupfer-Dauerverlustgrenze**; dieser Proxy reproduziert nur den Bericht. CSV weist ihn als solchen aus. Reale Eingangsleistung Re{V I*}, Kupferverlust |I|² Re. Keine HF- oder Gesamtsystem-Grenzpegelprognose.

Keine DSP-Filter aktiv: CSV zeigt den bei voller Rail angeforderten Hub separat. Die frequenzweise optimale Spannung ist eine Hüllkurve für Einzelsinus, kein gleichzeitig erreichbares Musiksignal und kein implementierter Limiter. Warmes Re, Parameterstreuung, Nichtlinearität, Portgeräusch, Gitter, Schallwand, Kompression, HF, Verzerrung und Bauteiltemperaturen fehlen. Xmax enthält Hersteller-Gapzuschlag und ist kein Nachweis niedriger THD.

Portlänge Leff=Map S/rho; Lphys≈Leff−0,73 d_eq. Runde Endkorrektur auf noch nicht konstruierten Schlitzport nur als Näherung. Kanalwände/Flares und deren Volumen fehlen. CAD muss alle Verdrängungen gegen Vb bilanzieren.

## Referenzen und Sensitivität

Tests vergleichen die geschlossene Netzwerkantwort mit einer unabhängig formulierten klassischen Hochpassfunktion zweiter Ordnung, Helmholtzfrequenz aus Geometrie und elektrische Wirkleistung mit Kupfer-/Aufhängungs-/Port-/Leckverlusten. Dazu 1/r-Abstandsfall und bekannte Packlast. Dies sind analytische Implementierungsprüfungen, keine externe Validierung der BR-Annahmen. Ein unabhängiger BR-Simulator und Messungen bleiben Prüftore. Ql/Rail-Sweep in sensitivity.csv; T/S-Konsistenz in summary.json. Unbekannte Herstellertoleranzen werden nicht durch erfundene Prozentwerte ersetzt.

## Energie

Pdirect=Pidle+Paux+Paudio/eta_incremental. Pboost=Pdirect/eta_boost+Pboost_idle. Laufzeit [58 Wh/Pmax, 65 Wh/Pmin]. Gesamte mittlere elektrische Audioleistung beider Kanäle; keine direkte Zuordnung zum Regler oder SPL. Vier Profile aus Bericht S. 10. Wirkungsgrad und Idle sind ungemessen bzw. nur berichtet; Wandler-Idle 0,3 W zusätzlich angenommener Prüfpunkt. Extremkombinationen bilden ein Szenariointervall, kein statistisches Konfidenzband. Nutzbare Wh pauschal; Abschaltpunkt, Last, Temperatur und Alterung können den Bereich verlassen.

Spitzenlast als separater elektrischer Stressfall, nicht aus einem behaupteten Crestfaktor abgeleitet. P=I(Voc−IR); stabile Lösung V=(Voc+sqrt(Voc²−4RP))/2, I=P/V. Widerstände 0,05–0,2 Ohm sind hypothetisch. 15-V-UVLO nur Prüfwert; weder Zellschutz noch Hysterese implementiert. Kein BMS-/Sicherungsrating aus diesen Zahlen ableiten. Nahe UVLO ist Konstantleistung für A0 pessimistisch, da dessen Ausgangsleistung mit Rail fällt.

## Artefakte und Reproduktion

manifest.json enthält SHA256 der Eingabedaten, Rechenquellen und des Nutzer-PDF sowie Pythonversion. results/validation.json wird nur nach erfolgreichem Audit geschrieben. Tests separat ausführen. Kein Zeitstempel im Generator, sodass unveränderte Quellen bei gleicher Pythonversion identische Ergebnisse erzeugen. Optionale PDF-Extraktion: `.tools/python` mit pypdf 6.12.0; keine Laufzeitabhängigkeit des Modells. Fremde PDF-Anlagen wurden gelesen, nicht ausgeführt oder in den Modellcode kopiert.
