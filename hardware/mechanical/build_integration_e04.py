"""Clone own E03 archive, add E04 mounting, wiring and protective candidates.
New integration geometry is regenerated from versioned SI parameters. Its base
features are not linked live to Fusion user-parameter edits; regenerate to change.
"""
import adsk.core, adsk.fusion
import json, math, sys, importlib
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
OUT=ROOT/'hardware/mechanical/exports/E04'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import layout as layout_module, integration as integration_module
importlib.reload(layout_module);importlib.reload(integration_module)

def run(_context: str):
    raise RuntimeError("E04 exterior rejected by user. Do not rebuild; use saved E03 baseline and verified purchased parts.")
    app=adsk.core.Application.get();target='OPEN_LOUD_A0_E04_Integration'
    existing=[d for d in app.documents if d.name.startswith(target)]
    if existing:
        doc=existing[0];doc.activate()
    else:
        options=app.importManager.createFusionArchiveImportOptions(str(ROOT/'hardware/mechanical/exports/E03/OPEN_LOUD_A0_E03.f3d'))
        doc=app.importManager.importToNewDocument(options);assert doc
        doc.name=target
    design=adsk.fusion.Design.cast(app.activeProduct);root=design.rootComponent
    assert not any(o.component.name.startswith('E04_') for o in root.occurrences),'E04 already built; inspect instead of duplicating'
    root.attributes.add('OPEN_LOUD','revision','E04')
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    layout=layout_module.calculate(data);screen=integration_module.calculate(data)
    m=layout['dimensions'];p={k:v['value'] for k,v in data['integration'].items()}
    V=adsk.core.ValueInput.createByString;P=adsk.core.Point3D.create
    for key in ('lf_backing_inner_d',):design.userParameters.itemByName(key).expression=f'{m[key]*1000:.12g} mm'
    design.userParameters.itemByName('service_z').expression=f"{layout['service_z']*1000:.12g} mm"
    design.userParameters.itemByName('backing_displacement').expression=f"{layout['backing_displacement']*1e9:.12g} mm^3"
    # All original source dimensions remain editable, but E04 additions regenerate from JSON.
    for key,r in data['integration'].items():
        if isinstance(r['value'],(int,float)) and r['unit']=='m':
            design.userParameters.add('e04_'+key,V(f"{r['value']*1000:.12g} mm"),'mm',r['source']+'; regenerate E04 additions after changes')
    design.computeAll()
    tm=adsk.fusion.TemporaryBRepManager.get()
    def point(x):return P(*(v*100 for v in x))
    def box(origin,size):
        center=[a+b/2 for a,b in zip(origin,size)]
        obb=adsk.core.OrientedBoundingBox3D.create(point(center),adsk.core.Vector3D.create(1,0,0),adsk.core.Vector3D.create(0,1,0),*(v*100 for v in size))
        return tm.createBox(obb)
    def cyl(a,b,r):return tm.createCylinderOrCone(point(a),r*100,point(b),r*100)
    def difference(body,tool):
        assert tm.booleanOperation(body,tool,adsk.fusion.BooleanTypes.DifferenceBooleanType)
        return body
    def component(name,bodies,kind='prototype_candidate'):
        occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());cp=occ.component;cp.name='E04_'+name
        cp.attributes.add('OPEN_LOUD','status',kind)
        base=cp.features.baseFeatures.add();base.startEdit()
        for i,b in enumerate(bodies):
            item=cp.bRepBodies.add(b,base);item.name=cp.name+'_'+str(i+1)
        base.finishEdit()
        return cp
    def cut_profile(cp,axis,at,length,name,diameter=None,size=None):
        index='xyz'.index(axis)
        baseplane={'x':cp.yZConstructionPlane,'y':cp.xZConstructionPlane,'z':cp.xYConstructionPlane}[axis]
        sign=1 if axis!='y' else -1
        pin=cp.constructionPlanes.createInput();pin.setByOffset(baseplane,V(f'{at[index]*1000*sign:.12g} mm'))
        plane=cp.constructionPlanes.add(pin);plane.isLightBulbOn=False
        sk=cp.sketches.add(plane);sk.name=name
        first=sk.modelToSketchSpace(point(at))
        if diameter:
            circle_=sk.sketchCurves.sketchCircles.addByCenterRadius(first,diameter*50);circle_.isFixed=True
        else:
            opposite=list(at)
            for j in range(3):
                if j!=index:opposite[j]+=size[j]
            second=sk.modelToSketchSpace(point(opposite))
            lines=sk.sketchCurves.sketchLines.addTwoPointRectangle(first,second)
            for line in lines:line.isFixed=True
        inp=cp.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        direction=adsk.fusion.ExtentDirections.PositiveExtentDirection if sign>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f'{length*1000:.12g} mm')),direction)
        inp.participantBodies=list(cp.bRepBodies)
        cp.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
    def cut_circle(cp,axis,at,diameter,length,name):cut_profile(cp,axis,at,length,name,diameter=diameter)
    def cut_box(cp,origin,size,name):
        index=min(range(3),key=lambda i:size[i])
        cut_profile(cp,'xyz'[index],origin,size[index],name,size=size)
    def named(name):return next(o.component for o in root.occurrences if o.component.name==name)
    # Replace the optimistic single-frustum LF envelope with a conservative lip + taper.
    lf=named('REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE')
    for b in lf.bRepBodies:b.isLightBulbOn=False
    center=[m['width']/2,m['lf_y']]
    rear=m['lf_depth']-m['lf_flange']-m['lf_magnet_depth']
    basket=[cyl([*center,0],[*center,p['basket_lip_depth']],m['lf_basket_d']/2),
            tm.createCylinderOrCone(point([*center,p['basket_lip_depth']]),m['lf_basket_d']*50,point([*center,rear]),m['lf_magnet_d']*50),
            cyl([*center,rear],[*center,m['lf_depth']-m['lf_flange']],m['lf_magnet_d']/2)]
    component('LF_conservative_basket_envelope',basket,'clearance_reference_assumed_profile_not_manufacturer_CAD')
    old=named('RESERVE_amp_wiring_UNVERIFIED_no_mounting_holes')
    for b in old.bRepBodies:b.isLightBulbOn=False
    # Fixed front-access M4 thread plates behind the horn and grille.
    nut_positions=[]
    for ix in (-1,1):
        for iy in (-1,1):nut_positions.append(('horn',m['width']/2+ix*m['horn_bolt_pitch']/2,m['horn_y']+iy*m['horn_bolt_pitch']/2))
    for x in (.023,m['width']-.023):
        for y in (.100,.410,.500):nut_positions.append(('grille',x,y))
    for i,(kind,x,y) in enumerate(nut_positions):
        w=p['horn_nut_plate_width'];h=p['horn_nut_plate_height'];t=p['horn_nut_plate_thickness'];z=2*m['wall']
        body=box([x-w/2,y-h/2,z],[w,h,t])
        difference(body,cyl([x,y,z-.001],[x,y,z+t+.001],.0033/2))
        for dy in (-.008,.008):difference(body,cyl([x,y+dy,z-.001],[x,y+dy,z+t+.001],.003/2))
        component(f'{kind}_M4_thread_plate_{i}',[body],'M4_tap_candidate_3p3mm_pilot_not_thread_geometry')
    baffle=named('Baffle');lamination=named('Baffle_inner_lamination')
    for i,(kind,x,y) in enumerate(nut_positions):
        if kind=='grille':
            for cp,z in [(baffle,0),(lamination,m['wall'])]:cut_circle(cp,'z',[x,y,z],.0045,m['wall'],'Grille_M4_clearance')
    # Service tray, verified PCB envelope, and mounting standoffs.
    tray=box(p['tray_origin'],p['tray_size']);pcb_origin=p['pcb_origin']
    pcb=box(pcb_origin,[p['pcb_width'],p['pcb_height'],p['pcb_total_depth']])
    pcb_holes=[]
    for dx in ((p['pcb_width']-p['pcb_hole_pitch_x'])/2,(p['pcb_width']+p['pcb_hole_pitch_x'])/2):
        for dy in ((p['pcb_height']-p['pcb_hole_pitch_y'])/2,(p['pcb_height']+p['pcb_hole_pitch_y'])/2):
            x=pcb_origin[0]+dx;y=pcb_origin[1]+dy;pcb_holes.append([x,y])
            difference(pcb,cyl([x,y,pcb_origin[2]-.001],[x,y,pcb_origin[2]+p['pcb_total_depth']+.001],p['pcb_hole_d']/2))
            difference(tray,cyl([x,y,.189],[x,y,.194],.0032/2))
    for x in (.040,.150):
        for y in (.380,.475):difference(tray,cyl([x,y,.189],[x,y,.194],.0032/2))
    component('electronics_tray',[tray])
    for i,(x,y) in enumerate(( (x,y) for x in (.040,.150) for y in (.380,.475) )):
        start=layout['service_z']+m['wall']
        stand=cyl([x,y,start],[x,y,.190],.003)
        difference(stand,cyl([x,y,start-.001],[x,y,.191],.0015));component('tray_mount_standoff_'+str(i),[stand],'blind_insert_mounting_candidate_thread_engagement_to_validate')
    component('REF_JAB3_manufacturer_assembly_envelope',[pcb],'manufacturer_outline_height_holes_verified_internals_unmodeled')
    for i,(x,y) in enumerate(pcb_holes):
        stand=cyl([x,y,.193],[x,y,.200],.003)
        difference(stand,cyl([x,y,.192],[x,y,.201],.0015));component('PCB_standoff_'+str(i),[stand])
    component('RESERVE_UVLO_reverse_polarity',[box([.180,.410,.200],[.045,.060,.025])],'unqualified_module_installation_reserve')
    component('RESERVE_fuse_switch_distribution',[box([.250,.450,.200],[.045,.040,.025])],'unqualified_module_installation_reserve')
    # The gland thread fits a thin plate with seal/nut, not a 12mm wooden floor.
    floor=named('Service_floor')
    cut_box(floor,p['bulkhead_opening_origin'],p['bulkhead_opening_size'],'Cable_bulkhead_opening')
    plate=box(p['bulkhead_plate_origin'],p['bulkhead_plate_size'])
    for x in (.240,.280):difference(plate,cyl([x,.362,.2125],[x,.367,.2125],.0125/2))
    for x in (.220,.300):
        for z in (.195,.230):difference(plate,cyl([x,.362,z],[x,.367,z],.0032/2))
    component('sealed_speaker_bulkhead_plate',[plate])
    for i,x in enumerate((.240,.280)):
        body=cyl([x,.366,.2125],[x,.388,.2125],p['gland_body_d']/2)
        difference(body,cyl([x,.365,.2125],[x,.389,.2125],p['speaker_cable_od']/2))
        thread=cyl([x,.358,.2125],[x,.366,.2125],p['gland_thread_d']/2)
        difference(thread,cyl([x,.357,.2125],[x,.367,.2125],p['speaker_cable_od']/2))
        nut=cyl([x,.355,.2125],[x,.358,.2125],p['gland_nut_size']/2)
        difference(nut,cyl([x,.354,.2125],[x,.359,.2125],p['gland_thread_d']/2))
        component('speaker_gland_'+str(i),[body,thread,nut],'LAPP_family_envelope_nut_is_wrench_reserve')
    # Side entry has a removable thin plate and a downward-open rain hood.
    side=named('Side_right');cut_box(side,[m['width']-m['wall'],.405,.205],[m['wall'],.070,.050],'Side_bulkhead_opening')
    plate=box(p['side_plate_origin'],p['side_plate_size'])
    difference(plate,cyl([.331,.420,.230],[.336,.420,.230],.0125/2));component('side_power_entry_plate',[plate])
    body=cyl([.335,.420,.230],[.357,.420,.230],p['gland_body_d']/2);difference(body,cyl([.334,.420,.230],[.358,.420,.230],p['power_cable_od']/2))
    thread=cyl([.327,.420,.230],[.335,.420,.230],p['gland_thread_d']/2);difference(thread,cyl([.326,.420,.230],[.336,.420,.230],p['power_cable_od']/2))
    nut=cyl([.329,.420,.230],[.332,.420,.230],p['gland_nut_size']/2);difference(nut,cyl([.328,.420,.230],[.333,.420,.230],p['gland_thread_d']/2))
    component('power_entry_gland',[body,thread,nut],'LAPP_family_envelope_nut_is_wrench_reserve')
    ox,oy,oz=p['side_hood_origin'];sx,sy,sz=p['side_hood_size'];t=p['hood_wall']
    component('side_rain_hood',[box([ox,oy+sy-t,oz],[sx,t,sz]),box([ox,oy,oz],[sx,sy-t,t]),box([ox,oy,oz+sz-t],[sx,sy-t,t]),box([ox+sx-t,oy,oz+t],[t,sy-t,sz-2*t])],'downward_open_splash_shield_not_watertight_enclosure')
    # Smooth routes are explicit jacket envelopes; endpoints remain service tails.
    for kind,route in screen['routes'].items():
        points=route['sampled_points_m'];radius=p['power_cable_od' if kind=='power' else 'speaker_cable_od']/2
        bodies=[cyl(a,b,radius) for a,b in zip(points,points[1:]) if integration_module.norm(integration_module.sub(b,a))>1e-8]
        component('cable_'+kind,bodies,'round_jacket_route_final_terminal_positions_unverified')
        # 3D centreline is convenient for review without treating jacket bodies as wiring pins.
        sk=root.sketches.add(root.xYConstructionPlane);sk.name='E04_route_'+kind;sk.is3D=True
        for a,b in zip(points,points[1:]):
            if integration_module.norm(integration_module.sub(b,a))>1e-8:sk.sketchCurves.sketchLines.addByTwoPoints(point(a),point(b))
        sk.isLightBulbOn=False
    # Cabinet corners have rear-face relief, so they do not capture the removable cover.
    W,H,D=m['width'],m['height'],m['depth'];L=p['corner_leg'];t=p['corner_thickness'];lip=p['rear_guard_lip']
    def local_box(corner,sign,origin,size):
        a=[corner[i]+sign[i]*origin[i] for i in range(3)];b=[corner[i]+sign[i]*(origin[i]+size[i]) for i in range(3)]
        return box([min(a[i],b[i]) for i in range(3)],[abs(b[i]-a[i]) for i in range(3)])
    for ix in (0,1):
        for iy in (0,1):
            for iz in (0,1):
                corner=[W*ix,H*iy,D*iz];sign=[-1 if k else 1 for k in (ix,iy,iz)]
                specs=[([-t,0,0],[t,L,L]),([-t,-t,0],[L+t,t,L])]
                if iz:specs += [([-t,-t,-t],[lip+t,L+t,t]),([lip,-t,-t],[L-lip,lip+t,t])]
                else:specs += [([-t,-t,-t],[L+t,L+t,t])]
                component(f'corner_guard_{ix}{iy}{iz}',[local_box(corner,sign,*s) for s in specs],'own_TPU_prototype_guard_no_impact_UV_or_load_rating')
    # Twelve edge profiles stop short of the corner guards. Rear lip remains outside cover.
    t=p['edge_thickness'];leg=p['edge_leg'];gap=p['rail_end_gap']
    for ix in (0,1):
        for iz in (0,1):
            c=[W*ix,0,D*iz];s=[-1 if ix else 1,1,-1 if iz else 1];rear_lip=lip if iz else leg
            component(f'vertical_edge_{ix}{iz}',[local_box(c,s,[-t,L+gap,0],[t,H-2*(L+gap),leg]),local_box(c,s,[0,L+gap,-t],[rear_lip,H-2*(L+gap),t])],'edge_profile_candidate_seal_cut_ends')
    for iy in (0,1):
        for iz in (0,1):
            c=[0,H*iy,D*iz];s=[1,-1 if iy else 1,-1 if iz else 1];rear_lip=lip if iz else leg
            component(f'horizontal_edge_{iy}{iz}',[local_box(c,s,[L+gap,-t,0],[W-2*(L+gap),t,leg]),local_box(c,s,[L+gap,0,-t],[W-2*(L+gap),rear_lip,t])],'edge_profile_candidate_seal_cut_ends')
    for ix in (0,1):
        for iy in (0,1):
            c=[W*ix,H*iy,0];s=[-1 if ix else 1,-1 if iy else 1,1]
            component(f'depth_edge_{ix}{iy}',[local_box(c,s,[-t,0,L+gap],[t,leg,D-2*(L+gap)]),local_box(c,s,[0,-t,L+gap],[leg,t,D-2*(L+gap)])],'edge_profile_candidate_seal_cut_ends')
    for x in (.045,W-.075):
        for z in (.045,D-.075):component('foot_'+str(x)+'_'+str(z),[box([x,-p['feet_height'],z],[.030,p['feet_height'],.030])],'rubber_foot_candidate_not_load_rated')
    # Grille: square wire envelopes, not an acoustically tested supplier mesh.
    gx,gy,gz=p['front_grille_origin'];gw,gh=p['front_grille_size'];f=p['grille_frame_width'];wire=p['mesh_wire'];pitch=p['mesh_pitch']
    mesh=[box([gx,gy,gz],[f,gh,3*wire]),box([gx+gw-f,gy,gz],[f,gh,3*wire]),box([gx+f,gy,gz],[gw-2*f,f,3*wire]),box([gx+f,gy+gh-f,gz],[gw-2*f,f,3*wire])]
    nx=int((gw-2*f)/pitch)+1;ny=int((gh-2*f)/pitch)+1
    for i in range(nx):mesh.append(box([gx+f+i*pitch,gy+f,gz+wire],[wire,gh-2*f,wire]))
    for i in range(ny):mesh.append(box([gx+f,gy+f+i*pitch,gz+2*wire],[gw-2*f,wire,wire]))
    component('front_grille_mesh_candidate',mesh,'own_wire_envelopes_64percent_ideal_open_area_no_supplier_mesh_claim')
    for x in (.018,W-.028):
        for y in (.095,.405,.495):
            stand=box([x,y,gz+3*wire],[.010,.010,-gz-3*wire]);difference(stand,cyl([x+.005,y+.005,gz],[x+.005,y+.005,.001],.0045/2))
            component('grille_standoff_'+str(x)+'_'+str(y),[stand])
    # Baffled, downward-open port cover; free outlet is checked independently.
    hx,hy,hz=p['port_hood_origin'];hw,hh,hd=p['port_hood_size'];t=p['hood_wall']
    component('port_splash_hood',[box([hx,hy,hz],[hw,hh,t]),box([hx,hy+hh-t,hz+t],[hw,t,hd-t]),box([hx,hy,hz+t],[t,hh-t,hd-t]),box([hx+hw-t,hy,hz+t],[t,hh-t,hd-t])],'removable_hood_bracket_detail_and_acoustic_loss_to_validate')
    # Rear drip cap is above, not across, the rear cover's extraction path.
    t=.002;over=p['rain_drip_cover_depth']
    component('rear_drip_cap',[box([-.003,H+.003,D-.010],[W+.006,t,over+.010]),box([-.003,H-.009,D+over-t],[W+.006,.012,t])],'drip_deflector_not_IP_seal')
    root.attributes.add('OPEN_LOUD','integration_ready','E04')
    design.computeAll();OUT.mkdir(parents=True,exist_ok=True)
    info={'revision':'E04','document':doc.name,'source_archive':'exports/E03/OPEN_LOUD_A0_E03.f3d','fusion_version':app.version,
          'integration_source':'data/parameters.json:integration','screening':{k:v for k,v in screen.items() if k!='routes'},
          'pcb_source':'WONDOM manufacturer datasheet AA-JA32173 p3, distributor-hosted copy; internals not modeled',
          'notes':['New E04 base features regenerate from source; not live-driven by Fusion user parameter edits.',
                   'Battery holder, UVLO and reverse-polarity circuitry are still unresolved.',
                   'No IP or real assembly/fit claim from nominal CAD alone.']}
    (OUT/'build.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'document':doc.name,'new_components':sum(o.component.name.startswith('E04_') for o in root.occurrences),'screening':info['screening']}))
