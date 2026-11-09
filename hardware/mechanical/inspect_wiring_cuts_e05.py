import adsk.core,adsk.fusion,json
def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct);rows=[]
    for o in d.rootComponent.occurrences:
        cp=o.component
        if cp.name not in ('Service_floor','Service_partition'):continue
        for sk in cp.sketches:
            if not sk.name.startswith('E05_'):continue
            rows.append(dict(component=cp.name,sketch=sk.name,origin=sk.origin.asArray(),centers=[sk.sketchToModelSpace(c.centerSketchPoint.geometry).asArray() for c in sk.sketchCurves.sketchCircles]))
        for ft in cp.features.extrudeFeatures:
            if ft.name in ('Extrusion6','Extrusion7'):rows.append(dict(feature=ft.name,health=str(ft.healthState),message=ft.errorOrWarningMessage,body_bounds=[dict(min=b.boundingBox.minPoint.asArray(),max=b.boundingBox.maxPoint.asArray()) for b in cp.bRepBodies]))
    print(json.dumps(rows))

