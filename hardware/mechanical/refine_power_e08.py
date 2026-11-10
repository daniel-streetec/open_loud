"""Resolve known E08 placement clashes; keep conservative converter envelope flagged."""
import adsk.core,adsk.fusion,sys,json,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent;F=cad_parts.Parts(root)
    for o in list(root.occurrences):
        if o.component.name in ('E08_F2_charge7p5A_holder','E08_F3_output5A_holder','E08_Battery_bottom_pad') or o.component.name.startswith('E08_ROUTE_'):o.deleteMe()
    pad=F.box([.147,.015,.171],[.195,.003,.130])
    for x in (.190,.280):F.subtract(pad,F.box([x-.0125,.014,.169],[.025,.0035,.134]))
    F.component('E08_Battery_bottom_pad',[pad],'OWN_BATTERY_PAD_3MM','foam_with_strap_reliefs_material_compression_unverified')
    F.component('E08_F2_charge7p5A_holder',[F.box([.265,.155,.307],[.034,.022,.018])],'LITTELFUSE_FHAC0001ZXJ','reserved_holder_envelope_actual_measure_before_mounting')
    F.component('E08_F3_output5A_holder',[F.box([.200,.350,.270],[.034,.022,.018])],'LITTELFUSE_FHAC0001ZXJ','reserved_holder_envelope_actual_measure_before_mounting')
    for name,route in json.loads((ROOT/'results/power/E08/harness.json').read_text(encoding='utf-8'))['routes'].items():
        bodies=[]
        for a,b in zip(route['points_m'],route['points_m'][1:]):
            if sum((x-y)**2 for x,y in zip(a,b))>1e-16:bodies.append(F.cylinder(a,b,route['outer_diameter_m']/2))
        F.component('E08_ROUTE_'+name,bodies,'WIRE_4MM2_SINGLE' if name.startswith('main') else 'CORDIAL_CLS215','sampled_bend_envelope_tails_and_slack_unlocated')
    d.computeAll();print(json.dumps({'replaced_parts':F.created}))
