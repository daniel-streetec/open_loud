"""Constrain rectangles, inspect collisions, test parameter response and export."""
import adsk.core, adsk.fusion
import json, math
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
OUT=ROOT/'hardware/mechanical/exports/E03'

def run(_context: str):
    app=adsk.core.Application.get()
    design=adsk.fusion.Design.cast(app.activeProduct)
    root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E03'
    design.userParameters.itemByName('horn_flange').expression='5.5 mm'
    design.computeAll()
    # Side cleats overlap the service floor's rear corners: notch the floor to fit.
    floor=next(o.component for o in root.occurrences if o.component.name=='Service_floor')
    if not any(sk.name.startswith('Cleat_corner_notch') for sk in floor.sketches):
        u=design.unitsManager
        def ev(x):return u.evaluateExpression(x,'cm')
        for x in ('wall','width-wall-rear_cleat_width'):
            pin=floor.constructionPlanes.createInput();pin.setByOffset(floor.xYConstructionPlane,adsk.core.ValueInput.createByString('depth-wall-rear_cleat_depth'))
            plane=floor.constructionPlanes.add(pin);plane.isLightBulbOn=False
            sk=floor.sketches.add(plane);sk.name='Cleat_corner_notch'
            lines=sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(ev(x),ev('service_floor_y'),0),adsk.core.Point3D.create(ev(x)+ev('rear_cleat_width'),ev('service_floor_y+wall'),0))
            for line in lines:line.isFixed=True
            inp=floor.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
            inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('rear_cleat_depth')),adsk.fusion.ExtentDirections.PositiveExtentDirection)
            inp.participantBodies=list(floor.bRepBodies)
            feat=floor.features.extrudeFeatures.add(inp);feat.name='Cleat_notch';sk.isLightBulbOn=False
    report=json.loads((OUT/'fusion_validation.json').read_text(encoding='utf-8'))
    # Recreate export-only sketches after the final bores/cuts; old edge projections
    # do not necessarily acquire new holes when a source face changes.
    for o in root.occurrences:
        old=[sk for sk in o.component.sketches if '_export_face_DRAFT' in sk.name]
        for sk in old:sk.deleteMe()
    # addTwoPointRectangle creates topology, but no H/V constraints in this build.
    constrained=[]
    for occ in root.occurrences:
        for sk in occ.component.sketches:
            if sk.sketchCurves.sketchLines.count==4 and sk.sketchCurves.sketchCircles.count==0 and sk.sketchDimensions.count>=2 and not sk.isFullyConstrained:
                lines=sk.sketchCurves.sketchLines
                for i in (0,2):sk.geometricConstraints.addHorizontal(lines.item(i))
                for i in (1,3):sk.geometricConstraints.addVertical(lines.item(i))
                assert sk.isFullyConstrained,sk.name
                constrained.append(sk.name)
    report['rectangles_constrained']=constrained
    sketches=[{'component':o.component.name,'sketch':sk.name,'fully_constrained':sk.isFullyConstrained} for o in root.occurrences for sk in o.component.sketches]
    assert all(s['fully_constrained'] for s in sketches), 'Unconstrained sketches remain'
    report['sketches']=sketches
    # Verify that editing width actually changes the panel and returns to its source state.
    width=design.userParameters.itemByName('width')
    original=width.expression
    right=next(o.component for o in root.occurrences if o.component.name=='Side_right')
    before=right.bRepBodies.item(0).boundingBox.maxPoint.x
    width.expression=f'{width.value*10+10:.12g} mm'
    design.computeAll()
    moved=right.bRepBodies.item(0).boundingBox.maxPoint.x
    width.expression=original
    design.computeAll()
    restored=right.bRepBodies.item(0).boundingBox.maxPoint.x
    assert abs(moved-before-1)<1e-6 and abs(restored-before)<1e-6,'Width change did not propagate/restore'
    report['width_edit_test']={'delta_input_mm':10,'delta_panel_mm':(moved-before)*10,'restored':True,'note':'Dependent volume-budget lengths regenerated from Python when design input changes.'}
    entities=adsk.core.ObjectCollection.create()
    for occ in root.occurrences:entities.add(occ)
    inp=design.createInterferenceInput(entities)
    inp.areCoincidentFacesIncluded=False
    interferences=design.analyzeInterference(inp)
    clashes=[]
    for i in range(interferences.count):
        clash=interferences.item(i)
        clashes.append({'entity_one':clash.entityOne.name,'entity_two':clash.entityTwo.name,'volume_cm3':clash.interferenceBody.volume})
    report['interferences']=clashes
    assert not clashes, f'Interferences found: {clashes}'
    issues=[]
    for i in range(design.timeline.count):
        entry=design.timeline.item(i)
        if entry.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            issues.append({'name':entry.name,'message':entry.errorOrWarningMessage})
    assert not issues,issues
    report['timeline_issues']=issues
    # Supplied masses are not replaced by volumes of solid clearance envelopes.
    wood_volume=sum(sum(b.volume for b in o.component.bRepBodies) for o in root.occurrences if not o.component.name.startswith(('REF_','RESERVE_','Port_','LF_steel_','Rear_thread_plate_')))
    report['steel_backing_mass_kg_assumed_7850kg_m3']=next(o.component for o in root.occurrences if o.component.name=='LF_steel_backing_ring_candidate').bRepBodies.item(0).volume*.00785
    report['rear_thread_plates_mass_kg_assumed_7850kg_m3']=sum(o.component.bRepBodies.item(0).volume for o in root.occurrences if o.component.name.startswith('Rear_thread_plate_'))*.00785
    report['solid_bodies']=[{'component':o.component.name,'body':b.name,'solid':b.isSolid,'volume_cm3':b.volume,'size_mm':[(b.preciseBoundingBox.maxPoint.asArray()[i]-b.preciseBoundingBox.minPoint.asArray()[i])*10 for i in range(3)]} for o in root.occurrences for b in o.component.bRepBodies]
    report['wood_volume_cm3']=wood_volume
    report['wood_mass_kg_density_600_to_700']=[wood_volume*.0006,wood_volume*.0007]
    report['weight_status']='Assembly mass unknown until battery, fasteners, grille, straps and finish are selected; quality over mass per user; 24mm laminated baffle, backing ring and rear assembly cleats increase mass.'
    # Camera faces the XY baffle from negative Z, with Y vertical.
    def camera(eye,target,path):
        cam=app.activeViewport.camera
        cam.eye=adsk.core.Point3D.create(*eye)
        cam.target=adsk.core.Point3D.create(*target)
        cam.upVector=adsk.core.Vector3D.create(0,1,0)
        cam.isFitView=True
        cam.isSmoothTransition=False
        app.activeViewport.camera=cam
        app.activeViewport.refresh()
        assert app.activeViewport.saveAsImageFile(str(OUT/path),1400,1000)
    camera((85,75,-100),(16.5,26,10),'OPEN_LOUD_A0_E03_front.png')
    hidden=[]
    for o in root.occurrences:
        if o.component.name in ('Side_right','Rear_removable','Top'):
            hidden.append(o);o.isLightBulbOn=False
    camera((100,65,110),(16.5,26,15),'OPEN_LOUD_A0_E03_inside.png')
    for o in hidden:o.isLightBulbOn=True
    camera((85,75,-100),(16.5,26,10),'OPEN_LOUD_A0_E03.png')
    manager=design.exportManager
    assert manager.execute(manager.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E03.step'),root))
    assert manager.execute(manager.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E03.f3d')))
    # Export separate planar panel outlines from actual BRep faces.
    dxf=[]
    for occ in root.occurrences:
        cp=occ.component
        if cp.name.startswith(('REF_','RESERVE_','Port_')):continue
        faces=[f for b in cp.bRepBodies for f in b.faces if f.geometry.surfaceType==adsk.core.SurfaceTypes.PlaneSurfaceType]
        if cp.name.startswith('Rear_cleat_'):
            face=max((f for f in faces if abs(f.geometry.normal.z)>.999),key=lambda f:f.area)
        elif cp.name=='Baffle':
            face=next(f for f in faces if abs(f.centroid.z)<1e-6 and f.area>500)
        else:face=max(faces,key=lambda f:f.area)
        sk=cp.sketches.add(face);sk.name=cp.name+'_export_face_DRAFT';sk.isLightBulbOn=False
        name=cp.name+'_E03_DRAFT.dxf'
        assert sk.saveAsDXF(str(OUT/name));dxf.append(name)
    rear=next(o.component for o in root.occurrences if o.component.name=='Rear_removable')
    gasket=next(sk for sk in rear.sketches if sk.name=='Rear_gasket_recess')
    assert gasket.saveAsDXF(str(OUT/'Rear_gasket_recess_E03_DRAFT.dxf'))
    dxf.append('Rear_gasket_recess_E03_DRAFT.dxf')
    report['dxf_exports']=dxf
    # Native export includes the final derived export sketches and visibility state.
    assert manager.execute(manager.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E03.f3d')))
    report['saved']=app.activeDocument.isSaved
    report['cloud_file_id']=app.activeDocument.dataFile.id if app.activeDocument.dataFile else None
    (OUT/'fusion_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fully_constrained_sketches':len(sketches),'interferences':clashes,'parameter_test':report['width_edit_test'],'wood_mass_kg':report['wood_mass_kg_density_600_to_700'],'dxf_exports':dxf}))
