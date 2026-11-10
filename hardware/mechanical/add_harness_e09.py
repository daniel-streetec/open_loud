"""Own cable route envelopes. Tails/slack are allowances, not falsely located geometry."""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud')
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent
    assert not any(o.component.name.startswith('E09_ROUTE_') for o in root.occurrences),'Already built'
    F=cad_parts.Parts(root)
    data=json.loads((ROOT/'results/power/E09/harness.json').read_text(encoding='utf-8'))
    for name,route in data['routes'].items():
        points=route['points_m'];bodies=[]
        for a,b in zip(points,points[1:]):
            if sum((x-y)**2 for x,y in zip(a,b))<1e-16:continue
            bodies.append(F.cylinder(a,b,route['outer_diameter_m']/2))
        F.component('E09_ROUTE_'+name,bodies,'WIRE_4MM2_SINGLE' if name.startswith('main') else 'CORDIAL_CLS215',
            'sampled_bend_envelope_terminal_tails_and_service_slack_not_located','results/power/E09/harness.json')
    design.computeAll()
    print(json.dumps({'routes_added':len(data['routes']),'status':'collision_check_pending'}))
