"""Actual discrete rearward battery extraction: a clash disproves that service path."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E08')
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));tm=adsk.fusion.TemporaryBRepManager.get()
    occurrences=list(d.rootComponent.allOccurrences)
    battery=next(o for o in occurrences if o.component.name=='E08_Battery_EREMIT_50Ah_BMS')
    base=tm.copy(battery.component.bRepBodies.item(0));assert tm.transform(base,battery.transform2)
    fixed=[]
    for o in occurrences:
        name=o.component.name
        if not o.component.bRepBodies.count or o==battery:continue
        if any(s in o.fullPathName for s in ('BG30_Service_Rueckwand','BG62_Akkuhalterung','BG90_Referenzraeume','BG80_Externes_Ladegeraet')):continue
        for b in o.component.bRepBodies:
            if not b.isLightBulbOn:continue
            tool=tm.copy(b);assert tm.transform(tool,o.transform2);fixed.append((name,tool))
    samples=[]
    for mm in range(0,201,5):
        moving=tm.copy(base);matrix=adsk.core.Matrix3D.create();matrix.translation=adsk.core.Vector3D.create(0,0,mm*.1);assert tm.transform(moving,matrix)
        aa=moving.boundingBox;hits=[]
        for name,b in fixed:
            bb=b.boundingBox
            if not all(aa.maxPoint.asArray()[k]>bb.minPoint.asArray()[k]+1e-6 and bb.maxPoint.asArray()[k]>aa.minPoint.asArray()[k]+1e-6 for k in range(3)):continue
            clone=tm.copy(moving);assert tm.booleanOperation(clone,b,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if clone.isValid and clone.faces.count and clone.volume>1e-5:hits.append(dict(part=name,overlap_cm3=clone.volume))
        samples.append(dict(rearward_mm=mm,hits=hits))
        if hits:break
    report=dict(status='BLOCKED' if samples[-1]['hits'] else 'sampled_path_clear',samples=samples,
        assumptions=['Rear cover and its screws removed, straps/pad released, battery leads disconnected.'],
        limitations=['A sampled collision disproves this straight path; no alternative rotation/tilt path has been established.','Nominal case, not actual terminals or tolerance stack.'])
    (OUT/'battery_service_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
