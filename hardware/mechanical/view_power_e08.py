"""Save E08 draft inspection view and exchange export, without claiming release."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E08'
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    hidden=[]
    for o in root.allOccurrences:
        if o.component.name in ('Side_right','Rear_removable','Top') or 'External_' in o.component.name:
            hidden.append((o,o.isLightBulbOn));o.isLightBulbOn=False
    cam=app.activeViewport.camera;cam.eye=adsk.core.Point3D.create(95,75,110);cam.target=adsk.core.Point3D.create(18,28,20)
    cam.upVector=adsk.core.Vector3D.create(0,1,0);cam.isFitView=True;cam.isSmoothTransition=False
    app.activeViewport.camera=cam;app.activeViewport.refresh()
    assert app.activeViewport.saveAsImageFile(str(OUT/'power_inside_DRAFT.png'),1600,1200)
    for o,state in hidden:o.isLightBulbOn=state
    em=d.exportManager
    assert em.execute(em.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E08_checkpoint.step'),root))
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E08_checkpoint.f3d')))
    print(json.dumps({'view':'power_inside_DRAFT.png','exports':'STEP and F3D; roundtrip pending'}))
