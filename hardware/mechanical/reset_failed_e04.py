"""Discard only our unsaved, incomplete E04 generation after a failed run."""
import adsk.core, adsk.fusion

def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name=='OPEN_LOUD_A0_E04_Integration' and not doc.isSaved
    root=adsk.fusion.Design.cast(app.activeProduct).rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','integration_ready') is None
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E04'
    doc.close(False)
    print('Discarded own unsaved failed E04 generation; saved E03 untouched')
