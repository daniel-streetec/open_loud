"""Kernel check new power/cable geometry and save a reviewable E09 checkpoint."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E09'
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    tm=adsk.fusion.TemporaryBRepManager.get();items=[]
    for o in root.allOccurrences:
        for b in o.component.bRepBodies:
            if not b.isLightBulbOn:continue
            if 'RESERVE' in o.component.name or 'EXTERNAL' in o.component.name:continue
            body=tm.copy(b);tm.transform(body,o.transform2)
            items.append((o.component.name,body))
    hits=[];failures=[]
    for i,(name,a) in enumerate(items):
        if not name.startswith(('E09_','E06_')):continue
        if 'strap' in name.lower() or 'buckle' in name.lower():continue
        aa=a.boundingBox
        for j,(other,b) in enumerate(items):
            if i==j or name==other:continue
            if other.startswith(('E09_','E06_')) and j<i:continue
            bb=b.boundingBox
            if not all(aa.maxPoint.asArray()[k]>bb.minPoint.asArray()[k]+1e-6 and bb.maxPoint.asArray()[k]>aa.minPoint.asArray()[k]+1e-6 for k in range(3)):continue
            clone=tm.copy(a)
            if not tm.booleanOperation(clone,b,adsk.fusion.BooleanTypes.IntersectionBooleanType):
                failures.append([name,other]);continue
            if clone.isValid and clone.faces.count and clone.volume>1e-5:
                hits.append(dict(a=name,b=other,volume_cm3=clone.volume))
    issues=[]
    for i in range(d.timeline.count):
        f=d.timeline.item(i)
        if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append(dict(name=f.name,message=f.errorOrWarningMessage))
    report=dict(status='screening_not_release',interferences=hits,kernel_failures=failures,timeline_issues=issues,
        exclusions=['Same-component geometry','Reference reserves','Strap and buckle envelopes; retention not released'],
        limitations=['Envelope geometry and provisional terminal stations; actual supplier models and extraction remain to verify.'])
    (OUT/'power_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    em=d.exportManager
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E09_checkpoint.f3d')))
    print(json.dumps({'interferences':len(hits),'kernel_failures':len(failures),'timeline_issues':len(issues),'export':'checkpoint_not_release'}))
