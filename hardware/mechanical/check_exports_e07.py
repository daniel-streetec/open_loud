"""Actual native and STEP reimports, including individual physical subassemblies."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E07'
def metrics(cp,exclude_reference=False):
    bodies=list(cp.bRepBodies)+[b for o in cp.allOccurrences if not(exclude_reference and 'BG90_Referenzraeume' in o.fullPathName) for b in o.component.bRepBodies]
    bb=cp.boundingBox
    return dict(bodies=len(bodies),solid=sum(b.isSolid for b in bodies),volume_cm3=sum(b.volume for b in bodies),
        min_cm=bb.minPoint.asArray(),max_cm=bb.maxPoint.asArray())
def compare(a,b):
    assert a['bodies']==b['bodies']==b['solid'],(a,b)
    error=abs(a['volume_cm3']-b['volume_cm3'])
    assert error<max(1e-7,a['volume_cm3']*1e-6),(a,b)
    for key in ('min_cm','max_cm'):assert max(abs(x-y) for x,y in zip(a[key],b[key]))<1e-6,(key,a,b)
    return error
def run(_context: str):
    app=adsk.core.Application.get();source=app.activeDocument
    assert source and source.name.startswith('OPEN_LOUD_A0_E07_Assemblies')
    d=adsk.fusion.Design.cast(source.products.itemByProductType('DesignProductType'));root=d.rootComponent
    initial=metrics(root);paths=sorted(o.fullPathName for o in root.allOccurrences)
    parameters={p.name:p.value for p in d.userParameters}
    native=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(str(OUT/'OPEN_LOUD_A0_E07.f3d')))
    assert native
    try:
        actual=adsk.fusion.Design.cast(native.products.itemByProductType('DesignProductType'))
        native_error=compare(initial,metrics(actual.rootComponent))
        assert sorted(o.fullPathName for o in actual.rootComponent.allOccurrences)==paths,'Native hierarchy changed'
        assert {p.name:p.value for p in actual.userParameters}==parameters
        assert all(actual.timeline.item(i).healthState==adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState for i in range(actual.timeline.count))
    finally:native.close(False);source.activate()
    def step_check(path,expected):
        imported=app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(str(path)));assert imported
        try:
            model=adsk.fusion.Design.cast(imported.products.itemByProductType('DesignProductType'))
            observed=metrics(model.rootComponent);error=compare(expected,observed)
            return dict(file=path.name,status='passed',expected=expected,observed=observed,volume_error_cm3=error)
        finally:imported.close(False);source.activate()
    # STEP omits the two hidden nonphysical clearance references. Compare the
    # explicit physical assembly, rather than silently relaxing body counts.
    physical=metrics(root,exclude_reference=True)
    full_step=step_check(OUT/'OPEN_LOUD_A0_E07.step',physical)
    modules=[];directory=OUT/'subassemblies';directory.mkdir(exist_ok=True)
    for occ in list(root.occurrences):
        cp=occ.component
        if cp.name.startswith('BG90_'):continue
        path=directory/(cp.name+'.step')
        assert d.exportManager.execute(d.exportManager.createSTEPExportOptions(str(path),cp))
        modules.append(step_check(path,metrics(cp)))
    project=next(p for p in app.data.dataProjects if p.name=='OPEN_LOUD')
    note='E07 hierarchy and native/STEP reimports checked; engineering prototype, no fabrication release'
    saved=source.save(note) if source.isSaved else source.saveAs(source.name,project.rootFolder,note,'E07')
    assert saved
    report=dict(status='passed',saved=source.isSaved,native=dict(volume_error_cm3=native_error,parameters=len(parameters),occurrence_paths=len(paths),hierarchy_preserved=True),
        step=full_step,physical_subassemblies=modules,reference_spaces_separate_not_exported_as_module=True,
        STEP_scope='physical model; hidden nonphysical reference bodies omitted',reference_bodies_not_in_STEP=initial['bodies']-physical['bodies'])
    (OUT/'export_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'native_hierarchy':'passed','full_STEP':'passed','individual_STEP_modules':len(modules),'saved':source.isSaved}))
