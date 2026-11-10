"""Own cable route envelopes. Tails/slack are allowances, not falsely located geometry."""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud')
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert not any(o.component.name.startswith('E08_ROUTE_') for o in root.occurrences),'Already built'
    F=cad_parts.Parts(root)
    data=json.loads((ROOT/'results/power/E08/harness.json').read_text(encoding='utf-8'))
    # Move the reserved F3 holder clear of the expanded tray and PCB.
    occ=next(o for o in root.occurrences if o.component.name=='E08_F3_output5A_holder')
    t=occ.transform2;t.translation=adsk.core.Vector3D.create(4.5,0,0);occ.transform2=t
    for name,route in data['routes'].items():
        points=route['points_m'];bodies=[]
        for a,b in zip(points,points[1:]):
            if sum((x-y)**2 for x,y in zip(a,b))<1e-16:continue
            bodies.append(F.cylinder(a,b,route['outer_diameter_m']/2))
        F.component('E08_ROUTE_'+name,bodies,'WIRE_4MM2_SINGLE' if name.startswith('main') else 'CORDIAL_CLS215',
            'sampled_bend_envelope_terminal_tails_and_service_slack_not_located','results/power/E08/harness.json')
    design.computeAll()
    print(json.dumps({'routes_added':len(data['routes']),'status':'collision_check_pending'}))
