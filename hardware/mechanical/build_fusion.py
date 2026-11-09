"""OPEN//LOUD A0 E02: parametric concept CAD. Run through tools/fusion_bridge.py.
Axes x=width, y=height, z=rearwards, millimetres user units; API internal cm.
No fabricated purchased-part mounting detail. References are clearance models.
"""
import adsk.core, adsk.fusion
import json, math
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
OUT=ROOT/'hardware/mechanical/exports'
V=adsk.core.ValueInput.createByString
P=adsk.core.Point3D.create
NEW=adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT=adsk.fusion.FeatureOperations.CutFeatureOperation
H=adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
Y=adsk.fusion.DimensionOrientations.VerticalDimensionOrientation


def run(_context: str):
    app=adsk.core.Application.get()
    projects=app.data.dataProjects
    matches=[projects.item(i) for i in range(projects.count) if projects.item(i).name=='OPEN_LOUD']
    project=matches[0] if matches else projects.add('OPEN_LOUD','Portable DIY loudspeaker development','')
    assert project, 'Project creation failed'
    target='OPEN_LOUD_A0_E02_Concept'
    existing=[app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name.startswith(target)]
    folder=project.rootFolder
    for i in range(folder.dataFiles.count):
        assert folder.dataFiles.item(i).name!=target, 'Target exists; do not overwrite'
    doc=existing[0] if existing else app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.activate()
    doc.name=target
    design=adsk.fusion.Design.cast(app.activeProduct)
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    assert design.rootComponent.occurrences.count==0 and design.userParameters.count==0, 'Existing design contains work; refuse rebuild' 
    root=design.rootComponent
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    mech=data['mechanical']
    def add(name,expression,unit='mm',comment='E02 concept'):
        assert design.unitsManager.isValidExpression(expression,unit), f"Invalid parameter {name}: {expression} [{unit}]; existing={[(q.name,q.expression) for q in design.userParameters]}"
        design.userParameters.add(name,V(expression),unit,comment)
    for key,rec in mech.items():
        if rec['unit']=='m':
            add(key,f"{rec['value']*1000:.12g} mm",comment=rec['source']+'; '+rec['status'])
    add('target_net',f"{data['concepts']['A0']['Vb']['value']*1e9:.12g} mm^3",'mm^3','report:p7')
    add('port_area',f"{data['concepts']['A0']['port_area']['value']*1e6:.12g} mm^2",'mm^2','report:p7')
    rho=data['environment']['rho']['value'];c=data['environment']['c']['value']
    vb=data['concepts']['A0']['Vb']['value'];fb=data['concepts']['A0']['Fb']['value'];area=data['concepts']['A0']['port_area']['value']
    leff=c*c*area/((2*math.pi*fb)**2*vb)
    length=leff-data['model']['end_correction']['value']*2*math.sqrt(area/math.pi)
    add('port_length',f'{length*1000:.12g} mm',comment='derived Helmholtz and equivalent-round end correction; prototype tune')
    add('lf_displacement',f"{data['drivers']['10FE200-4']['displacement']['value']*1e9:.12g} mm^3",'mm^3','manufacturer occupied air volume, not solid clearance-envelope volume')
    add('horn_displacement',f"{mech['horn_displacement']['value']*1e9:.12g} mm^3",'mm^3','manufacturer horn volume')
    # Fusion E02 diagnostic shows incorrect scaling when referencing squared/cubic
    # user parameters inside new expressions. Calculate these dependent lengths in
    # Python from versioned SI inputs; geometry remains driven by length parameters.
    m={k:r['value'] for k,r in mech.items() if isinstance(r,dict) and 'value' in r}
    wi=m['width']-2*m['wall'];hi=m['height']-2*m['wall'];di=m['depth']-2*m['wall']
    port_d=2*math.sqrt(area/math.pi)
    port_displacement=math.pi/4*(port_d+2*m['port_wall'])**2*(length-m['wall'])
    hf_displacement=math.pi/4*m['hf_diameter']**2*m['hf_depth']
    brace_displacement=wi*m['brace_height']*m['wall']
    exclusion=wi*hi*di-vb-port_displacement-data['drivers']['10FE200-4']['displacement']['value']-m['horn_displacement']-hf_displacement-brace_displacement
    service_z=m['depth']-m['wall']-exclusion/(wi*(m['height']-m['wall']-m['service_floor_y']))
    add('port_d',f'{port_d*1000:.12g} mm',comment='derived in Python; Fusion area-reference scaling workaround')
    add('service_z',f'{service_z*1000:.12g} mm',comment='derived net-volume budget in Python; regenerate after dimensional changes')
    for name,expr,unit in [
        ('inner_width','width-2*wall','mm'),('inner_height','height-2*wall','mm'),('inner_depth','depth-2*wall','mm'),
        ('port_outer_d','port_d+2*port_wall','mm'),
        ('gross_internal','inner_width*inner_height*inner_depth','mm^3'),
        ('port_displacement','PI/4*port_outer_d^2*(port_length-wall)','mm^3'),
        ('hf_displacement','PI/4*hf_diameter^2*hf_depth','mm^3'),
        ('brace_displacement','inner_width*brace_height*wall','mm^3'),
        ('service_reserve','inner_width*(height-wall-service_floor_y)*(depth-wall-service_z)','mm^3')]:add(name,expr,unit)
    def ev(expr,unit='cm'):
        parameter=design.userParameters.itemByName(expr)
        return parameter.value if parameter else design.unitsManager.evaluateExpression(expr,unit)
    def plane(comp,z):
        inp=comp.constructionPlanes.createInput();inp.setByOffset(comp.xYConstructionPlane,V(z))
        result=comp.constructionPlanes.add(inp);result.isLightBulbOn=False;return result
    def comp(name,reference=False):
        occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name=name
        occ.component.attributes.add('OPEN_LOUD','status','clearance_reference_not_manufacturing' if reference else 'prototype_candidate')
        if reference:occ.opacity=.35
        return occ.component
    def anchor(sk,pt,x,y):
        # Origin-to-corner dimensions preserve positions under user-parameter changes.
        if abs(ev(x))<1e-9 and abs(ev(y))<1e-9:
            sk.geometricConstraints.addCoincident(pt,sk.originPoint)
        else:
            if abs(ev(x))<1e-9:sk.geometricConstraints.addVerticalPoints(sk.originPoint,pt)
            else:sk.sketchDimensions.addDistanceDimension(sk.originPoint,pt,H,P(ev(x),ev(y)+1,0)).parameter.expression=x
            if abs(ev(y))<1e-9:sk.geometricConstraints.addHorizontalPoints(sk.originPoint,pt)
            else:sk.sketchDimensions.addDistanceDimension(sk.originPoint,pt,Y,P(ev(x)+1,ev(y),0)).parameter.expression=y
    def rectangle(comp,name,x,y,w,h,z):
        sk=comp.sketches.add(plane(comp,z));sk.name=name
        lines=sk.sketchCurves.sketchLines.addTwoPointRectangle(P(ev(x),ev(y),0),P(ev(f'({x})+({w})'),ev(f'({y})+({h})'),0))
        for i in (0,2):sk.geometricConstraints.addHorizontal(lines.item(i))
        for i in (1,3):sk.geometricConstraints.addVertical(lines.item(i))
        anchor(sk,lines.item(0).startSketchPoint,x,y)
        sk.sketchDimensions.addDistanceDimension(lines.item(0).startSketchPoint,lines.item(0).endSketchPoint,H,P(ev(x),ev(y)-1,0)).parameter.expression=w
        sk.sketchDimensions.addDistanceDimension(lines.item(1).startSketchPoint,lines.item(1).endSketchPoint,Y,P(ev(x)-1,ev(y),0)).parameter.expression=h
        return sk
    def circle(comp,name,x,y,d,z,inner=None):
        sk=comp.sketches.add(plane(comp,z));sk.name=name
        curve=sk.sketchCurves.sketchCircles.addByCenterRadius(P(ev(x),ev(y),0),ev(d)/2)
        anchor(sk,curve.centerSketchPoint,x,y)
        sk.sketchDimensions.addDiameterDimension(curve,P(ev(x)+ev(d),ev(y),0)).parameter.expression=d
        if inner:
            second=sk.sketchCurves.sketchCircles.addByCenterRadius(P(ev(x),ev(y),0),ev(inner)/2)
            sk.geometricConstraints.addConcentric(curve,second)
            sk.sketchDimensions.addDiameterDimension(second,P(ev(x),ev(y)+ev(d),0)).parameter.expression=inner
        return sk
    def profile(sk,ring=False):
        if ring:return next(sk.profiles.item(i) for i in range(sk.profiles.count) if sk.profiles.item(i).profileLoops.count==2)
        assert sk.profiles.count==1, f'{sk.name}: unexpected profiles'
        return sk.profiles.item(0)
    def extrude(comp,sk,depth,name,operation=NEW,ring=False):
        feat=comp.features.extrudeFeatures.addSimple(profile(sk,ring),V(depth),operation)
        feat.name=name;sk.isLightBulbOn=False
        if operation==NEW:feat.bodies.item(0).name=name
        return feat
    def box(name,x,y,w,h,z,d):
        cp=comp(name);sk=rectangle(cp,name+'_profile',x,y,w,h,z);extrude(cp,sk,d,name);return cp,sk
    panels=[]
    for name,x,y,w,h,z,d in [
        ('Side_left','0 mm','0 mm','wall','height','0 mm','depth'),
        ('Side_right','width-wall','0 mm','wall','height','0 mm','depth'),
        ('Bottom','wall','0 mm','inner_width','wall','0 mm','depth'),
        ('Top','wall','height-wall','inner_width','wall','0 mm','depth'),
        ('Baffle','wall','wall','inner_width','inner_height','0 mm','wall'),
        ('Rear_removable','wall','wall','inner_width','inner_height','depth-wall','wall')]:
        cp,sk=box(name,x,y,w,h,z,d);panels.append((cp,sk))
    baffle=panels[4][0]
    for name,y,d in [('LF','lf_y','lf_cutout+2*baffle_clearance'),('Port','port_y','port_outer_d+2*baffle_clearance')]:
        sk=circle(baffle,name+'_cutout','width/2',y,d,'0 mm');extrude(baffle,sk,'wall',name+'_cut',CUT)
    sk=rectangle(baffle,'Horn_cutout','(width-horn_cutout)/2','horn_y-horn_cutout/2','horn_cutout','horn_cutout','0 mm')
    extrude(baffle,sk,'wall','Horn_cut',CUT)
    # Mounting centres as construction geometry only; original slot pattern must be checked.
    sk=baffle.sketches.add(baffle.xYConstructionPlane);sk.name='LF_8x45deg_mounting_centres_VERIFY_slots'
    for i in range(8):
        angle=i*math.pi/4
        pt=sk.sketchPoints.add(P(ev('width/2')+ev('lf_pcd')/2*math.cos(angle),ev('lf_y')+ev('lf_pcd')/2*math.sin(angle),0))
        pt.isFixed=True
    sk.isLightBulbOn=False
    for name,x,y,w,h,z,d in [
        ('Service_partition','wall','service_floor_y+wall','inner_width','height-wall-service_floor_y-wall','service_z','wall'),
        ('Service_floor','wall','service_floor_y','inner_width','wall','service_z','depth-wall-service_z'),
        ('Brace_lower','wall','brace_y','inner_width','brace_height','brace_z','wall')]:
        box(name,x,y,w,h,z,d)
    tube=comp('Port_round_candidate')
    sk=circle(tube,'Port_tube_profile','width/2','port_y','port_outer_d','0 mm','port_d')
    extrude(tube,sk,'port_length','Port_tube',ring=True)
    lf=comp('REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE',True)
    sk=circle(lf,'LF_flange','width/2','lf_y','lf_outer','-lf_flange','lf_cutout')
    extrude(lf,sk,'lf_flange','LF_flange_envelope',ring=True)
    first=circle(lf,'LF_basket_front','width/2','lf_y','lf_basket_d','0 mm')
    second=circle(lf,'LF_basket_rear','width/2','lf_y','lf_magnet_d','lf_depth-lf_flange-lf_magnet_depth')
    loft=lf.features.loftFeatures.createInput(NEW);loft.loftSections.add(profile(first));loft.loftSections.add(profile(second))
    ft=lf.features.loftFeatures.add(loft);ft.name='Basket_clearance_frustum_NOT_SOLID_MATERIAL'
    first.isLightBulbOn=False;second.isLightBulbOn=False
    sk=circle(lf,'LF_magnet','width/2','lf_y','lf_magnet_d','lf_depth-lf_flange-lf_magnet_depth')
    extrude(lf,sk,'lf_magnet_depth','Magnet_envelope')
    horn=comp('REF_BC_ME10V3_DATASHEET_ENVELOPE',True)
    sk=rectangle(horn,'Horn_flange','(width-horn_width)/2','horn_y-horn_width/2','horn_width','horn_width','-horn_flange')
    # Cutout ring rather than a solid flange obscuring the mouth.
    extrude(horn,sk,'horn_flange','Horn_flange_envelope')
    inner=rectangle(horn,'Horn_flange_open','(width-horn_cutout)/2','horn_y-horn_cutout/2','horn_cutout','horn_cutout','-horn_flange')
    extrude(horn,inner,'horn_flange','Horn_mouth_open',CUT)
    first=rectangle(horn,'Horn_mouth_envelope','(width-horn_cutout)/2','horn_y-horn_cutout/2','horn_cutout','horn_cutout','0 mm')
    second=circle(horn,'Horn_throat_envelope','width/2','horn_y','horn_throat','horn_depth-horn_flange')
    loft=horn.features.loftFeatures.createInput(NEW);loft.loftSections.add(profile(first));loft.loftSections.add(profile(second))
    ft=horn.features.loftFeatures.add(loft);ft.name='Flare_clearance_ONLY_not_acoustic_surface'
    first.isLightBulbOn=False;second.isLightBulbOn=False
    hf=comp('REF_BC_DE10_DATASHEET_ENVELOPE',True)
    sk=circle(hf,'DE10_envelope','width/2','horn_y','hf_diameter','horn_depth-horn_flange')
    extrude(hf,sk,'hf_depth','DE10_cylinder_envelope')
    reserve=comp('RESERVE_amp_wiring_UNVERIFIED_no_mounting_holes',True)
    sk=rectangle(reserve,'Amp_installation_reserve','(width-amp_reserve_width)/2','service_floor_y+wall+10 mm','amp_reserve_width','amp_reserve_height','service_z+wall+10 mm')
    extrude(reserve,sk,'amp_reserve_depth','Amp_space_reserve')
    root.attributes.add('OPEN_LOUD','revision','E02')
    root.attributes.add('OPEN_LOUD','net_volume_basis','Manufacturer LF/horn displacement; HF bounding cylinder; service compartment as gross excluded envelope; port outside cross-section internal intrusion; brace solid. Not measured.')
    app.activeViewport.fit()
    OUT.mkdir(parents=True,exist_ok=True)
    report={'fusion_version':app.version,'project_name':project.name,'project_id':project.id,'document_name':doc.name,'net_l':ev('target_net')/1000,'gross_internal_l':ev('gross_internal')/1000,'service_z_mm':ev('service_z')*10,'service_excluded_l':ev('service_reserve')/1000,'port_length_mm':ev('port_length')*10,'port_d_mm':ev('port_d')*10,'status':'concept_not_manufacturing_release'}
    assert ev('service_z')>ev('horn_depth-horn_flange+hf_depth')+1, 'HF to partition clearance below 10mm'
    assert ev('port_length')<ev('depth-wall')-ev('port_d'), 'Port rear clearance less than one diameter'
    balance=ev('gross_internal')-sum(ev(k) for k in ['service_reserve','port_displacement','lf_displacement','horn_displacement','hf_displacement','brace_displacement','target_net'])
    assert abs(balance)<1e-5, f'Volume balance residual cm3={balance}; parameters={[(q.name,q.value) for q in design.userParameters]}'
    issues=[]
    for i in range(design.timeline.count):
        item=design.timeline.item(i)
        if item.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            issues.append({'name':item.name,'message':item.errorOrWarningMessage})
    report['timeline_issues']=issues
    report['solid_bodies']=[{'component':occ.component.name,'body':body.name,'solid':body.isSolid,'volume_cm3':body.volume} for occ in root.occurrences for body in occ.component.bRepBodies]
    assert not issues, 'Timeline contains warnings/errors'
    assert all(b['solid'] and b['volume_cm3']>0 for b in report['solid_bodies'])
    manager=design.exportManager
    assert manager.execute(manager.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E02.step'),root))
    assert manager.execute(manager.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E02.f3d')))
    # Export current baffle planar face including actual cuts, not original uncut sketch.
    face=next(face for body in baffle.bRepBodies for face in body.faces if face.geometry.surfaceType==adsk.core.SurfaceTypes.PlaneSurfaceType and abs(face.centroid.z)<1e-6 and face.area>500)
    drawing=baffle.sketches.add(face);drawing.name='Baffle_export_face_DRAFT'
    assert drawing.saveAsDXF(str(OUT/'Baffle_E02_DRAFT.dxf'))
    drawing.isLightBulbOn=False
    assert app.activeViewport.saveAsImageFile(str(OUT/'OPEN_LOUD_A0_E02.png'),1400,1000)
    report['cloud_save_requested']=False # Save after modelling transaction has completed.
    report['saved']=doc.isSaved
    (OUT/'fusion_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
