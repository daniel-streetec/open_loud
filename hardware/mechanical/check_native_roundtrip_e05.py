"""Open the exported F3D and verify parameters, bodies and timeline health."""
import adsk.core, adsk.fusion
import json
from pathlib import Path

OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E05')

def run(_context: str):
    app=adsk.core.Application.get();source=app.activeDocument
    design=adsk.fusion.Design.cast(app.activeProduct)
    expected={p.name:p.value for p in design.userParameters}
    body_count=sum(o.component.bRepBodies.count for o in design.rootComponent.allOccurrences)+design.rootComponent.bRepBodies.count
    options=app.importManager.createFusionArchiveImportOptions(str(OUT/'OPEN_LOUD_A0_E05.f3d'))
    imported=app.importManager.importToNewDocument(options)
    assert imported,'Native archive import failed'
    actual=adsk.fusion.Design.cast(app.activeProduct)
    params={p.name:p.value for p in actual.userParameters}
    assert expected.keys()==params.keys()
    assert all(abs(v-params[k])<max(1e-8,abs(v)*1e-10) for k,v in expected.items())
    count=sum(o.component.bRepBodies.count for o in actual.rootComponent.allOccurrences)+actual.rootComponent.bRepBodies.count
    assert count==body_count
    issues=[]
    for i in range(actual.timeline.count):
        item=actual.timeline.item(i)
        if item.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append(item.errorOrWarningMessage)
    assert not issues,issues
    report={'status':'passed','parameters_checked':len(params),'solid_bodies':count,'timeline_issues':issues}
    (OUT/'native_roundtrip.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    imported.close(False);source.activate()
    print(json.dumps(report))
