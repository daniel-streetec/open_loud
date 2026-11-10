"""Open a separate E07 copy; record the unmodified E06 assembly as reference."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E07'
def run(_context: str):
    app=adsk.core.Application.get();name='OPEN_LOUD_A0_E07_Assemblies'
    assert not any(d.name.startswith(name) for d in app.documents),'E07 already open; inspect existing document'
    archive=ROOT/'hardware/mechanical/exports/E06/OPEN_LOUD_A0_E06_PAUSED.f3d'
    doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(str(archive)))
    assert doc;doc.name=name
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E06'
    records=[]
    for occ in root.occurrences:
        cp=occ.component
        records.append(dict(component=cp.name,bodies=[dict(name=b.name,solid=b.isSolid,volume_cm3=b.volume,
            min_cm=b.boundingBox.minPoint.asArray(),max_cm=b.boundingBox.maxPoint.asArray()) for b in cp.bRepBodies],
            transform=occ.transform2.asArray()))
    report=dict(source_archive=str(archive.relative_to(ROOT)),document=doc.name,components=records,
        parameters={p.name:p.value for p in design.userParameters})
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'baseline.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'document':doc.name,'leaves':len(records),'names':[r['component'] for r in records]}))
