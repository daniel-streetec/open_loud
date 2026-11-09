"""Repair owned LF cuts and regenerate ONLY E05 cable routes after kernel review."""
import adsk.core,adsk.fusion,json,sys,importlib,math
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud')
sys.path.insert(0,str(ROOT/'tools'))
import generate_wiring;importlib.reload(generate_wiring)
def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','wiring_ready').value=='E05'
    floor=next(o.component for o in root.occurrences if o.component.name=='Service_floor')
    cuts=[ft for ft in floor.features.extrudeFeatures if hasattr(ft.profile,'parentSketch') and ft.profile.parentSketch.name.startswith('E05_LF_')]
    sketches=[ft.profile.parentSketch for ft in cuts]
    for ft in sorted(cuts,key=lambda f:f.timelineObject.index,reverse=True):ft.deleteMe()
    for sk in sketches:sk.deleteMe()
    d.timeline.moveToEnd();V=adsk.core.ValueInput.createByString;P=adsk.core.Point3D.create
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));w={k:v['value'] for k,v in data['wiring'].items()}
    for name,diameter,length in [('M16_through',w['gland_bore'],.012),('inside_counterbore',w['gland_counterbore_diameter'],w['gland_counterbore_depth'])]:
        pin=floor.constructionPlanes.createInput();pin.setByOffset(floor.xZConstructionPlane,V('350 mm'));plane=floor.constructionPlanes.add(pin);plane.isLightBulbOn=False
        sk=floor.sketches.add(plane);sk.name='E05_LF_'+name
        center=sk.modelToSketchSpace(P(27.5,35,24));circle_=sk.sketchCurves.sketchCircles.addByCenterRadius(center,diameter*50);circle_.isFixed=True
        inp=floor.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f'{length*1000} mm')),adsk.fusion.ExtentDirections.PositiveExtentDirection)
        inp.participantBodies=list(floor.bRepBodies);floor.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
    for sk in [sk for sk in root.sketches if sk.name.startswith('E05_centerline_')]:sk.deleteMe()
    for o in [o for o in root.occurrences if o.component.name.startswith('E05_cable_')]:o.deleteMe()
    tm=adsk.fusion.TemporaryBRepManager.get();calc=generate_wiring.calculate(data)
    def pt(a):return P(*(v*100 for v in a))
    for key,b in calc['branches'].items():
        cp=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;cp.name='E05_cable_'+key
        cp.attributes.add('OPEN_LOUD','status','jacket_route_only_service_slack_and_OEM_ends_not_geometry')
        cp.attributes.add('OPEN_LOUD','part','Cordial_CLS215_'+key)
        base=cp.features.baseFeatures.add();base.startEdit();points=b['route_points_m']
        for a,bb in zip(points,points[1:]):
            if math.dist(a,bb)>1e-8:cp.bRepBodies.add(tm.createCylinderOrCone(pt(a),w['cable_diameter']*50,pt(bb),w['cable_diameter']*50),base)
        base.finishEdit()
        sk=root.sketches.add(root.xYConstructionPlane);sk.name='E05_centerline_'+key;sk.is3D=True
        for a,bb in zip(points,points[1:]):
            if math.dist(a,bb)>1e-8:sk.sketchCurves.sketchLines.addByTwoPoints(pt(a),pt(bb))
        sk.isLightBulbOn=False
    d.computeAll();print(json.dumps({'LF_cuts_rebuilt':len(cuts),'routes_regenerated':list(calc['branches'])}))
