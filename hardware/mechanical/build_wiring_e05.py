"""Clone checked E03; add internal harness, feedthroughs and standard fasteners.
New base geometry regenerates from JSON; it is not live-linked to Fusion edits.
Thread cylinders are clearance envelopes; OEM connector/terminal positions pending.
"""
import adsk.core,adsk.fusion
import json,math,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E05'
sys.path.insert(0,str(ROOT/'tools'))
import generate_wiring;importlib.reload(generate_wiring)

def run(_context: str):
    app=adsk.core.Application.get()
    assert not any(d.name.startswith('OPEN_LOUD_A0_E05') for d in app.documents),'E05 already open; inspect before rebuilding'
    doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(str(ROOT/'hardware/mechanical/exports/E03/OPEN_LOUD_A0_E03.f3d')))
    assert doc;doc.name='OPEN_LOUD_A0_E05_WiringFasteners'
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    d=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    w={k:v['value'] for k,v in d['wiring'].items()};f={k:v['value'] for k,v in d['fasteners'].items()};m={k:v['value'] for k,v in d['mechanical'].items()}
    calc=generate_wiring.calculate(d)
    root.attributes.add('OPEN_LOUD','revision','E05')
    tm=adsk.fusion.TemporaryBRepManager.get();P=adsk.core.Point3D.create;V=adsk.core.ValueInput.createByString
    def pt(v):return P(*(x*100 for x in v))
    def cyl(a,b,r):return tm.createCylinderOrCone(pt(a),r*100,pt(b),r*100)
    def box(origin,size,angle=0):
        c=[a+b/2 for a,b in zip(origin,size)]
        return tm.createBox(adsk.core.OrientedBoundingBox3D.create(pt(c),adsk.core.Vector3D.create(math.cos(angle),math.sin(angle),0),adsk.core.Vector3D.create(-math.sin(angle),math.cos(angle),0),*(x*100 for x in size)))
    def boolean(a,b,kind):
        assert tm.booleanOperation(a,b,kind),'Boolean failed';return a
    def diff(a,b):return boolean(a,b,adsk.fusion.BooleanTypes.DifferenceBooleanType)
    def hexagon(x,y,z,h,af):
        body=cyl([x,y,z],[x,y,z+h],af/math.sqrt(3))
        for angle in (0,math.pi/3,2*math.pi/3):
            slab=box([x-af/2,y-af,z],[af,2*af,h],angle)
            boolean(body,slab,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return body
    added=[];inventory={}
    def comp(name,bodies,sku,status='nominal_standard_envelope_SKU_verification_pending'):
        cp=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;cp.name='E05_'+name
        cp.attributes.add('OPEN_LOUD','status',status);cp.attributes.add('OPEN_LOUD','part',sku)
        base=cp.features.baseFeatures.add();base.startEdit()
        for i,b in enumerate(bodies):
            assert b and b.isSolid and b.volume>0
            item=cp.bRepBodies.add(b,base);item.name=cp.name+'_'+str(i)
        base.finishEdit();added.append(cp.name);inventory[sku]=inventory.get(sku,0)+1
        return cp
    def washer(name,x,y,z,size):
        h=f[f'm{size}_washer_h'];od=.010 if size==5 else .009;id_=.0053 if size==5 else .0043
        b=diff(cyl([x,y,z],[x,y,z+h],od/2),cyl([x,y,z-.001],[x,y,z+h+.001],id_/2))
        comp(name,[b],f'ISO7089_M{size}')
    def nut(name,x,y,z,size):
        h=f[f'm{size}_nut_h'];af=.008 if size==5 else .007
        b=diff(hexagon(x,y,z,h,af),cyl([x,y,z-.001],[x,y,z+h+.001],size*.0005))
        comp(name,[b],f'{"ISO4032" if size==5 else "DIN934"}_M{size}')
    def screw(name,x,y,under,size,length,sign=1):
        h=f[f'm{size}_head_h'];hd=f[f'm{size}_head_d'];af=.004 if size==5 else .003
        lo=min(under,under-sign*h);hi=max(under,under-sign*h)
        head=cyl([x,y,lo],[x,y,hi],hd/2)
        recess_z=lo-.0001 if sign==1 else hi-h*.6
        diff(head,hexagon(x,y,recess_z,h*.6+.0002,af))
        shaft=cyl([x,y,under],[x,y,under+sign*length],size*.0005)
        boolean(head,shaft,adsk.fusion.BooleanTypes.UnionBooleanType)
        comp(name,[head],f'ISO4762_M{size}x{round(length*1000)}')
    # Existing holes: actual head, shaft, washers and hex nuts. No exterior armor.
    for i in range(8):
        a=i*math.pi/4;x=m['width']/2+m['lf_pcd']/2*math.cos(a);y=m['lf_y']+m['lf_pcd']/2*math.sin(a)
        washer(f'LF_{i}_front_washer',x,y,-m['lf_flange']-f['m5_washer_h'],5)
        screw(f'LF_{i}_M5x45',x,y,-m['lf_flange']-f['m5_washer_h'],5,f['lf_screw_length'])
        z=2*m['wall']+m['lf_backing_thickness'];washer(f'LF_{i}_rear_washer',x,y,z,5);nut(f'LF_{i}_nut',x,y,z+f['m5_washer_h'],5)
    for ix in (-1,1):
        for iy in (-1,1):
            x=m['width']/2+ix*m['horn_bolt_pitch']/2;y=m['horn_y']+iy*m['horn_bolt_pitch']/2;tag=f'HF_{ix}_{iy}'
            washer(tag+'_front_washer',x,y,-m['horn_flange']-f['m4_washer_h'],4)
            screw(tag+'_M4x40',x,y,-m['horn_flange']-f['m4_washer_h'],4,f['horn_screw_length'])
            washer(tag+'_rear_washer',x,y,2*m['wall'],4);nut(tag+'_nut',x,y,2*m['wall']+f['m4_washer_h'],4)
    rear=[(x,m['height']*v,False) for x in (m['wall']+m['rear_cleat_width']/2,m['width']-m['wall']-m['rear_cleat_width']/2) for v in (.15,.5,.85)]
    rear += [(m['width']*v,y,True) for y in (m['wall']+m['rear_cleat_width']/2,m['height']-m['wall']-m['rear_cleat_width']/2) for v in (.27,.73)]
    for i,(x,y,horizontal) in enumerate(rear):
        washer(f'Rear_{i}_washer',x,y,m['depth'],5);screw(f'Rear_{i}_M5x40',x,y,m['depth']+f['m5_washer_h'],5,f['rear_screw_length'],-1)
        for sign in (-1,1):
            xx=x+sign*m['rear_retainer_pitch']/2 if horizontal else x;yy=y if horizontal else y+sign*m['rear_retainer_pitch']/2
            z=m['depth']-m['wall']-m['rear_cleat_depth']-m['rear_plate_thickness']
            comp(f'Rear_{i}_retainer_{sign}',[cyl([xx,yy,z-.002],[xx,yy,z],.0025),cyl([xx,yy,z],[xx,yy,z+.012],.00125)],'wood_pan_2p5x12','purchase_candidate_head_envelope_not_threaded')
    def named(name):return next(o.component for o in root.occurrences if o.component.name==name)
    def cut(cp,axis,at,diameter,length,name):
        index='xyz'.index(axis);normal=1 # This Fusion build's xZ plane normal is +Y.
        base=cp.xYConstructionPlane if axis=='z' else cp.xZConstructionPlane
        pin=cp.constructionPlanes.createInput();pin.setByOffset(base,V(f'{at[index]*1000*normal:.12g} mm'));plane=cp.constructionPlanes.add(pin);plane.isLightBulbOn=False
        sk=cp.sketches.add(plane);sk.name=name
        c=sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(pt(at)),diameter*50);c.isFixed=True
        inp=cp.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f'{length*1000:.12g} mm')),adsk.fusion.ExtentDirections.PositiveExtentDirection if normal>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection)
        inp.participantBodies=list(cp.bRepBodies);cp.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
    service_z=design.userParameters.itemByName('service_z').value/100
    glands=[('LF','Service_floor','y',[.275,m['service_floor_y'],.240]),('HF','Service_partition','z',[.275,.460,service_z])]
    for tag,panel,axis,at in glands:
        cp=named(panel);idx='xyz'.index(axis)
        cut(cp,axis,at,w['gland_bore'],m['wall'],'E05_'+tag+'_M16_through')
        cut(cp,axis,at,w['gland_counterbore_diameter'],w['gland_counterbore_depth'],'E05_'+tag+'_inside_counterbore')
        # Envelope along feedthrough axis: 12mm thread, 28mm body, hollow cable bore.
        shoulder=list(at);shoulder[idx]+=m['wall']
        aa=list(shoulder);aa[idx]-=w['gland_thread_length'];bb=list(shoulder);bb[idx]+=.028
        thread=cyl(aa,shoulder,.008);shell=cyl(shoulder,bb,.011)
        tool_a=list(aa);tool_a[idx]-=.001;tool_b=list(bb);tool_b[idx]+=.001
        for body in (thread,shell):diff(body,cyl(tool_a,tool_b,.0037))
        comp(tag+'_M16_gland',[thread,shell],'LAPP_53017210','manufacturer_dimensions_simplified_shape_nut_seal_pending')
        nn=list(at);nn[idx]+=.002;ne=list(nn);ne[idx]+=.003
        lock=diff(cyl(nn,ne,.011),cyl(tool_a,tool_b,.008))
        comp(tag+'_gland_locknut',[lock],'M16x1p5_locknut','3mm_reserved_thickness_actual_PN_pending')
    for key,b in calc['branches'].items():
        pts=b['route_points_m'];radius=w['cable_diameter']/2
        # Separate overlapping round jacket segments avoid pretending to model conductors.
        bodies=[cyl(a,bb,radius) for a,bb in zip(pts,pts[1:]) if math.dist(a,bb)>1e-8]
        comp('cable_'+key,bodies,'Cordial_CLS215_'+key,'jacket_route_only_service_slack_and_OEM_ends_not_geometry')
        sk=root.sketches.add(root.xYConstructionPlane);sk.name='E05_centerline_'+key;sk.is3D=True
        for a,bb in zip(pts,pts[1:]):
            if math.dist(a,bb)>1e-8:sk.sketchCurves.sketchLines.addByTwoPoints(pt(a),pt(bb))
        sk.isLightBulbOn=False
    root.attributes.add('OPEN_LOUD','wiring_ready','E05')
    design.computeAll();OUT.mkdir(parents=True,exist_ok=True)
    report=dict(revision='E05',document=doc.name,base_archive='E03/OPEN_LOUD_A0_E03.f3d',added_components=added,modeled_inventory=inventory,
        notes=['Base features regenerate from JSON; not live Fusion parameters.','Thread envelopes intentionally intersect untapped pilot bores.','Cable end stations and service slack require physical routing; no electrical release.'])
    (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'document':doc.name,'added_components':len(added),'inventory':inventory}))
