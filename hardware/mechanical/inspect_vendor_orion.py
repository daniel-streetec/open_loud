"""Inspect official STEP in a temporary document; never bundle vendor geometry."""
import adsk.core,adsk.fusion,json,hashlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');FILE=ROOT/'.tools/references/orion-small.step'
def run(_context: str):
    app=adsk.core.Application.get();source=app.activeDocument
    assert source.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    doc=app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(str(FILE)));assert doc
    try:
        d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
        holes=[];bodies=[];world=[];tm=adsk.fusion.TemporaryBRepManager.get();mainmatrix=None
        for b in root.bRepBodies:world.append(tm.copy(b))
        for o in root.allOccurrences:
            for b in o.component.bRepBodies:
                body=tm.copy(b);assert tm.transform(body,o.transform2);world.append(body)
                if any(f.geometry.surfaceType==adsk.core.SurfaceTypes.CylinderSurfaceType and abs(f.geometry.radius-.19)<1e-5 for f in b.faces):mainmatrix=o.transform2
        allb=list(root.bRepBodies)+[b for o in root.allOccurrences for b in o.component.bRepBodies]
        for b in allb:
            bb=b.boundingBox;bodies.append(dict(name=b.name,min_cm=bb.minPoint.asArray(),max_cm=bb.maxPoint.asArray()))
            for f in b.faces:
                g=f.geometry
                if g.surfaceType==adsk.core.SurfaceTypes.CylinderSurfaceType and abs(g.radius-.19)<1e-5:
                    bb=f.boundingBox;holes.append(dict(radius_cm=g.radius,axis=g.axis.asArray(),origin_cm=g.origin.asArray(),min_cm=bb.minPoint.asArray(),max_cm=bb.maxPoint.asArray()))
        access=[]
        for x in (-4.94,4.94):
            for z in (-4.21,4.21):
                tool=tm.createCylinderOrCone(adsk.core.Point3D.create(x,.20001,z),.4,adsk.core.Point3D.create(x,1.5,z),.4)
                assert mainmatrix is not None;assert tm.transform(tool,mainmatrix)
                overlaps=[]
                for b in world:
                    clone=tm.copy(tool)
                    if not tm.booleanOperation(clone,b,adsk.fusion.BooleanTypes.IntersectionBooleanType):raise RuntimeError('Vendor intersection operation failed')
                    if clone.isValid and clone.faces.count and clone.volume>1e-7:overlaps.append(clone.volume)
                access.append(dict(x_cm=x,z_cm=z,radius_cm=.4,from_y_cm=.20001,to_y_cm=1.5,overlaps_cm3=overlaps))
        bb=root.boundingBox
        report=dict(source_url='https://www.victronenergy.com/upload/documents/Orion-Tr-110W-120W-Isolated-%28stp%29.STEP',
            sha256=hashlib.sha256(FILE.read_bytes()).hexdigest(),bodies=bodies,mounting_cylinders=holes,
            root_min_cm=bb.minPoint.asArray(),root_max_cm=bb.maxPoint.asArray(),mount_tool_access=access,
            limitations=['Supplier nominal geometry, not measurement of purchased sample.','Vendor geometry not copied into public model or Git repository.'])
        (ROOT/'.tools/orion_inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report))
    finally:doc.close(False);source.activate()
