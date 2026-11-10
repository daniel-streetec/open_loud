"""Persist a truthful E09 handoff only after the actual geometry/export gates pass."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/exports/E09'
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
v=load('power_validation.json');a=load('assembly_validation.json');b=load('battery_continuous_envelope.json');e=load('export_validation.json');mass=load('inventory_mass.json')
assert not any(v[k] for k in ('interferences','kernel_failures','timeline_issues'))
assert a['status']=='passed' and a['parts']==228 and a['groups']==22
assert b['status']=='passed_for_assumed_envelope' and not b['hits']
assert all(r['status']=='passed' for r in e['checks']) and e['native_hierarchy_preserved']
lo,hi=mass['partial_subtotal_kg']
note=f'''## E09 – neuer geprüfter CAD-Zwischenstand, 2026-11-10

Aktives Fusion-Dokument `OPEN_LOUD_A0_E09_PowerSystem`; E08 separat erhalten und wegen blockiertem Akku-Auszug gesperrt. **E09-Eingaben sind `data/experiments/E09_parameters.json`**. `data/parameters.json` bleibt bewusst E08-Referenz. Nicht beide vermischen oder E09 durch unbedachtes Aufrufen alter Skripte überschreiben. Details/Befehle in `docs/build/E09_status.md`.

E09: aufrechter Akku90° gedreht,22mm angehoben, neue echte Bodenauflagen und rechte Kammerwand, Dach240mm, Träger180×102mm, angepasste Leitungen/Durchführungen und interner Ladehalter.228 Teile in22 geprüften Gruppen,8 Hauptgruppen. Durchgehender konservativer Akku-Box-Sweep227mm inklusive Pad, Polreserve14mm und2mm Zugaben an freien Flächen bestanden; untere Padfläche ist Auflagedatum. Statische Kernelprüfung0 Treffer/Fehler, native/STEP-Rückimporte einschließlich nativer Hierarchie bestanden. Dies ist kein Nachweis für reale, noch unvermessenene Pole/Stecker/Griffe. Alte Teil-/Gehäuseexporte im E09-Ordner sind Vorgeschichte; `*_checkpoint.f3d/step` ist der vollständige aktuelle Stand.

20 Tests bestanden; Zahlenreproduktion doppelt byte-identisch. E09-Versorgung berücksichtigt warme Kabel/Kontakte, hypothetischen Verpolschutzverlust, LF-Re-Sensitivität und HF-Mindestimpedanz. Vorläufig LF10,5/HF10Vrms, nicht aufgespielte DSP-Ziele; Wandlerreserve≈10,35%, etwa23W Wandlerwärme plus konservativ32W Verstärkerwärme. Geschlossene Holzkammer thermisch nicht qualifiziert. Offline-DSP40HzBW4 +2,5kHzLR4: nominal3,14mm Hub,8,87m/s Port,F6≈61Hz; keine akustische HF-Abstimmung/Messung. Echte PNG/SVG/PDF-Plots in results/dsp/E09 wurden zweimal byte-identisch gerendert, PDF und Bild geprüft. Optionale Toolversionen unter tools/requirements-visual.txt.

**Massenproblem:** bereits {lo:.2f}–{hi:.2f}kg für Holz+Akku+LF+HF+Horn+Wandler; Stahl, Kabel, Gitter, Trage-/Schutzteile/Lack fehlen. Frühe10kg/300EUR werden verfehlt. Nicht als fertiges tragbares Produkt ausgeben. Leichtes außenverleimtes Sperrholz/Hybridbau und Größen-/Energievergleich gezielt prüfen, ohne Reststege oder Montagestellen zu schwächen.

Nächste konstruktive Priorität: tatsächliche lösbare Batterie-Pigtails mit packnaher Sicherung/Polschutz und greifbarer Trennstelle. XT90S-Paar von AMASS für4,05EUR/1–2Tage endkundentauglich verifiziert, noch nicht modelliert. M6-Ringösen nicht erst unter dem engen Dach abschrauben müssen. Reale Klemmenhalter, Zugentlastungen, Sicherungshalterfixierung, Gurtanker und Horn-/Treiberbefestigung ergänzen. Pololu5389 noch nicht eingebaut; Schalter und thermischer Pfad offen. Fertige AdamHall4072-Ecken als Endkundenkandidat dokumentiert, noch keine Bohrungen/Radiusänderung ohne geprüfte Zeichnung. Quellen/Angebote in data/procurement_E09_additions.json und docs/build/service_connections_E09.md.

Wichtig aus dieser Sitzung: verschachtelte Occurrence-Proxys ließen beim Löschen alte Instanzen stehen; korrekt über nativeObject löschen und Rückgabewert prüfen. Ein suffigiertes altes XT60-Teil wurde zusätzlich entfernt. Finale228-Teile-/Eigentums-/Kollisionsprüfung ist danach bestanden. Neue Baugruppenänderungen bewusst rekursiv ausführen; alte flache Mutatoren nicht blind wiederholen. Kein Scheduler, keine unautorisierte Lizenzänderung/Bestellung; weitere selbstständige Entwicklung und Push sind beauftragt.

'''
for name in ('docs/NEXT_SESSION.md','docs/DEVELOPMENT.md'):
    p=ROOT/name;s=p.read_text(encoding='utf-8')
    if not s.startswith('## E09 – neuer'):p.write_text(note+s,encoding='utf-8')
p=ROOT/'docs/CHANGELOG.md';s=p.read_text(encoding='utf-8')
entry='## E09 2026-11-10 – Montagepfad und konservative Versorgung\n\nNeuer Akku-/Kammeraufbau, durchgehender Hüllraum-Auszug geprüft, Ladehalter/Kabelkollisionen behoben und228 Teile in22 Gruppen organisiert. Native/STEP-Rückimporte bestanden. Warme Versorgungsrechnung und Offline-DSP-Schutzsweep mit wissenschaftlichen PDF/SVG/PNG-Plots,20 Tests. Masse/Kühlung und unvollständige Anschlüsse ausdrücklich offen; keine Fertigungsfreigabe.\n\n'
if not s.startswith('## E09 2026'):p.write_text(entry+s,encoding='utf-8')
sources=[ROOT/'data/experiments/E09_parameters.json',ROOT/'data/assembly_structure_E09.json',ROOT/'data/experiments/E09_dsp_draft.json']+sorted((ROOT/'hardware/mechanical').glob('*e09.py'))
sources += [ROOT/'hardware/mechanical'/name for name in ('cad_parts.py','electronics.py','layout.py','assemblies.py')]
sources += [ROOT/'tools'/name for name in ('prepare_e09_cad.py','prepare_e09_assembly_stages.py','run_e09_stages.py','requirements-visual.txt')]
sources += sorted((ROOT/'tools').glob('*e09.py'))+[ROOT/'simulation/filters.py',ROOT/'simulation/model.py',ROOT/'data/verification/orion_mount.json']
manifest=dict(revision='E09',status='checked_development_checkpoint_not_product_release',
    inputs={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='checkpoint_manifest.json'})
(OUT/'checkpoint_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'revision':'E09','parts':a['parts'],'continuous_sweep':'passed','partial_mass_kg':[lo,hi]}))
