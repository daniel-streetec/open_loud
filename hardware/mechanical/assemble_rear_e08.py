"""Synchronize revised layout and add accessible rear-cover fixing candidates."""
import adsk.core, adsk.fusion
import json, math, sys
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import importlib, layout as layout_module
importlib.reload(layout_module)
calculate=layout_module.calculate

def run(_context: str):
    app=adsk.core.Application.get()
    doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_E08'), 'Activate the intended E08 document first'
    design=adsk.fusion.Design.cast(app.activeProduct);root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E08'
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));layout=calculate(data)
    V=adsk.core.ValueInput.createByString;P=adsk.core.Point3D.create
    NEW=adsk.fusion.FeatureOperations.NewBodyFeatureOperation;CUT=adsk.fusion.FeatureOperations.CutFeatureOperation
    for key,r in data['mechanical'].items():
        if r['unit']=='m':
            parameter=design.userParameters.itemByName(key)
            expr=f"{r['value']*1000:.12g} mm"
            if parameter:parameter.expression=expr
            else:design.userParameters.add(key,V(expr),'mm',r['source'])
    for key in ('port_d','port_length','service_z'):
        design.userParameters.itemByName(key).expression=f'{layout[key]*1000:.12g} mm'
    for key in ('reinforcement_displacement','cleat_acoustic_displacement','backing_displacement','rear_fixing_displacement'):
        p=design.userParameters.itemByName(key);expr=f'{layout[key]*1e9:.12g} mm^3'
        if p:p.expression=expr
        else:design.userParameters.add(key,V(expr),'mm^3','Python-derived volume budget')
    ring=next(o.component for o in root.occurrences if o.component.name=='LF_steel_backing_ring_candidate')
    ring_sketch=next(sk for sk in ring.sketches if sk.name=='Steel_backing_annulus')
    for dimension in ring_sketch.sketchDimensions:
        if 'lf_cutout' in dimension.parameter.expression:dimension.parameter.expression='lf_backing_inner_d'
    if not layout['relief_required']:
        old=next((f for f in ring.features.extrudeFeatures if hasattr(f.profile,'parentSketch') and f.profile.parentSketch.name=='Port_relief'),None)
        if old:old.deleteMe()
    baffle=next(o.component for o in root.occurrences if o.component.name=='Baffle')
    old=next((s for s in baffle.sketches if s.name.startswith('LF_8x45deg_mounting_centres')),None)
    if old:old.deleteMe() # Former fixed annotation; actual parameter-driven bores supersede it.
    design.computeAll()
    def ev(s):
        p=design.userParameters.itemByName(s)
        return p.value if p else design.unitsManager.evaluateExpression(s,'cm')
    def plane(comp,z):
        pin=comp.constructionPlanes.createInput();pin.setByOffset(comp.xYConstructionPlane,V(z))
        p=comp.constructionPlanes.add(pin);p.isLightBulbOn=False;return p
    def circle(comp,name,x,y,d,z):
        sk=comp.sketches.add(plane(comp,z));sk.name=name
        c=sk.sketchCurves.sketchCircles.addByCenterRadius(P(ev(x),ev(y),0),ev(d)/2)
        sk.sketchDimensions.addDistanceDimension(sk.originPoint,c.centerSketchPoint,adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,P(ev(x),ev(y)+1,0)).parameter.expression=x
        sk.sketchDimensions.addDistanceDimension(sk.originPoint,c.centerSketchPoint,adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,P(ev(x)+1,ev(y),0)).parameter.expression=y
        sk.sketchDimensions.addDiameterDimension(c,P(ev(x)+1,ev(y)+1,0)).parameter.expression=d
        return sk
    def rectangle(comp,name,x,y,w,h,z):
        sk=comp.sketches.add(plane(comp,z));sk.name=name
        lines=sk.sketchCurves.sketchLines.addTwoPointRectangle(P(ev(x),ev(y),0),P(ev(x)+ev(w),ev(y)+ev(h),0))
        for i in (0,2):sk.geometricConstraints.addHorizontal(lines.item(i))
        for i in (1,3):sk.geometricConstraints.addVertical(lines.item(i))
        q=lines.item(0).startSketchPoint
        sk.sketchDimensions.addDistanceDimension(sk.originPoint,q,adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,P(ev(x),ev(y)+1,0)).parameter.expression=x
        sk.sketchDimensions.addDistanceDimension(sk.originPoint,q,adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,P(ev(x)+1,ev(y),0)).parameter.expression=y
        sk.sketchDimensions.addDistanceDimension(q,lines.item(0).endSketchPoint,adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,P(ev(x),ev(y)-1,0)).parameter.expression=w
        sk.sketchDimensions.addDistanceDimension(lines.item(1).startSketchPoint,lines.item(1).endSketchPoint,adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,P(ev(x)-1,ev(y),0)).parameter.expression=h
        return sk
    def extrude(comp,sk,depth,name,operation=NEW):
        if operation==CUT:
            inp=comp.features.extrudeFeatures.createInput(sk.profiles.item(0),operation)
            inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(depth)),adsk.fusion.ExtentDirections.PositiveExtentDirection)
            inp.participantBodies=list(comp.bRepBodies)
            ft=comp.features.extrudeFeatures.add(inp)
        else:ft=comp.features.extrudeFeatures.addSimple(sk.profiles.item(0),V(depth),operation)
        ft.name=name;sk.isLightBulbOn=False
        if operation==NEW:ft.bodies.item(0).name=name
        return ft
    def component(name):
        cp=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;cp.name=name
        cp.attributes.add('OPEN_LOUD','status','fabricated_thread_plate_candidate_not_load_validated');return cp
    rear=next(o.component for o in root.occurrences if o.component.name=='Rear_removable')
    if not any(o.component.name.startswith('Rear_thread_plate_') for o in root.occurrences):
        points=[]
        for side,x in [('left','wall+rear_cleat_width/2'),('right','width-wall-rear_cleat_width/2')]:
            for fraction in (.15,.5,.85):points.append((f'{side}_{fraction}',x,f'height*{fraction}',f'Rear_cleat_{side}',False))
        for side,y in [('bottom','wall+rear_cleat_width/2'),('top','height-wall-rear_cleat_width/2')]:
            for fraction in (.27,.73):points.append((f'{side}_{fraction}',f'width*{fraction}',y,f'Rear_cleat_{side}',True))
        for name,x,y,cleat_name,horizontal in points:
            cleat=next(o.component for o in root.occurrences if o.component.name==cleat_name)
            for cp,z,depth in [(rear,'depth-wall','wall'),(cleat,'depth-wall-rear_cleat_depth','rear_cleat_depth')]:
                sk=circle(cp,'Rear_M5_clearance_'+name,x,y,'rear_bolt_clearance',z);extrude(cp,sk,depth,'Rear_M5_through_'+name,CUT)
            plate=component('Rear_thread_plate_'+name)
            w,h=('rear_plate_length','rear_plate_width') if horizontal else ('rear_plate_width','rear_plate_length')
            z='depth-wall-rear_cleat_depth-rear_plate_thickness'
            sk=rectangle(plate,'Plate_outline',f'({x})-({w})/2',f'({y})-({h})/2',w,h,z);extrude(plate,sk,'rear_plate_thickness','Steel_plate_M5_tap_after_drilling')
            sk=circle(plate,'M5x0p8_pilot_VERIFY',x,y,'rear_tap_pilot',z);extrude(plate,sk,'rear_plate_thickness','M5_pilot_not_thread_geometry',CUT)
            for sign in (-1,1):
                xx=f'({x})+({sign})*rear_retainer_pitch/2' if horizontal else x
                yy=y if horizontal else f'({y})+({sign})*rear_retainer_pitch/2'
                sk=circle(plate,'Retainer_screw_clearance',xx,yy,'rear_retainer_bore',z);extrude(plate,sk,'rear_plate_thickness','Retainer_bore',CUT)
        # Recess for a continuous gasket; compression/material still require testing.
        sk=rear.sketches.add(plane(rear,'depth-wall'));sk.name='Rear_gasket_recess'
        for inset in ('gasket_edge_offset','gasket_edge_offset+gasket_groove_width'):
            x=ev('wall')+ev(inset);y=ev('wall')+ev(inset)
            lines=sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x,y,0),P(ev('width-wall')-ev(inset),ev('height-wall')-ev(inset),0))
            for line in lines:line.isFixed=True
        ring_profile=next(sk.profiles.item(i) for i in range(sk.profiles.count) if sk.profiles.item(i).profileLoops.count==2)
        ft=rear.features.extrudeFeatures.addSimple(ring_profile,V('gasket_groove_depth'),CUT);ft.name='Gasket_recess_untested';sk.isLightBulbOn=False
    design.computeAll()
    output=ROOT/'hardware/mechanical/exports/E08'
    report=json.loads((output/'fusion_validation.json').read_text(encoding='utf-8'))
    report.update(layout_source='data/parameters.json',gross_internal_l=layout['gross_internal']*1000,net_l=layout['target_net']*1000,
                  service_z_mm=layout['service_z']*1000,service_excluded_l=layout['service_excluded']*1000,
                  rear_fixing_acoustic_l=layout['rear_fixing_displacement']*1000,
                  envelope_mm=[data['mechanical'][k]['value']*1000 for k in ('width','height','depth')],
                  construction='12mm birch plywood shell, 24mm laminated baffle, 3mm steel LF backing, 20mm rear cleats, ten 5mm tapped steel plates')
    (output/'fusion_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'layout_mm':report['envelope_mm'],'rear_fixings':10,'service_z_mm':layout['service_z']*1000,'net_l_estimate':layout['target_net']*1000}))
