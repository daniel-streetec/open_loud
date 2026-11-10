"""Verify grouping did not change or drop any native geometry or parameter."""
import adsk.core,adsk.fusion,json,sys,csv,hashlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E07'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import assemblies
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_E07_Assemblies')
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E07'
    baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'));structure=json.loads((ROOT/'data/assembly_structure.json').read_text(encoding='utf-8'))
    identity=adsk.core.Matrix3D.create().asArray();leaves=assemblies.leaf_occurrences(root)
    expected={r['component']:r for r in baseline['components']};actual={o.component.name:o for o in leaves}
    assert len(leaves)==len(actual)==len(expected) and actual.keys()==expected.keys(),'Leaf inventory changed'
    for occ in root.allOccurrences:
        if not occ.component.bRepBodies.count:
            assert max(abs(a-b) for a,b in zip(occ.transform2.asArray(),identity))<1e-10,'Container transform not identity'
    errors=[];max_delta=0;body_count=0
    for name,occ in actual.items():
        old=expected[name];cp=occ.component
        assert max(abs(a-b) for a,b in zip(occ.transform2.asArray(),old['transform']))<1e-10,(name,'placement changed')
        path=assemblies.classify(name,structure)
        assert all(segment in occ.fullPathName for segment in path.split('/')),(name,occ.fullPathName,path)
        assert cp.bRepBodies.count==len(old['bodies']),(name,'body count changed')
        bodies={b.name:b for b in cp.bRepBodies}
        for record in old['bodies']:
            b=bodies[record['name']];assert b.isSolid==record['solid'];body_count+=1
            delta=abs(b.volume-record['volume_cm3']);max_delta=max(max_delta,delta)
            assert delta<max(1e-7,record['volume_cm3']*1e-9),(name,'volume changed',delta)
            for point,key in ((b.boundingBox.minPoint,'min_cm'),(b.boundingBox.maxPoint,'max_cm')):
                assert max(abs(a-b) for a,b in zip(point.asArray(),record[key]))<1e-7,(name,'bounds changed')
    assert {p.name:p.value for p in design.userParameters}==baseline['parameters'],'User parameter set changed'
    # Independent functional check of preserved native parametric relationships.
    width=design.userParameters.itemByName('width');expression=width.expression
    top=actual['Top'].component;before=top.bRepBodies.item(0).boundingBox.maxPoint.x
    width.expression='('+expression+') + 10 mm';design.computeAll()
    after=top.bRepBodies.item(0).boundingBox.maxPoint.x
    width.expression=expression;design.computeAll()
    restored=top.bRepBodies.item(0).boundingBox.maxPoint.x
    assert abs(after-before-1)<1e-6 and abs(restored-before)<1e-7,'Native dimension link did not survive reparenting'
    for i in range(design.timeline.count):
        item=design.timeline.item(i)
        if item.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:errors.append(dict(name=item.name,message=item.errorOrWarningMessage))
    assert not errors,errors
    # Module list: empty references and nonphysical keepouts are explicitly excluded from purchasing.
    inventory=[]
    for name,occ in actual.items():
        cp=occ.component;part=cp.attributes.itemByName('OPEN_LOUD','part');status=cp.attributes.itemByName('OPEN_LOUD','status')
        path=assemblies.classify(name,structure)
        inventory.append(dict(assembly=path,component=name,quantity=1,part=part.value if part else name,
            status=status.value if status else 'baseline_nominal_geometry',purchasing_included=path!='BG90_Referenzraeume'))
    with (OUT/'assembly_bom.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(inventory[0]));writer.writeheader();writer.writerows(sorted(inventory,key=lambda r:(r['assembly'],r['component'])))
    # Show a clean tree; subassemblies can be isolated and extracted independently.
    app.activeViewport.fit()
    assert app.activeViewport.saveAsImageFile(str(OUT/'assembly_overview.png'),1400,1000)
    em=design.exportManager
    assert em.execute(em.createSTEPExportOptions(str(OUT/'OPEN_LOUD_A0_E07.step'),root))
    assert em.execute(em.createFusionArchiveExportOptions(str(OUT/'OPEN_LOUD_A0_E07.f3d')))
    report=dict(status='passed',scope='Hierarchy, unchanged native solids/placement/parameters, functional width edit; not a new fit/safety approval',
        root_assemblies=[o.component.name for o in root.occurrences],leaf_components=len(leaves),solid_bodies=body_count,
        max_volume_change_cm3=max_delta,parameters_checked=len(baseline['parameters']),timeline_issues=errors,
        width_edit_test=dict(delta_input_mm=10,delta_top_panel_mm=(after-before)*10,restored=True),
        planned_not_modeled=structure['planned_not_modeled'])
    (OUT/'hierarchy_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    sources=['data/parameters.json','data/assembly_structure.json','hardware/mechanical/assemblies.py',
        'hardware/mechanical/prepare_assemblies_e07.py','hardware/mechanical/organize_assemblies_e07.py','hardware/mechanical/verify_assemblies_e07.py']
    (OUT/'manifest.json').write_text(json.dumps(dict(source_sha256={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
