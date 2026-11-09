"""Export own CAD edges for reproducible orthographic and exploded review sheets."""
import adsk.core,adsk.fusion,json
from pathlib import Path
OUT=Path(r'C:\Repositories\open_loud\hardware\mechanical\exports\E05')
def run(_context: str):
    app=adsk.core.Application.get();d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','revision').value=='E05'
    rows=[]
    for o in root.occurrences:
        cp=o.component
        if cp.name.startswith('E05_cable_'):continue # Jackets would obscure assembly sheets.
        polylines=[]
        for body in cp.bRepBodies:
            for edge in body.edges:
                evaluator=edge.evaluator;ok,start,end=evaluator.getParameterExtents();assert ok
                ok,points=evaluator.getStrokes(start,end,.03);assert ok # 0.3mm chord tolerance.
                polylines.append([[v*10 for v in p.asArray()] for p in points])
        bb=cp.boundingBox
        rows.append(dict(name=cp.name,edges_mm=polylines,bounds_mm=[[v*10 for v in bb.minPoint.asArray()],[v*10 for v in bb.maxPoint.asArray()]],
            status=cp.attributes.itemByName('OPEN_LOUD','status').value if cp.attributes.itemByName('OPEN_LOUD','status') else 'baseline_E03'))
    payload=dict(revision='E05',unit='mm',edge_chord_tolerance_mm=.3,hidden_line_removal=False,parts=rows,
        note='Own CAD edge strokes; reference drivers simplified. All edges shown; review drawing, not production release.')
    (OUT/'drawing_geometry.json').write_text(json.dumps(payload,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'components':len(rows),'polylines':sum(len(r['edges_mm']) for r in rows)}))
