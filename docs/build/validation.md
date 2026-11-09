# Prototypenprüfplan – Entwurf, keine Montagefreigabe

Grundlage Bericht S. 13–14. Messgeräte, Kalibrierung, Umgebung, Signal, Abstand, Akkuzustand und Hardware-/DSP-Revision bei jeder Messung speichern. Es gibt noch keine Messergebnisse.

| Prüfung | Messbares Kriterium / Freigabetor |
|---|---|
| T/S und Impedanz | Zwei Wiederholungen vor/nach Konditionierung; ZMA archivieren; Fb A0 50±2 Hz, A1 48±2 Hz |
| Frequenzgang | A0 F6≤63 Hz; A1≤52 Hz; Bezug 180–250 Hz wie Modell zusätzlich dokumentieren; 100 Hz–10 kHz ±3 dB auf Achse nach 1/6-Oktavglättung |
| Hörfenster | H/V 10-Grad-Raster; bis ±30 Grad H kein zusätzlicher Einbruch >5 dB bei 1–4 kHz |
| Grenzpegel | 40/50/63/80/100 Hz, dann ab 125 Hz; 2–3-dB-Schritte; Abbruch >1 dB Kompression, THD >10% unter 100 Hz oder >3% darüber, Clip oder Portgeräusch; erste Ursache erfassen |
| A1-Mehrwert | ≥2 dB bei 50 Hz gegen A0 bei gleicher Messgeometrie und dokumentierter Versorgung |
| Energie | Wh bis kontrollierter Abschaltung integrieren; alle vier Lastprofile, Idle, Spitzen, Wiederanlauf und Temperatur loggen; kein Mindestlaufzeitziel festgelegt |
| Versorgung | Keine Überschreitung dokumentierter Board-/Pack-/Ladergrenzen; Schutz am Adapter nachweisen; konkreter Sicherungs-/UVLO-Testplan nach Komponentenwahl |
| Masse | Vollständige Box inklusive Akku/Gurten wiegen: A0≤10 kg, A1≤11 kg |
| Tragen | Erste statische Prüfung mit gesicherter Testmasse 2× Zielgewicht; keine Person darunter; Wiederholungszahl/Dauer vor Versuch festlegen, noch kein vollständiger Nachweis |
| Regen | Zunächst stromlose Benetzung und Inneninspektion, Drainage; keine IP-Angabe ohne passende Prüfung |

Vorläufige Reihenfolge: Bauteilidentitäten prüfen → akustisches Testgehäuse ohne Akku vermessen → strombegrenzter elektrischer Prüfstand → Schutz- und DSP-Funktion → tragbarer Prototyp → Thermik/Tragen/Feuchte. Detaillierte Verdrahtung, Montage und Fertigungsunterlagen erst nach geschlossenen Prüftoren. BTL-Ausgänge nicht miteinander oder mit geerdetem Oszilloskop-Masseanschluss verbinden (Bericht S. 9).
