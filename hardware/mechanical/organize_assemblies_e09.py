"""Reparent whole occurrences, retaining native part features and world placement."""
import adsk.core,adsk.fusion,json,sys,importlib,csv
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E09'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import assemblies;importlib.reload(assemblies)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc and doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert not root.attributes.itemByName('OPEN_LOUD','assembly_structure'),'Already structured; verify instead of re-running'
    structure=json.loads((ROOT/'data/assembly_structure_E09.json').read_text(encoding='utf-8'))
    original=list(root.occurrences);assignment={o.component.name:assemblies.classify(o.component.name,structure) for o in original}
    assert len(assignment)==len(original),'Duplicate part names; mapping would be ambiguous'
    groups={}
    for entry in sorted(structure['assemblies'],key=lambda e:e['path'].count('/')):
        path=entry['path'];parent_path,_,name=path.rpartition('/')
        parent=root if not parent_path else groups[parent_path].component
        occ=parent.occurrences.addNewComponent(adsk.core.Matrix3D.create());cp=occ.component;cp.name=name;cp.partNumber=entry['part_number']
        cp.attributes.add('OPEN_LOUD','assembly_role',entry['role']);cp.attributes.add('OPEN_LOUD','assembly_path',path)
        # Resolve nested occurrence in the root assembly context.
        groups[path]=next(o for o in root.allOccurrences if o.component.name==name)
    moved=[]
    for occ in original:
        name=occ.component.name;path=assignment[name]
        target=next(o for o in root.allOccurrences if o.component.name==path.split('/')[-1])
        result=occ.moveToComponent(target);assert result,f'Move failed: {name}'
        moved.append(dict(component=name,assembly=path,path=result.fullPathName))
    design.computeAll();root.attributes.add('OPEN_LOUD','revision','E09');root.attributes.add('OPEN_LOUD','assembly_structure','data/assembly_structure_E09.json')
    (OUT/'assembly_mapping.json').write_text(json.dumps(dict(revision='E09',moved=moved,structure=structure),indent=2)+'\n',encoding='utf-8')
    with (OUT/'assembly_parts.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['assembly','component','path']);writer.writeheader();writer.writerows(moved)
    print(json.dumps({'moved_parts':len(moved),'root_assemblies':[o.component.name for o in root.occurrences]}))
