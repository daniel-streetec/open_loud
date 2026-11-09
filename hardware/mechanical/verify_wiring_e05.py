"""Kernel cable collision test, fastener tool corridors, real exports and manifest."""
import adsk.core,adsk.fusion,json,math,hashlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E05'

def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','wiring_ready').value=='E05'
    tm=adsk.fusion.TemporaryBRepManager.get();P=adsk.core.Point3D.create
    def pt(a):return P(*(v*100 for v in a))
    def cyl(a,b,r):return tm.createCylinderOrCone(pt(a),r*100,pt(b),r*100)
    items=[(o.component.name,b) for o in root.occurrences for b in o.component.bRepBodies if b.isLightBulbOn]
    numerical=[]
    def intersections(tool,excluded):
        result=[];a=tool.boundingBox
        for name,b in items:
            if any(name.startswith(s) for s in excluded):continue
            bb=b.boundingBox
            if not all(a.maxPoint.asArray()[i]>bb.minPoint.asArray()[i]+1e-7 and bb.maxPoint.asArray()[i]>a.minPoint.asArray()[i]+1e-7 for i in range(3)):continue
            copy=tm.copy(tool)
            if not tm.booleanOperation(copy,b,adsk.fusion.BooleanTypes.IntersectionBooleanType):numerical.append(name);continue
            if copy.isValid and copy.faces.count and copy.volume>1e-6:result.append(dict(component=name,volume_cm3=copy.volume))
        return result
    cable_hits={}
    for key in ('power','lf','hf'):
        hits=[]
        for n,b in items:
            if n=='E05_cable_'+key:hits+=intersections(tm.copy(b),('E05_cable_'+key,))
        cable_hits[key]=hits
    d=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));m={k:v['value'] for k,v in d['mechanical'].items()};f={k:v['value'] for k,v in d['fasteners'].items()}
    tool_checks=[]
    for i in range(8):
        a=i*math.pi/4;x=m['width']/2+m['lf_pcd']/2*math.cos(a);y=m['lf_y']+m['lf_pcd']/2*math.sin(a)
        z=2*m['wall']+m['lf_backing_thickness']+f['m5_washer_h']+f['m5_nut_h']+.0002
        start=[x,y,z];stub=[x,y,z+.018];entry=[x,.280 if y>.330 else .200 if y<.160 else y,.320]
        ex=('E05_LF_'+str(i),'Rear_removable','E05_Rear_')
        direct=intersections(cyl(start,[x,y,.320],.0055),ex)
        alt=intersections(cyl(start,stub,.0055),ex)+intersections(cyl(stub,entry,.006),ex)
        angle=math.degrees(math.atan2(abs(y-entry[1]),entry[2]-stub[2]))
        tool_checks.append(dict(index=i,straight_obstructions=direct,articulated_obstructions=alt,angle_deg=angle,accepted=not direct or(not alt and angle<=25)))
    issues=[]
    for i in range(design.timeline.count):
        e=design.timeline.item(i)
        if e.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append(dict(name=e.name,message=e.errorOrWarningMessage))
    report=dict(revision='E05',cable_intersections=cable_hits,LF_nut_socket_checks=tool_checks,timeline_issues=issues,numerical_failures=numerical,
        solids=sum(b.isSolid for n,b in items),scope='Nominal cable jackets; no slack loops or actual OEM terminal ends. Mounting contact and threaded engagement are intentional.',
        electrical_release=False,assembly_release=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'assembly_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
    assert not numerical and not issues
    assert not any(cable_hits.values()),'Resolve cable clashes before export'
    assert all(x['accepted'] for x in tool_checks),'LF nut tooling blocked'
    def camera(eye,path):
        cam=app.activeViewport.camera;cam.eye=P(*eye);cam.target=P(16.5,28,15);cam.upVector=adsk.core.Vector3D.create(0,1,0);cam.isFitView=True;cam.isSmoothTransition=False
        app.activeViewport.camera=cam;app.activeViewport.refresh();assert app.activeViewport.saveAsImageFile(str(OUT/path),1400,1000)
    camera((85,75,-100),'front.png')
    hidden=[]
    for o in root.occurrences:
        if o.component.name in ('Side_right','Rear_removable','Top'):hidden.append(o);o.isLightBulbOn=False
    camera((95,70,110),'inside.png')
    for o in hidden:o.isLightBulbOn=True
    camera((85,75,-100),'overview.png')
    # Changed panels: through-hole face plus counterbore sketch, separately named.
    for name in ('Service_floor','Service_partition'):
        cp=next(o.component for o in root.occurrences if o.component.name==name)
        for sk in cp.sketches:
            if sk.name.startswith('E05_'):assert sk.saveAsDXF(str(OUT/(name+'_'+sk.name+'.dxf')))
    em=design.exportManager
    assert em.execute(em.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E05.step'),root))
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E05.f3d')))
    sources=['data/parameters.json','hardware/mechanical/build_wiring_e05.py','hardware/mechanical/verify_wiring_e05.py','tools/generate_wiring.py','hardware/mechanical/exports/E03/OPEN_LOUD_A0_E03.f3d']
    manifest=dict(sources={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},fusion_version=app.version,
        exports={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.suffix in ('.step','.f3d','.dxf','.png')})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
