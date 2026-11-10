"""Concrete E09 battery compartment, battery/BMS, converter, charger and hardware.
Purchase parts are own source-referenced envelope models; no foreign CAD is bundled.
"""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E09'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts,layout;importlib.reload(cad_parts);importlib.reload(layout)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    assert not any(o.component.name.startswith('E09_Battery_') for o in root.occurrences),'Power hardware already exists'
    data=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'));m={k:v['value'] for k,v in data['mechanical'].items()};p={k:v['value'] for k,v in data['battery_mount'].items()};calc=layout.calculate(data)
    F=cad_parts.Parts(root);V=adsk.core.ValueInput.createByString
    def named(n):return next(o.component for o in root.occurrences if o.component.name==n)
    # Remove just the old prototype gland features/envelopes before moving derived partition.
    for panel,prefix in [('Service_partition','E05_HF_'),('Service_floor','E05_LF_')]:
        cp=named(panel);cuts=[ft for ft in cp.features.extrudeFeatures if hasattr(ft.profile,'parentSketch') and ft.profile.parentSketch.name.startswith(prefix)]
        sketches=[ft.profile.parentSketch for ft in cuts]
        for ft in sorted(cuts,key=lambda q:q.timelineObject.index,reverse=True):ft.deleteMe()
        for sk in sketches:sk.deleteMe()
    for occ in [o for o in root.occurrences if o.component.name in ('E05_HF_M16_gland','E05_HF_gland_locknut','E05_LF_M16_gland','E05_LF_gland_locknut')]:occ.deleteMe()
    d.timeline.moveToEnd()
    for key in ('service_z','port_d','port_length'):
        d.userParameters.itemByName(key).expression=f'{calc[key]*1000:.12g} mm'
    for key,amount in [('battery_reserve',calc['battery_excluded']),('cleat_acoustic_displacement',calc['cleat_acoustic_displacement']),('rear_fixing_displacement',calc['rear_fixing_displacement'])]:
        d.userParameters.itemByName(key).expression=f'{amount*1e9:.12g} mm^3'
    d.computeAll()
    # Scoped rear-corner reliefs only in service floor; cleats remain continuous.
    floor=named('Service_floor');wall=m['wall'];cw=m['rear_cleat_width'];cd=m['rear_cleat_depth'];rear=m['depth']-wall
    for x in (wall,m['width']-wall-cw):
        plane_in=floor.constructionPlanes.createInput();plane_in.setByOffset(floor.xYConstructionPlane,V(f'{(rear-cd)*1000} mm'))
        plane=floor.constructionPlanes.add(plane_in);plane.isLightBulbOn=False;sk=floor.sketches.add(plane);sk.name='E09_Cleat_corner_notch'
        curves=sk.sketchCurves.sketchLines.addTwoPointRectangle(F.point([x,m['service_floor_y'],0]),F.point([x+cw,m['service_floor_y']+wall,0]))
        for line in curves:line.isFixed=True
        inp=floor.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f'{cd*1000} mm')),adsk.fusion.ExtentDirections.PositiveExtentDirection);inp.participantBodies=list(floor.bRepBodies)
        floor.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
    left=p['bay_left'];front=p['bay_front'];top=p['bay_top'];width=p['bay_right']-left
    frontwall=F.box([left,wall,front],[width,top-2*wall,wall])
    leftwall=F.box([left,wall,front+wall],[wall,top-2*wall,rear-front-wall])
    F.subtract(leftwall,F.box([left-.001,wall-.001,rear-cd],[wall+.002,cw+.001,cd+.001]))
    roof=F.box([left,top-wall,front],[width,wall,rear-front])
    # New bay ends before the fixed right rear cleat; no roof corner notch needed.
    F.component('E09_Battery_front_wall',[frontwall],'OWN_PLY12_BATTERY_FRONT')
    F.component('E09_Battery_left_wall',[leftwall],'OWN_PLY12_BATTERY_LEFT')
    roofcp=F.component('E09_Battery_roof',[roof],'OWN_PLY12_BATTERY_ROOF')
    rightwall=F.box([p['bay_right']-wall,wall,front+wall],[wall,top-2*wall,rear-front-wall])
    F.subtract(rightwall,F.box([p['bay_right']-wall-.001,wall-.001,rear-cd],[wall+.002,cw+.001,cd+.001]))
    F.component('E09_Battery_right_wall',[rightwall],'OWN_PLY12_BATTERY_RIGHT')
    origin=p['battery_origin'];size=p['battery_size']
    battery=F.component('E09_Battery_EREMIT_50Ah_BMS',[F.box(origin,size)],'EREMIT_12V50Ah_MICRO_GEN7_BASIS',
        'manufacturer_dimensions_own_envelope_actual_terminal_positions_unverified','https://www.eremit.de/p/12v-50ah-lifepo4-micro-gen-7-basis-beguenstigte-pv-verwendung-0-ust')
    battery.attributes.add('OPEN_LOUD','manufacturer_mass_kg',str(p['battery_mass']))
    padbody=F.box([origin[0],origin[1]-p['pad'],origin[2]],[size[0],p['pad'],size[2]])
    for axis_x in (.175,.245):F.subtract(padbody,F.box([axis_x-.0125,origin[1]-p['pad']-.001,origin[2]-.002],[.025,.0035,size[2]+.004]))
    F.component('E09_Battery_bottom_pad',[padbody],'OWN_BATTERY_PAD_3MM','foam_with_strap_reliefs_compression_unverified')
    for i,z in enumerate(p['support_runner_z']):
        F.component(f'E09_Battery_support_runner_{i}',[F.box([origin[0],wall,z],[size[0],origin[1]-p['pad']-wall,p['support_runner_depth']])],'OWN_WOOD_BATTERY_RUNNER_25_20_130','support_geometry_glue_and_retention_test_pending')
    zone=F.component('E09_REF_Battery_M6_terminal_zone',[F.box([origin[0],origin[1]+size[1],origin[2]],[size[0],p['terminal_zone_height'],size[2]])],
        'REFERENCE_TERMINAL_CLEARANCE','nonphysical_unverified_terminal_locations')
    for body in zone.bRepBodies:body.isLightBulbOn=False
    # Two standard25mm endless straps. Nominal band/buckle envelopes, not rated geometry.
    for index,x in enumerate((.175,.245)):
        w=p['strap_width'];t=.0015;yy=origin[1]-.002;hh=size[1]+.004;zz=origin[2]-.002;dd=size[2]+.004
        bands=[F.box([x-w/2,yy,zz],[w,t,dd]),F.box([x-w/2,yy+hh-t,zz],[w,t,dd]),
            F.box([x-w/2,yy+t,zz],[w,hh-2*t,t]),F.box([x-w/2,yy+t,zz+dd-t],[w,hh-2*t,t])]
        F.component(f'E09_Battery_strap_{index}',bands,'MASTERLOCK_3110EURDAT','25mm_purchased_strap_nominal_routing_buckle_shape_not_verified')
        F.component(f'E09_Battery_buckle_{index}',[F.box([x-.016,.120,origin[2]+size[2]+.003],[.032,.025,.008])],'MASTERLOCK_3110EURDAT_BUCKLE','reserved_envelope_not_manufacturer_dimensions')
    # Converter known mounting pattern. Outer body is a conservative clearance envelope.
    co=p['converter_origin'];cs=p['converter_size'];body=F.box(co,cs);holes=[]
    for sx in (-1,1):
        for sy in (-1,1):
            x=co[0]+cs[0]/2+sx*.0988/2;y=co[1]+cs[1]/2+sy*.0842/2;holes.append((x,y))
            F.subtract(body,F.cylinder([x,y,co[2]-.001],[x,y,co[2]+cs[2]+.001],.0038/2))
    conv=F.component('E09_Orion_12_24_5_converter',[body],'VICTRON_ORI122410110','manufacturer_outer_dimensions_pitch_own_clearance_model_mount_ear_thickness_assumed',
        'https://www.victronenergy.com/upload/documents/Orion-Tr-110W-120W-Isolated.PDF')
    conv.attributes.add('OPEN_LOUD','role','REGULATED20V SUPPLY, NOT A BATTERY CHARGER')
    partition=named('Service_partition');sz=calc['service_z']
    for i,(x,y) in enumerate(holes):
        F.cut_circle(partition,'z',[x,y,sz],.0034,wall,'E09_Orion_M3_clearance')
        F.washerz(f'E09_Orion_{i}_front_washer',x,y,sz-.0005,3)
        F.boltz(f'E09_Orion_{i}_M3x20',x,y,sz-.0005,3,.020)
        F.washerz(f'E09_Orion_{i}_rear_washer',x,y,co[2]+.003,3)
        F.nutz(f'E09_Orion_{i}_nut',x,y,co[2]+.0035,3)
    # External mains charger is an accessory, deliberately outside the carried cabinet.
    ch=F.component('E09_External_EREMIT_14p6V_5A_charger',[F.box([.440,0,.200],[.130,.030,.055])],'EREMIT_12V5A_LFP_CHARGER',
        'external_accessory_dimensions_from_manufacturer_not_mains_internal','https://www.eremit.de/p/12v-5a-lifepo4-ladegeraet-entstoert')
    ch.attributes.add('OPEN_LOUD','not_carried_mass','true')
    # Real supplier fuse-holder references, with explicit envelope uncertainty.
    for tag,origin_,part in [('F1_main15A',[.280,.182,.270],'LITTELFUSE_FHAC0002ZXJ'),('F2_charge7p5A',[.280,.150,.270],'LITTELFUSE_FHAC0001ZXJ')]:
        F.component('E09_'+tag+'_holder',[F.box(origin_,[.034,.022,.018])],part,'reserved_holder_envelope_actual_measure_before_mounting')
    F.component('E09_F3_output5A_holder',[F.box([.235,.350,.230],[.034,.022,.018])],'LITTELFUSE_FHAC0001ZXJ','reserved_holder_envelope_actual_measure_before_mounting')
    # XT60 charge socket is behind the sealed removable rear cover: no exposed IP40 port.
    xt=F.box([.29345,.189175,.3058],[.0191,.01165,.0202])
    flange=F.box([.286,.1871,.3219],[.034,.0158,.0041])
    for x in (.2905,.3155):F.subtract(flange,F.cylinder([x,.195,.320],[x,.195,.328],.0031/2))
    F.component('E09_XT60E_F_charge_socket',[xt,flange],'AMASS_XT60E_F','own_drawing_envelope_IP40_INTERNAL_ONLY',
        'AMASS XT60E-F manufacturer drawing,25mm hole pitch,19.3x11.85panel cutout')
    # Recreate speaker glands at the new, clear routing stations.
    def gland(tag,cp,axis,at,thread,bodylength,outer,thread_d,bore_d,relief_d,relief_depth,part):
        idx='xyz'.index(axis);F.cut_circle(cp,axis,at,bore_d,wall,'E09_'+tag+'_through')
        F.cut_circle(cp,axis,at,relief_d,relief_depth,'E09_'+tag+'_relief')
        shoulder=list(at);shoulder[idx]+=wall;a=list(shoulder);a[idx]-=thread;end=list(shoulder);end[idx]+=bodylength
        threadbody=F.cylinder(a,shoulder,thread_d/2);shell=F.cylinder(shoulder,end,outer/2)
        begin=list(a);begin[idx]-=.001;finish=list(end);finish[idx]+=.001;inside=.0038 if thread_d==.016 else .0026
        F.subtract(threadbody,F.cylinder(begin,finish,inside));F.subtract(shell,F.cylinder(begin,finish,inside))
        F.component('E09_'+tag+'_gland',[threadbody,shell],part,'manufacturer_thread_and_clamp_reference_own_outer_envelope')
        a=list(at);a[idx]+=relief_depth-.003;b=list(a);b[idx]+=.003
        nut=F.subtract(F.cylinder(a,b,outer/2),F.cylinder(begin,finish,thread_d/2))
        F.component('E09_'+tag+'_locknut',[nut],'SKINDICHT_SM_M_'+str(round(thread_d*1000)),'3mm_metal_nut_reference_SKU_qualification_pending')
    gland('LF_feed',floor,'y',[p['lf_floor_feed_xz'][0],m['service_floor_y'],p['lf_floor_feed_xz'][1]],.012,.028,.022,.016,.0165,.028,.005,'LAPP_53017210')
    gland('HF_feed',partition,'z',[.170,.500,sz],.012,.028,.022,.016,.0165,.028,.005,'LAPP_53017210')
    for slot,(axis_x,axis_z) in enumerate(p['power_feed_xz']):
        for tag,cp,y in [('BAT',roofcp,top-wall),('ELEC',floor,m['service_floor_y'])]:
            gland(tag+'_'+str(slot),cp,'y',[axis_x,y,axis_z],.015,.0217,.0166,.012,.0125,.022,.002,'LAPP_53010000')
    root.attributes.add('OPEN_LOUD','power_hardware','E09');d.computeAll()
    report=dict(document=doc.name,created=F.created,layout=calc,source='data/experiments/E09_parameters.json',
        limitations=['Envelope models, not supplier CAD; battery terminal positions and holder envelopes still to verify.',
            'Strap anchors, clip and connector bracket completion follows; no battery retention release yet.',
            'External charger used only dry with speaker switched off; no mains inside cabinet.'])
    (OUT/'power_build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'power_parts':len(F.created),'service_z_mm':sz*1000,'battery_nominal_Wh':640,'case_net_l':calc['target_net']*1000}))
