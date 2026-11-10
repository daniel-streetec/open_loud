"""Temporary-body service study; active E08 model remains untouched."""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));F=cad_parts.Parts(d.rootComponent);tm=F.tm
    study=json.loads((ROOT/'data/experiments/E09_packaging.json').read_text(encoding='utf-8'));p=study['battery_mount']
    tol=study['planning_tolerance_each_face_m'];origin=[x-tol for x in p['battery_origin']];size=[x+2*tol for x in p['battery_size']];size[1]+=study['terminal_zone_height_m']
    base=F.box(origin,size);fixed=[]
    for o in d.rootComponent.allOccurrences:
        name=o.component.name
        if name in ('E08_Battery_front_wall','E08_Battery_left_wall','E08_Battery_roof'):continue
        if any(n in o.fullPathName for n in ('BG30_Service_Rueckwand','BG60_Akkuversorgung','BG90_Referenzraeume','BG80_Externes_Ladegeraet','BG50_Kabelbaum')):continue
        for b in o.component.bRepBodies:
            if b.isLightBulbOn:
                clone=tm.copy(b);assert tm.transform(clone,o.transform2);display_name=name
                if name.startswith(('E08_BAT_232_','E08_BAT_260_')):
                    idx=0 if name.startswith('E08_BAT_232_') else 1
                    old_x=.232 if idx==0 else .260;new_x,new_z=study['battery_roof_feed_xz'][idx]
                    matrix=adsk.core.Matrix3D.create();matrix.translation=adsk.core.Vector3D.create((new_x-old_x)*100,2,(new_z-.315)*100);assert tm.transform(clone,matrix)
                    display_name='STUDY_RELOCATED_'+name
                fixed.append((display_name,clone))
    left=p['bay_left'];right=p['bay_right'];front=p['bay_front'];top=p['bay_top'];wall=.012
    fixed.append(('STUDY_front_wall',F.box([left,wall,front],[right-left,top-2*wall,wall])))
    for name,x in [('left',left),('right',right-wall)]:
        body=F.box([x,wall,front+wall],[wall,top-2*wall,.328-front-wall])
        F.subtract(body,F.box([x-.001,.011,.308],[.014,.021,.021]));fixed.append(('STUDY_'+name+'_wall',body))
    fixed.append(('STUDY_roof',F.box([left,top-wall,front],[right-left,wall,.328-front])))
    rows=[]
    for mm in range(0,226,5):
        moving=tm.copy(base);m=adsk.core.Matrix3D.create();m.translation=adsk.core.Vector3D.create(0,0,mm*.1);assert tm.transform(moving,m)
        aa=moving.boundingBox;hits=[]
        for name,b in fixed:
            bb=b.boundingBox
            if not all(aa.maxPoint.asArray()[i]>bb.minPoint.asArray()[i]+1e-6 and bb.maxPoint.asArray()[i]>aa.minPoint.asArray()[i]+1e-6 for i in range(3)):continue
            test=tm.copy(moving);assert tm.booleanOperation(test,b,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if test.isValid and test.faces.count and test.volume>1e-5:hits.append(dict(part=name,overlap_cm3=test.volume))
        rows.append(dict(rearward_mm=mm,hits=hits))
    report=dict(status='sampled_study_clear' if not any(r['hits'] for r in rows) else 'study_blocked',samples=rows,
        case_tolerance_each_face_m=tol,terminal_zone_included_m=study['terminal_zone_height_m'],active_CAD_modified=False,
        exclusions=['E08 bay walls replaced with proposed temporary walls/roof; roof glands translated into right corridor','Rear cover removed','Old battery/pad/straps and charge/fuse hardware to be relocated','Disconnected harness; E09 routes not yet built'],
        limitations=['Discrete positions, not continuous swept-volume proof.','Proposed walls are temporary BReps only; new platform, fittings and wiring not built.','Tolerances and terminal reserve are assumptions; real supplier interfaces need verification.'])
    out=ROOT/'results/service';out.mkdir(exist_ok=True)
    (out/'E09_battery_service_study.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'samples':len(rows),'hits':sum(len(r['hits']) for r in rows),'active_CAD_modified':False}))
