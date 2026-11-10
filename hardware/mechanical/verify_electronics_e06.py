"""Actual BRep mounting collisions and sampled service extraction, then exports."""
import adsk.core,adsk.fusion,json,math,sys,hashlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E06'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import electronics
def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E06'
    tm=adsk.fusion.TemporaryBRepManager.get()
    items=[(o.component.name,b) for o in root.occurrences for b in o.component.bRepBodies if b.isLightBulbOn]
    bounds={b.entityToken:(b.boundingBox.minPoint.asArray(),b.boundingBox.maxPoint.asArray()) for n,b in items}
    numerical=[]
    def intersect(a,b):
        aa=a.boundingBox;lo,hi=bounds[b.entityToken]
        if not all(aa.maxPoint.asArray()[i]>lo[i]+1e-7 and hi[i]>aa.minPoint.asArray()[i]+1e-7 for i in range(3)):return 0
        clone=tm.copy(a)
        if not tm.booleanOperation(clone,b,adsk.fusion.BooleanTypes.IntersectionBooleanType):numerical.append(b.name);return 0
        return clone.volume if clone.isValid and clone.faces.count else 0
    pairs=[]
    for i,(name,a) in enumerate(items):
        if not name.startswith('E06_'):continue
        for other,b in items:
            if a==b:continue
            if other.startswith('E06_') and other<name:continue
            volume=intersect(a,b)
            if volume>1e-6:pairs.append(dict(first=name,second=other,overlap_cm3=volume))
    moving_prefix=('E06_removable_tray','E06_JAB3_PCB','E06_PCB_')
    moving=[(n,b) for n,b in items if n.startswith(moving_prefix)]
    # Four tray-top screws removed first; support standoffs remain attached to floor.
    samples=[]
    for displacement in (0,.015,.030,.060,.100,.150):
        hits=[]
        matrix=adsk.core.Matrix3D.create();matrix.translation=adsk.core.Vector3D.create(0,0,displacement*100)
        for n,b in moving:
            tool=tm.copy(b);assert tm.transform(tool,matrix)
            for other,fixed in items:
                if other.startswith(moving_prefix) or other.startswith(('Rear_removable','E06_tray_top_','E05_cable_')):continue
                vol=intersect(tool,fixed)
                if vol>1e-6:hits.append(dict(moving=n,fixed=other,overlap_cm3=vol))
        samples.append(dict(rearward_displacement_m=displacement,hits=hits))
    issues=[]
    for i in range(d.timeline.count):
        ft=d.timeline.item(i)
        if ft.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append(dict(name=ft.name,error=ft.errorOrWarningMessage))
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));calc=electronics.calculate(data)
    report=dict(revision='E06',new_mount_interferences=pairs,service_extraction_samples=samples,timeline_issues=issues,numerical_failures=numerical,
        thread_stacks=calc['thread_engagement_m'],opposing_screw_tip_gaps_m=calc['screw_tip_gap_m'],
        limitations=['Extraction samples are not continuous swept-volume proof.','Rear cover and four tray-top screws removed, all cables disconnected.','Actual component/connector envelope, PCB thickness, keepouts and thermal path still require verification.'])
    (OUT/'mount_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));assert not pairs and not issues and not numerical
    assert not any(r['hits'] for r in samples),'Service extraction obstructed'
    assert all(v>=.003 for v in calc['thread_engagement_m'].values())
    em=d.exportManager
    assert em.execute(em.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E06.step'),root))
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E06.f3d')))
    # Actual horizontal tray face gives drill DXF, not just its envelope.
    tray=next(o.component for o in root.occurrences if o.component.name=='E06_removable_tray_112x90x2')
    face=max((f for b in tray.bRepBodies for f in b.faces if f.geometry.surfaceType==adsk.core.SurfaceTypes.PlaneSurfaceType and abs(f.geometry.normal.y)>.999),key=lambda f:f.area)
    sk=tray.sketches.add(face);sk.name='E06_tray_drill_template_DRAFT';sk.isLightBulbOn=False
    assert sk.saveAsDXF(str(OUT/'E06_tray_112x90x2_DRAFT.dxf'))
    floor=next(o.component for o in root.occurrences if o.component.name=='Service_floor')
    for sk in floor.sketches:
        if sk.name.startswith('E06_tray_'):assert sk.saveAsDXF(str(OUT/(sk.name+'.dxf')))
    hidden=[]
    for o in root.occurrences:
        if o.component.name in ('Side_right','Rear_removable','Top'):hidden.append(o);o.isLightBulbOn=False
    cam=app.activeViewport.camera;cam.eye=adsk.core.Point3D.create(90,78,105);cam.target=adsk.core.Point3D.create(16.5,35,20);cam.upVector=adsk.core.Vector3D.create(0,1,0);cam.isFitView=True;cam.isSmoothTransition=False
    app.activeViewport.camera=cam;app.activeViewport.refresh();assert app.activeViewport.saveAsImageFile(str(OUT/'electronics_inside.png'),1400,1000)
    for o in hidden:o.isLightBulbOn=True
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E06.f3d')))
    manifest=dict(fusion_version=app.version,input_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'data/parameters.json',ROOT/'hardware/mechanical/build_electronics_e06.py',ROOT/'hardware/mechanical/electronics.py']})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
