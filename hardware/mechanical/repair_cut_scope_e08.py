"""Restrict two owned floor-notch cuts to the floor, restoring continuous cleats."""
import adsk.core, adsk.fusion, json

def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct)
    assert d.rootComponent.attributes.itemByName('OPEN_LOUD','revision').value=='E08'
    floor=next(o.component for o in d.rootComponent.occurrences if o.component.name=='Service_floor')
    # Recreate instead of editing old cached timeline entities: this Fusion build
    # otherwise exposes rolled-back timeline wrappers for healthy edited features.
    for o in d.rootComponent.occurrences:
        for sk in [s for s in o.component.sketches if '_export_face_DRAFT' in s.name]:sk.deleteMe()
    cuts=[f for f in floor.features.extrudeFeatures if hasattr(f.profile,'parentSketch') and f.profile.parentSketch.name.startswith('Cleat_corner_notch')]
    assert len(cuts)==2
    sketches=[f.profile.parentSketch for f in cuts]
    for f in sorted(cuts,key=lambda f:f.timelineObject.index,reverse=True):f.deleteMe()
    d.timeline.moveToEnd()
    for sk in sketches:
        inp=floor.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('rear_cleat_depth')),adsk.fusion.ExtentDirections.PositiveExtentDirection)
        inp.participantBodies=list(floor.bRepBodies)
        floor.features.extrudeFeatures.add(inp)
    d.computeAll()
    cleats=[o.component for o in d.rootComponent.occurrences if o.component.name.startswith('Rear_cleat_')]
    assert all(c.bRepBodies.count==1 for c in cleats),'Cleats still split'
    print(json.dumps({'floor_cuts_scoped':len(cuts),'continuous_cleats':len(cleats)}))
