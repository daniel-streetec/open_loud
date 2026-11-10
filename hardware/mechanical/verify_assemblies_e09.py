"""Check all E09 maintenance ownership and unchanged part volumes/placements."""
import adsk.core,adsk.fusion,json,sys
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E09'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from assemblies import classify
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    structure=json.loads((ROOT/'data/assembly_structure_E09.json').read_text(encoding='utf-8'))
    prior=json.loads((OUT/'inventory_mass.json').read_text(encoding='utf-8'))
    expected={r['component']:r for r in prior['items']};seen=set();checks=[];identity=adsk.core.Matrix3D.create().asArray()
    for o in root.allOccurrences:
        cp=o.component
        if not cp.bRepBodies.count:continue
        name=cp.name;assert name in expected and name not in seen;seen.add(name)
        parent='/'.join(seg.rsplit(':',1)[0] for seg in o.fullPathName.split('+')[:-1])
        assert parent==classify(name,structure),(name,parent)
        assert max(abs(a-b) for a,b in zip(o.transform2.asArray(),identity))<1e-9,name
        volume=sum(b.volume for b in cp.bRepBodies)*1e-6
        assert abs(volume-expected[name]['body_volume_m3'])<1e-10,name
        checks.append(dict(component=name,assembly=parent))
    assert seen==set(expected)
    for entry in structure['assemblies']:
        cp=next(o.component for o in root.allOccurrences if o.component.name==entry['path'].split('/')[-1])
        cp.attributes.add('OPEN_LOUD','assembly_role',entry['role'])
    issues=[d.timeline.item(i).name for i in range(d.timeline.count) if d.timeline.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    assert not issues,issues
    report=dict(status='passed',parts=len(seen),groups=len(structure['assemblies']),ownership=checks,unchanged_volumes_and_identity_placements=True,
        limitations=['Assembly ownership verification, not proof of physical extraction with all cables connected.','BG43 converter is separate from removable tray; retention anchors remain missing.'])
    (OUT/'assembly_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'parts':len(seen),'groups':len(structure['assemblies']),'status':'passed'}))
