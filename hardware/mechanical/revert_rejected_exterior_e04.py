"""Archive and close only our rejected unsaved E04; show the saved E03 baseline."""
import adsk.core, adsk.fusion
from pathlib import Path

def run(_context: str):
    app=adsk.core.Application.get()
    rejected=next(d for d in app.documents if d.name=='OPEN_LOUD_A0_E04_Integration')
    assert not rejected.isSaved, 'Do not discard a saved/user-revised document'
    design=adsk.fusion.Design.cast(rejected.products.itemByProductType('DesignProductType'))
    assert design.rootComponent.attributes.itemByName('OPEN_LOUD','revision').value=='E04'
    assert sum(o.component.name.startswith('E04_') for o in design.rootComponent.occurrences)==65
    out=Path(r'C:\Repositories\open_loud\.tools\rejected');out.mkdir(parents=True,exist_ok=True)
    manager=design.exportManager
    assert manager.execute(manager.createFusionArchiveExportOptions(str(out/'E04_REJECTED_overbuilt.f3d')))
    rejected.close(False)
    source=next(d for d in app.documents if d.name=='OPEN_LOUD_A0_E03_Concept')
    source.activate()
    d=adsk.fusion.Design.cast(source.products.itemByProductType('DesignProductType'))
    assert not any(o.component.name.startswith('E04_') for o in d.rootComponent.occurrences)
    app.activeViewport.fit()
    print('Rejected unsaved E04 archived locally and closed. E03 active; no E04 attachments in E03.')
