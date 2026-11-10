"""Save only the owned OPEN_LOUD E06 document on explicit user pause."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud')
def run(_context: str):
    app=adsk.core.Application.get()
    docs=[d for d in app.documents if d.name.startswith('OPEN_LOUD_A0_E06_Electronics')]
    if not docs:
        print(json.dumps({'saved':False,'reason':'E06 document not open; existing native archive remains on disk'}));return
    doc=docs[0];doc.activate()
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    assert design.rootComponent.attributes.itemByName('OPEN_LOUD','revision').value=='E06'
    note='User pause checkpoint E06 WIP; not fully verified, no manufacturing release'
    if doc.isSaved:success=doc.save(note)
    else:
        project=next(p for p in app.data.dataProjects if p.name=='OPEN_LOUD')
        success=doc.saveAs(doc.name,project.rootFolder,note,'E06 WIP paused')
    assert success
    report=dict(saved=doc.isSaved,document=doc.name,status='PAUSED_WIP_NOT_RELEASED')
    out=ROOT/'hardware/mechanical/exports/E06';out.mkdir(parents=True,exist_ok=True)
    assert design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(str(out/'OPEN_LOUD_A0_E06_PAUSED.f3d')))
    (out/'pause_save_status.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
