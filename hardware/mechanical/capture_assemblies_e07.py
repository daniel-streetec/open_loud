"""Isolated real-CAD module views; restores original visibility afterwards."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E07')
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_E07_Assemblies')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    states=[(o,o.isLightBulbOn) for o in root.occurrences];images=[]
    def capture(path,cp,direction):
        bb=cp.boundingBox;target=[(a+b)/2 for a,b in zip(bb.minPoint.asArray(),bb.maxPoint.asArray())]
        cam=app.activeViewport.camera;cam.target=adsk.core.Point3D.create(*target)
        cam.eye=adsk.core.Point3D.create(*(a+b for a,b in zip(target,direction)))
        cam.upVector=adsk.core.Vector3D.create(0,1,0);cam.isFitView=True;cam.isSmoothTransition=False
        app.activeViewport.camera=cam;app.activeViewport.refresh();assert app.activeViewport.saveAsImageFile(str(path),1400,1000)
        images.append(path.name)
    try:
        for chosen in list(root.occurrences):
            if chosen.component.name.startswith('BG90'):continue
            for occ,state in states:occ.isLightBulbOn=occ==chosen
            direction=(35,45,45) if chosen.component.name=='BG40_Elektronikmodul' else (85,75,-100)
            capture(OUT/'subassemblies'/(chosen.component.name+'.png'),chosen.component,direction)
    finally:
        for occ,state in states:occ.isLightBulbOn=state
    capture(OUT/'assembly_overview.png',root,(85,75,-100))
    assert doc.save('E07 module views; geometry unchanged; no new engineering release')
    (OUT/'module_views.json').write_text(json.dumps(dict(images=images,scope='Actual CAD views, no beauty-render or manufacturing claim'),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'module_views':len(images)-1,'overview':True}))
