"""Own internal XT60 mounting angle, through bolts and real metric counterparts.
Flat-stock/bend fabrication still needs bend allowance and material qualification.
"""
import adsk.core,adsk.fusion,json,sys,math,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    for o in list(root.allOccurrences):
        if o.component.name.startswith(('E08_Charge_socket_bracket','E08_XT60E_F_charge_socket','E08_Charge_socket_','E08_Charge_roof_')):
            native=o.nativeObject or o
            assert native.deleteMe(),f'Cannot remove owned component {o.component.name}'
    p={k:r['value'] for k,r in json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))['connection_mounts_e08'].items()}
    target=next((o.component for o in root.allOccurrences if o.component.name=='BG64_Ladeanschluss'),root)
    F=cad_parts.Parts(target)
    roof=next(o.component for o in root.allOccurrences if o.component.name=='E08_Battery_roof')
    owned=[]
    for ft in roof.features.extrudeFeatures:
        if hasattr(ft.profile,'parentSketch') and ft.profile.parentSketch.name.startswith('E08_charge_bracket_M3_'):owned.append((ft,ft.profile.parentSketch))
    for ft,sk in sorted(owned,key=lambda pair:pair[0].timelineObject.index,reverse=True):ft.deleteMe();sk.deleteMe()
    d.timeline.moveToEnd()
    plate=F.box(p['bracket_vertical_origin'],p['bracket_vertical_size'])
    foot=F.box(p['bracket_foot_origin'],p['bracket_foot_size'])
    assert F.tm.booleanOperation(plate,foot,adsk.fusion.BooleanTypes.UnionBooleanType)
    # Rounded rectangle cut from two strips and four corner cylinders.
    width,height,_=p['socket_cutout'];r=p['own_bracket_cut_radius'];cx=p['socket_flange_origin'][0]+p['socket_flange_size'][0]/2;cy=p['socket_center_y'];z=p['bracket_vertical_origin'][2]
    for origin,size in [([cx-width/2+r,cy-height/2,z-.001],[width-2*r,height,.004]),([cx-width/2,cy-height/2+r,z-.001],[width,height-2*r,.004])]:F.subtract(plate,F.box(origin,size))
    for sx in (-1,1):
        for sy in (-1,1):
            x=cx+sx*(width/2-r);y=cy+sy*(height/2-r)
            F.subtract(plate,F.cylinder([x,y,z-.001],[x,y,z+.003],r))
    flange=F.box(p['socket_flange_origin'],p['socket_flange_size'])
    for x in p['socket_hole_x']:
        F.subtract(plate,F.cylinder([x,cy,z-.001],[x,cy,z+.003],.0017))
        F.subtract(flange,F.cylinder([x,cy,z-.001],[x,cy,z+.008],.00155))
    for x in p['roof_hole_x']:
        foot_y=p['bracket_foot_origin'][1];foot_t=p['bracket_foot_size'][1]
        F.subtract(plate,F.cylinder([x,foot_y-.001,p['roof_hole_z']],[x,foot_y+foot_t+.001,p['roof_hole_z']],p['roof_bore']/2))
    F.component('E08_Charge_socket_bracket',[plate],'OWN_AL2_XT60_INTERNAL_BRACKET','own_nominal_angle_bend_radius_and_material_pending')
    F.component('E08_XT60E_F_charge_socket',[F.box(p['socket_body_origin'],p['socket_body_size']),flange],'AMASS_XT60E_F','manufacturer_envelope_internal_IP40_only')
    for i,x in enumerate(p['socket_hole_x']):
        F.boltz(f'E08_Charge_socket_{i}_M3x10',x,cy,z,3,p['socket_bolt_length'])
        back=p['socket_flange_origin'][2]+p['socket_flange_size'][2]
        F.washerz(f'E08_Charge_socket_{i}_back_washer',x,cy,back,3)
        F.nutz(f'E08_Charge_socket_{i}_nut',x,cy,back+.0005,3)
    # Y-axis hardware made directly in body coordinates, no unsaved occurrence moves.
    def hex_y(x,y,z,h):
        body=F.hexz(0,0,0,h,.0055);matrix=adsk.core.Matrix3D.create()
        matrix.setToRotation(-math.pi/2,adsk.core.Vector3D.create(1,0,0),F.point([0,0,0]));matrix.translation=adsk.core.Vector3D.create(x*100,y*100,z*100)
        assert F.tm.transform(body,matrix);return body
    roof=next(o.component for o in root.allOccurrences if o.component.name=='E08_Battery_roof')
    for i,x in enumerate(p['roof_hole_x']):
        zz=p['roof_hole_z'];cutname=f'E08_charge_bracket_M3_{i}'
        if not any(sk.name==cutname for sk in roof.sketches):F.cut_circle(roof,'y',[x,.208,zz],p['roof_bore'],.012,cutname)
        for tag,y in [('bottom',.2055),('top',.220)]:
            b=F.subtract(F.cylinder([x,y,zz],[x,y+.0005,zz],.0035),F.cylinder([x,y-.001,zz],[x,y+.0015,zz],.0016))
            F.component(f'E08_Charge_roof_{i}_{tag}_washer',[b],'ISO7089_M3')
        head=F.cylinder([x,.2025,zz],[x,.2055,zz],.00275)
        shaft=F.cylinder([x,.2055,zz],[x,.2055+p['roof_bolt_length'],zz],.0015)
        assert F.tm.booleanOperation(head,shaft,adsk.fusion.BooleanTypes.UnionBooleanType)
        F.component(f'E08_Charge_roof_{i}_M3x20',[head],'ISO4762_M3x20','nominal_thread_and_head_envelope_recess_not_modeled')
        nut=F.subtract(hex_y(x,.2205,zz,.0024),F.cylinder([x,.2195,zz],[x,.2239,zz],.0015))
        F.component(f'E08_Charge_roof_{i}_nut',[nut],'ISO4032_M3')
    d.computeAll()
    report=dict(created=F.created,socket_thread_protrusion_m=.001,roof_thread_protrusion_m=.0026,
        limitations=['Assemble bracket before battery insertion; battery terminal locations unknown.',
        'No bolt locking or seal qualification; bend radius not modeled.','Charge mating plug access and cable solder-joint insulation still to verify.'])
    out=ROOT/'hardware/mechanical/exports/E08/charge_bracket_build.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'parts_added':len(F.created),'status':'kernel_check_pending'}))
