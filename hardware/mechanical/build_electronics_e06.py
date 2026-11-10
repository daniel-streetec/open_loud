"""Clone E05 and add removable electronics tray, real M3 counterpieces and PCB.
No assumed battery or connector-pin geometry is silently made into a released part.
"""
import adsk.core,adsk.fusion,json,math,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E06'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import electronics;importlib.reload(electronics)
def run(_context: str):
    app=adsk.core.Application.get();target='OPEN_LOUD_A0_E06_Electronics'
    assert not any(d.name.startswith(target) for d in app.documents),'Inspect existing E06 before rebuilding'
    doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(str(ROOT/'hardware/mechanical/exports/E05/OPEN_LOUD_A0_E05.f3d')))
    assert doc;doc.name=target;design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));p=electronics.values(data['electronics_mount']);m=electronics.values(data['mechanical']);layout=electronics.calculate(data)
    root.attributes.add('OPEN_LOUD','revision','E06');tm=adsk.fusion.TemporaryBRepManager.get();P=adsk.core.Point3D.create;V=adsk.core.ValueInput.createByString
    def pt(a):return P(*(v*100 for v in a))
    def box(origin,size):
        center=[a+b/2 for a,b in zip(origin,size)]
        return tm.createBox(adsk.core.OrientedBoundingBox3D.create(pt(center),adsk.core.Vector3D.create(1,0,0),adsk.core.Vector3D.create(0,1,0),*(v*100 for v in size)))
    def cyl(x,z,y0,y1,r):return tm.createCylinderOrCone(pt([x,y0,z]),r*100,pt([x,y1,z]),r*100)
    def diff(a,b):assert tm.booleanOperation(a,b,adsk.fusion.BooleanTypes.DifferenceBooleanType);return a
    def hexy(x,z,y,h,af):
        body=cyl(x,z,y,y+h,af/math.sqrt(3))
        for angle in (0,math.pi/3,2*math.pi/3):
            slab=tm.createBox(adsk.core.OrientedBoundingBox3D.create(pt([x,y+h/2,z]),adsk.core.Vector3D.create(math.cos(angle),0,math.sin(angle)),adsk.core.Vector3D.create(0,1,0),af*100,h*100,af*200))
            assert tm.booleanOperation(body,slab,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return body
    counts={};added=[]
    def comp(name,bodies,part,status='nominal_mounting_candidate'):
        cp=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;cp.name='E06_'+name
        cp.attributes.add('OPEN_LOUD','part',part);cp.attributes.add('OPEN_LOUD','status',status)
        base=cp.features.baseFeatures.add();base.startEdit()
        for i,b in enumerate(bodies):assert b and b.isSolid;item=cp.bRepBodies.add(b,base);item.name=cp.name+'_'+str(i)
        base.finishEdit();counts[part]=counts.get(part,0)+1;added.append(cp.name);return cp
    def washer(name,x,z,y):
        body=diff(cyl(x,z,y,y+p['washer_thickness'],p['washer_od']/2),cyl(x,z,y-.001,y+.002,p['washer_id']/2))
        comp(name,[body],'ISO7089_M3')
    def spacer(name,x,z,y):
        body=diff(hexy(x,z,y,p['spacer_length'],p['spacer_af']),cyl(x,z,y-.001,y+p['spacer_length']+.001,p['screw_diameter']/2))
        comp(name,[body],'WURTH_970100321','manufacturer_dimensions_nominal_thread_envelope')
    def bolt(name,x,z,under,length,sign):
        lo=min(under,under-sign*.003);head=cyl(x,z,lo,lo+.003,.00275)
        recess=lo-.0001 if sign>0 else lo+.0014
        diff(head,hexy(x,z,recess,.0017,.0025));shaft=cyl(x,z,under,under+sign*length,.0015)
        assert tm.booleanOperation(head,shaft,adsk.fusion.BooleanTypes.UnionBooleanType)
        comp(name,[head],f'ISO4762_M3x{round(length*1000)}')
    old=next(o.component for o in root.occurrences if o.component.name=='RESERVE_amp_wiring_UNVERIFIED_no_mounting_holes')
    for b in old.bRepBodies:b.isLightBulbOn=False
    tray=box(p['tray_origin'],p['tray_size']);ty=p['tray_origin'][1];t=p['tray_size'][1]
    for x,z in layout['support_centres_m']:diff(tray,cyl(x,z,ty-.001,ty+t+.001,p['tray_support_bore']/2))
    for x,z in layout['pcb_hole_centres_m']:diff(tray,cyl(x,z,ty-.001,ty+t+.001,p['tray_pcb_bore']/2))
    comp('removable_tray_112x90x2',[tray],'OWN_AL_TRAY_112_90_2')
    board=box(layout['board_origin_m'],[p['pcb_width'],p['pcb_thickness'],p['pcb_depth']]);by=layout['board_origin_m'][1]
    for x,z in layout['pcb_hole_centres_m']:diff(board,cyl(x,z,by-.001,by+p['pcb_thickness']+.001,p['pcb_hole']/2))
    comp('JAB3_PCB_mounting_outline',[board],'WONDOM_AA_JA32173','manufacturer_outer_dimensions_holes; board_thickness_assumed')
    envelope=comp('RESERVE_JAB3_components_NOT_ACTUAL_GEOMETRY',[box([layout['board_origin_m'][0],by+p['pcb_thickness'],layout['board_origin_m'][2]],[p['pcb_width'],p['pcb_total_height']-p['pcb_thickness'],p['pcb_depth']])],'JAB3_COMPONENT_KEEP_OUT','component_positions_unverified')
    for b in envelope.bRepBodies:b.isLightBulbOn=False
    for i,(x,z) in enumerate(layout['support_centres_m']):
        spacer(f'tray_support_{i}',x,z,m['service_floor_y']+m['wall'])
        washer(f'floor_bottom_washer_{i}',x,z,m['service_floor_y']-p['washer_thickness'])
        bolt(f'floor_bottom_M3x16_{i}',x,z,m['service_floor_y']-p['washer_thickness'],p['floor_screw_length'],1)
        washer(f'tray_top_washer_{i}',x,z,ty+t)
        bolt(f'tray_top_M3x6_{i}',x,z,ty+t+p['washer_thickness'],p['small_screw_length'],-1)
    for i,(x,z) in enumerate(layout['pcb_hole_centres_m']):
        spacer(f'PCB_support_{i}',x,z,ty+t)
        washer(f'PCB_bottom_washer_{i}',x,z,ty-p['washer_thickness'])
        bolt(f'PCB_bottom_M3x6_{i}',x,z,ty-p['washer_thickness'],p['small_screw_length'],1)
        washer(f'PCB_top_washer_{i}',x,z,by+p['pcb_thickness'])
        bolt(f'PCB_top_M3x6_{i}',x,z,by+p['pcb_thickness']+p['washer_thickness'],p['small_screw_length'],-1)
    floor=next(o.component for o in root.occurrences if o.component.name=='Service_floor')
    for i,(x,z) in enumerate(layout['support_centres_m']):
        pin=floor.constructionPlanes.createInput();pin.setByOffset(floor.xZConstructionPlane,V(f"{m['service_floor_y']*1000} mm"));plane=floor.constructionPlanes.add(pin);plane.isLightBulbOn=False
        sk=floor.sketches.add(plane);sk.name=f'E06_tray_support_M3_{i}'
        c=sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(pt([x,m['service_floor_y'],z])),p['floor_bore']*50);c.isFixed=True
        inp=floor.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f"{m['wall']*1000} mm")),adsk.fusion.ExtentDirections.PositiveExtentDirection);inp.participantBodies=list(floor.bRepBodies)
        floor.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
    design.computeAll();OUT.mkdir(parents=True,exist_ok=True)
    report=dict(revision='E06',document=doc.name,added_components=added,inventory=counts,layout=layout,
        limitations=['JAB component/connector layout and PCB thickness not manufacturer CAD; thermal clearance unqualified.','Legacy cable stations unchanged, actual pigtails and clamps remain unfinished.','No battery or weatherproofing release.'])
    (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'new_components':len(added),'inventory':counts}))
