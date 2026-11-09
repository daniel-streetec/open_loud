"""Constrain rectangles, inspect collisions, test parameter response and export."""
import adsk.core, adsk.fusion
import json, math
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
OUT=ROOT/'hardware/mechanical/exports'

def run(_context: str):
    app=adsk.core.Application.get()
    design=adsk.fusion.Design.cast(app.activeProduct)
    root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E02'
    design.userParameters.itemByName('horn_flange').expression='5.5 mm'
    design.computeAll()
    report=json.loads((OUT/'fusion_validation.json').read_text(encoding='utf-8'))
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
    wood_volume=sum(o.component.bRepBodies.item(0).volume for o in root.occurrences if not o.component.name.startswith(('REF_','RESERVE_','Port_')))
    report['wood_volume_cm3']=wood_volume
    report['wood_mass_kg_density_600_to_700']=[wood_volume*.0006,wood_volume*.0007]
    report['weight_status']='Assembly mass unknown until battery, fasteners, grille, straps and finish are selected; wood + LF + HF + horn only already near 10kg.'
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
    camera((85,75,-100),(16.5,26,10),'OPEN_LOUD_A0_E02_front.png')
    hidden=[]
    for o in root.occurrences:
        if o.component.name in ('Side_right','Rear_removable','Top'):
            hidden.append(o);o.isLightBulbOn=False
    camera((100,65,110),(16.5,26,15),'OPEN_LOUD_A0_E02_inside.png')
    for o in hidden:o.isLightBulbOn=True
    camera((85,75,-100),(16.5,26,10),'OPEN_LOUD_A0_E02.png')
    manager=design.exportManager
    assert manager.execute(manager.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E02.step'),root))
    assert manager.execute(manager.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E02.f3d')))
    # Export separate planar panel outlines from actual BRep faces.
    dxf=[]
    for occ in root.occurrences:
        cp=occ.component
        if cp.name.startswith(('REF_','RESERVE_','Port_')):continue
        if cp.name=='Baffle':
            sk=next(s for s in cp.sketches if s.name=='Baffle_export_face_DRAFT')
        else:
            # Largest panel face, including YZ/XZ for sides/top/bottom.
            faces=[f for b in cp.bRepBodies for f in b.faces if f.geometry.surfaceType==adsk.core.SurfaceTypes.PlaneSurfaceType]
            face=max(faces,key=lambda f:f.area)
            sketch_name=cp.name+'_export_face_DRAFT_v2'
            sk=next((s for s in cp.sketches if s.name==sketch_name),None)
            if sk is None:
                sk=cp.sketches.add(face);sk.name=sketch_name;sk.isLightBulbOn=False
        name=cp.name+'_E02_DRAFT.dxf'
        assert sk.saveAsDXF(str(OUT/name));dxf.append(name)
    report['dxf_exports']=dxf
    # Native export includes the final derived export sketches and visibility state.
    assert manager.execute(manager.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E02.f3d')))
    report['saved']=app.activeDocument.isSaved
    report['cloud_file_id']=app.activeDocument.dataFile.id if app.activeDocument.dataFile else None
    (OUT/'fusion_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fully_constrained_sketches':len(sketches),'interferences':clashes,'parameter_test':report['width_edit_test'],'wood_mass_kg':report['wood_mass_kg_density_600_to_700'],'dxf_exports':dxf}))
