"""Write current handoff only after actual assembly/kernel/export checks pass."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/exports/E08'
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
v=read('power_validation.json');a=read('assembly_validation.json');e=read('export_validation.json')
assert not v['interferences'] and not v['kernel_failures'] and not v['timeline_issues']
assert a['status']=='passed' and a['parts']==225
assert {r['format'] for r in e['checks'] if r['status']=='passed'}=={'native','STEP'}
note='''## E08 – Montagehalter und Baugruppen geprüft, 2026-11-10

**Neu erkannter Montageblocker:** Der echte E08-Akku stößt beim geraden Wartungsauszug schon bei5mm an feste Gewindeplatten. Bericht `exports/E08/battery_service_validation.json`. E08 deshalb nicht fertigen. E09-Vorschlag in `data/experiments/E09_packaging.json`: aufrecht um90° gedrehter,22mm angehobener Akku, angepasste Kammer/Plattform/Träger und verlegte Durchführungen. Temporärer Kernelversuch mit2mm zusätzlichem Hüllraum pro Fläche und14mm Polreserve:46 Positionen bis225mm Auszug ohne Treffer (`results/service/E09_battery_service_study.json`). Dies ist eine geprüfte Studie, noch kein gebautes E09-CAD. Als Nächstes vollständig umsetzen, dann sämtliche Anschluss-/Montageprüfungen wiederholen. Kein bloßes Null-Kollisions-Ergebnis mit Montierbarkeit verwechseln.

Neuester Stand ersetzt die unmittelbar folgenden historischen E08-Notizen: Ladebuchsenhalter mit M3-Durchsteckmontage ergänzt, dazu bemaßtes eigenes PDF/SVG-Prüfblatt. Offizielles Orion-STEP lokal importiert, 2-mm-Montageohren und vier freie Ø8-mm-Werkzeugräume geprüft. Daraus eigene konservative Hülle korrigiert; keine fremden Solids publiziert. `data/verification/orion_mount.json` und `licenses/external_material_E08.json` enthalten Herkunft/Hash und Umfang.

225 Teile in22 eindeutig geprüften Gruppen; Einzelvolumina/Platzierungen unverändert. Acht Hauptgruppen einschließlich Akku und externem Ladegerät. BG43-Wandler ist unabhängig von BG41/BG42-Träger zu warten. Aktuelle Kernelprüfung nach Reparenting:0 Überschneidungen im dokumentierten Umfang,0 Kernel-/Timelinefehler; keine vollständige Montierbarkeits- oder Produktfreigabe. F3D-/STEP-Rückimporte bestanden und Fusion gespeichert. Neuaufbau-/Prüfreihenfolge in `docs/build/E08_reproduction.md`; flache Ergänzungsskripte nach Gruppierung nicht blind erneut aufrufen.

17 Rechentests und doppelte byte-identische Reproduktion bestanden. CAD-basierte Modell-BOM erzeugt:65 Positionen,58 Einheitskosten offen; keine vollständige Einkaufsliste. Wichtiger Zielkonflikt:17,02–18,60kg bereits für Holz/Akku/LF/Wandler, weitere Teile fehlen. Noch keine bestätigte leichte Holzplatte auswählen; Vergleich in `docs/build/material_mass_E08.md`. Vier Versorgungskaufteile bereits338,02EUR ohne Versand und Restprodukt. Frühe10kg/300EUR nicht erfüllt.

Prioritäten weiter selbstständig abarbeiten: reale Klemmenhalter/Zugentlastungen, Sicherungshalterbefestigung, Gurtanker, Polabdeckungen und vollständige Anschlussstellen; passende Schutz-/Schaltkette und Kühlung. Pololu5389 ist neue technische Verpolschutzvorauswahl, noch nicht eingebaut. EXP-Tech/Botland.store als geprüfte B2B-Quellen ausgeschlossen; Eckstein-Angebot mit Lieferlandhinweis noch verifizieren. Danach Material-/Massenoptimierung mit belastbaren Reststegen und Montagestellen, Kabelschlaufen/Extraktion, vollständige BOM/Zeichnungen/Explosionen und Akustik-/DSP-Absicherung. Alte Berichte bleiben historische Entwicklungsnachweise. Kein Scheduler aktivieren, keine neue Lizenz festlegen; weitere Arbeit und Push sind beauftragt.

'''
for name in ('docs/NEXT_SESSION.md','docs/DEVELOPMENT.md'):
    p=ROOT/name;s=p.read_text(encoding='utf-8')
    if not s.startswith('## E08 – Montagehalter'):p.write_text(note+s,encoding='utf-8')
p=ROOT/'docs/build/power_E08.md';s=p.read_text(encoding='utf-8')
prefix='> Neuester Montage-/Prüfstand: [E08 Reproduktion](E08_reproduction.md). Die unten historisch genannten acht Orion-Hüllkonflikte sind nach Hersteller-STEP-Prüfung behoben; aktuelle Kernelprüfung meldet0 im dokumentierten Umfang. Material-/Massenkonflikt siehe [Massenstudie](material_mass_E08.md).\n\n'
if not s.startswith('> Neuester Montage'):p.write_text(prefix+s,encoding='utf-8')
