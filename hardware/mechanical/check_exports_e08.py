"""Reimport E08 checkpoint exports; preserve all user-open documents."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E08')
def metrics(root,visible=False):
    items=list(root.bRepBodies)+[b for o in root.allOccurrences for b in o.component.bRepBodies if not visible or (b.isLightBulbOn and o.isLightBulbOn)]
    bb=root.boundingBox
    return dict(bodies=len(items),solids=sum(b.isSolid for b in items),volume_cm3=sum(b.volume for b in items),min_cm=bb.minPoint.asArray(),max_cm=bb.maxPoint.asArray())
def compare(a,b):
    assert a['bodies']==b['bodies']==b['solids'],(a,b)
    assert abs(a['volume_cm3']-b['volume_cm3'])<max(1e-7,a['volume_cm3']*1e-6),(a,b)
    for key in ('min_cm','max_cm'):assert max(abs(x-y) for x,y in zip(a[key],b[key]))<1e-6,(a,b)
def run(_context: str):
    app=adsk.core.Application.get();source=app.activeDocument
    assert source.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(source.products.itemByProductType('DesignProductType'))
    expected=metrics(d.rootComponent);physical=metrics(d.rootComponent,True)
    pars={p.name:p.value for p in d.userParameters};reports=[]
    for kind in ('native','STEP'):
        manager=app.importManager
        options=manager.createFusionArchiveImportOptions(str(OUT/'OPEN_LOUD_A0_E08_checkpoint.f3d')) if kind=='native' else manager.createSTEPImportOptions(str(OUT/'OPEN_LOUD_A0_E08_checkpoint.step'))
        doc=manager.importToNewDocument(options);assert doc
        try:
            imported=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            observed=metrics(imported.rootComponent);compare(expected if kind=='native' else physical,observed)
            if kind=='native':assert {p.name:p.value for p in imported.userParameters}==pars
            reports.append(dict(format=kind,status='passed',observed=observed))
        finally:doc.close(False);source.activate()
    project=next(p for p in app.data.dataProjects if p.name=='OPEN_LOUD')
    note='E08 power packaging checkpoint; eight converter-envelope mounting clashes unresolved, not fabrication release'
    assert source.save(note) if source.isSaved else source.saveAs(source.name,project.rootFolder,note,'E08')
    (OUT/'export_validation.json').write_text(json.dumps(dict(checkpoint_not_release=True,checks=reports,parameter_count=len(pars)),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(reimports='passed',cloud_saved=source.isSaved)))
