"""Import exported STEP into an isolated document and compare with the source."""
import adsk.core, adsk.fusion
import json
from pathlib import Path

OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E03')

def metrics(design):
    root=design.rootComponent
    bodies=list(root.bRepBodies)
    bodies += [b for o in root.allOccurrences for b in o.component.bRepBodies]
    bounds=root.boundingBox
    return {'body_count':len(bodies),'solid_count':sum(b.isSolid for b in bodies),
            'total_solid_volume_cm3':sum(b.volume for b in bodies),
            'bounds_mm':{'min':[v*10 for v in bounds.minPoint.asArray()],'max':[v*10 for v in bounds.maxPoint.asArray()]}}

def run(_context: str):
    app=adsk.core.Application.get()
    source_doc=app.activeDocument
    source_design=adsk.fusion.Design.cast(app.activeProduct)
    assert source_design.rootComponent.attributes.itemByName('OPEN_LOUD','revision').value=='E03'
    source=metrics(source_design)
    options=app.importManager.createSTEPImportOptions(str(OUT/'OPEN_LOUD_A0_E03.step'))
    imported_doc=app.importManager.importToNewDocument(options)
    assert imported_doc,'STEP import failed'
    imported=metrics(adsk.fusion.Design.cast(app.activeProduct))
    assert source['body_count']==imported['body_count'],(source,imported)
    assert imported['solid_count']==imported['body_count']
    volume_error=abs(source['total_solid_volume_cm3']-imported['total_solid_volume_cm3'])
    assert volume_error/source['total_solid_volume_cm3']<1e-6,(source,imported)
    for endpoint in ('min','max'):
        assert all(abs(a-b)<1e-5 for a,b in zip(source['bounds_mm'][endpoint],imported['bounds_mm'][endpoint]))
    report={'volume_absolute_error_cm3':volume_error,'relative_volume_tolerance':1e-6,'status':'passed','source':source,'STEP_reimport':imported,'scope':'solids, aggregate volumes and bounds; no surface-detail or manufacturing approval'}
    (OUT/'step_roundtrip.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Only our newly created import-check document is closed/discarded.
    imported_doc.close(False)
    source_doc.activate()
    print(json.dumps(report))
