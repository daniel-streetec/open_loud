"""Own native geometry tessellation for honest CAD-derived shaded review views."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E05')
def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct)
    assert d.rootComponent.attributes.itemByName('OPEN_LOUD','revision').value=='E05'
    rows=[]
    for o in d.rootComponent.occurrences:
        n=o.component.name
        if n.startswith(('E05_','RESERVE_')):continue
        nodes=[];indices=[]
        for b in o.component.bRepBodies:
            calc=b.meshManager.createMeshCalculator();calc.surfaceTolerance=.03;mesh=calc.calculate();assert mesh
            offset=len(nodes);nodes.extend([[v*10 for v in p.asArray()] for p in mesh.nodeCoordinates])
            indices.extend([i+offset for i in mesh.nodeIndices])
        rows.append(dict(name=n,nodes_mm=nodes,indices=indices))
    payload=dict(revision='E05',parts=rows,note='Own simplified CAD reference geometry, not verified supplier solids.')
    (OUT/'mesh_geometry.json').write_text(json.dumps(payload,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'parts':len(rows),'triangles':sum(len(r['indices'])//3 for r in rows)}))
