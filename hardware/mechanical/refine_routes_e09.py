"""Replace only owned E09 cable route bodies after a recorded routing correction."""
import adsk.core,adsk.fusion,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    for o in list(d.rootComponent.occurrences):
        if o.component.name.startswith('E09_ROUTE_'):o.deleteMe()
    import add_harness_e09;importlib.reload(add_harness_e09);add_harness_e09.run(_context)
