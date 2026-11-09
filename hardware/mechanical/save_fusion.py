"""Save the generated document into its dedicated Fusion project."""
import adsk.core, adsk.fusion, json
from pathlib import Path

def run(_context: str):
    app=adsk.core.Application.get()
    doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_')
    root=adsk.fusion.Design.cast(app.activeProduct).rootComponent
    revision=root.attributes.itemByName('OPEN_LOUD','revision').value
    assert revision in ('E02','E03','E05')
    project=next(p for p in app.data.dataProjects if p.name=='OPEN_LOUD')
    if doc.isSaved:
        success=doc.save(revision+' checked parametric concept')
    else:
        success=doc.saveAs(doc.name,project.rootFolder,revision+' concept; datasheet clearance models; no fabrication release',revision)
    assert success,'Save failed'
    output=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports')
    if revision in ('E03','E05'):output=output/revision
    report_path=output/'fusion_validation.json'
    if report_path.exists():
        report=json.loads(report_path.read_text(encoding='utf-8'));report.update(saved=doc.isSaved,cloud_file_id=doc.dataFile.id if doc.dataFile else None);report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'saved':doc.isSaved,'name':doc.name,'file_id':doc.dataFile.id if doc.dataFile else None}))
