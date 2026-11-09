# OPEN//LOUD

Tragbarer DIY-Outdoor-Lautsprecher. Entwicklungsstand: **Vorentwurf, keine Bau- oder Sicherheitsfreigabe**.

Startpunkt ist der vom Nutzer bereitgestellte [Forschungsbericht](docs/research/OPEN_LOUD_Forschungsbericht_Phase_1.pdf). Seine Empfehlungen und Zahlen sind Prüfgrundlagen. Es liegen noch keine eigenen Messungen vor.

- [Bestandsaufnahme und Anforderungen](docs/requirements.md)
- [Entwicklungsplan und Sitzungsübergabe](docs/DEVELOPMENT.md)
- [Aktueller Arbeitsplan und exakter Fortsetzungsstand](docs/NEXT_SESSION.md)
- [Verkabelung, Strom-/Querschnittsrechnung und Schrauben E05](docs/build/wiring.md)
- [Festivalversorgung im Vergleich – USB ausdrücklich optional](results/battery/comparison.md)
- [Autorisierter Wiederanlauf nach Kontingentreset](docs/automation/README.md)
- [CAD-basierter Zeichnungssatz E05: 25 Teile, Gesamtansicht, Explosion und Schraubenaufbauten](hardware/mechanical/drawings/E05/README.md)
- [Modell und Grenzen](simulation/README.md)
- [Generierter Konzeptvergleich](results/comparison.md)
- [Quellen und Verifikation](docs/sources.md)
- [Entscheidungen und Risiken](docs/decisions.md)
- [Lizenzvorbereitung](licenses/README.md)
- [Fusion-Konstruktion E03 mit STEP/F3D und Montagefolge](hardware/mechanical/README.md)

Reproduzieren ab Repositorywurzel mit Python 3.13, ohne Zusatzpakete:

```powershell
python -m unittest discover -s tests -v
python simulation/run.py
python tools/check_outputs.py
```

Alles mit Abbruch bei Fehler und zusätzlichem Vergleich zweier Generierungsläufe: `python tools/reproduce.py`.

`data/parameters.json` ist die zentrale numerische Parameterbasis. `data/components.json` enthält Beschaffungs- und Freigabedaten. Ergebnisse sind generiert und dürfen nicht von Hand korrigiert werden. Keine Bestellung, Veröffentlichung oder Lizenzänderung wurde vorgenommen.
