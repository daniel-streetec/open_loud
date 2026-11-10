"""Reimport E09 checkpoint exports; preserve all user-open documents."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E09')
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
    assert source.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(source.products.itemByProductType('DesignProductType'))
    expected=metrics(d.rootComponent);physical=metrics(d.rootComponent,True)
    paths=sorted(o.fullPathName for o in d.rootComponent.allOccurrences)
    pars={p.name:p.value for p in d.userParameters};reports=[]
    for kind in ('native','STEP'):
        manager=app.importManager
        options=manager.createFusionArchiveImportOptions(str(OUT/'OPEN_LOUD_A0_E09_checkpoint.f3d')) if kind=='native' else manager.createSTEPImportOptions(str(OUT/'OPEN_LOUD_A0_E09_checkpoint.step'))
        doc=manager.importToNewDocument(options);assert doc
        try:
            imported=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            observed=metrics(imported.rootComponent);compare(expected if kind=='native' else physical,observed)
            if kind=='native':
                assert {p.name:p.value for p in imported.userParameters}==pars
                assert sorted(o.fullPathName for o in imported.rootComponent.allOccurrences)==paths,'Native hierarchy changed'
            reports.append(dict(format=kind,status='passed',observed=observed))
        finally:doc.close(False);source.activate()
    project=next(p for p in app.data.dataProjects if p.name=='OPEN_LOUD')
    validation=json.loads((OUT/'power_validation.json').read_text(encoding='utf-8'))
    note=f"E09 checkpoint; {len(validation['interferences'])} screened overlaps; incomplete hardware and thermal qualification, not fabrication release"
    assert source.save(note) if source.isSaved else source.saveAs(source.name,project.rootFolder,note,'E09')
    (OUT/'export_validation.json').write_text(json.dumps(dict(checkpoint_not_release=True,checks=reports,parameter_count=len(pars),native_hierarchy_preserved=True,occurrence_paths=len(paths)),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(reimports='passed',cloud_saved=source.isSaved)))
