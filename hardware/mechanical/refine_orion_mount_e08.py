"""Rebuild own conservative converter envelope with supplier-verified free regions."""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    p={k:v['value'] for k,v in data['orion_mount_e08'].items()};co=data['battery_mount']['converter_origin']['value'];cs=data['battery_mount']['converter_size']['value']
    verification=json.loads((ROOT/'data/verification/orion_mount.json').read_text(encoding='utf-8'))
    assert all(not h for h in verification['access_overlap_cm3'])
    F=cad_parts.Parts(root)
    for o in list(root.occurrences):
        n=o.component.name
        if n=='E08_Orion_12_24_5_converter' or (n.startswith('E08_Orion_') and n.endswith(('_rear_washer','_nut'))):o.deleteMe()
    body=F.box(co,[cs[0],cs[1],p['depth_keepout']]);index=0
    for sx in (-1,1):
        for sy in (-1,1):
            x=co[0]+cs[0]/2+sx*p['hole_pitch'][0]/2;y=co[1]+cs[1]/2+sy*p['hole_pitch'][1]/2
            F.subtract(body,F.cylinder([x,y,co[2]-.001],[x,y,co[2]+p['depth_keepout']+.001],p['hole_diameter']/2))
            # Free cylinder is proven in official STEP up to15mm, not assumed through the whole case.
            F.subtract(body,F.cylinder([x,y,co[2]+p['ear_thickness']],[x,y,co[2]+p['verified_access_depth']],p['verified_access_radius']))
            F.washerz(f'E08_Orion_{index}_rear_washer',x,y,co[2]+p['ear_thickness'],3)
            F.nutz(f'E08_Orion_{index}_nut',x,y,co[2]+p['ear_thickness']+.0005,3);index+=1
    F.component('E08_Orion_12_24_5_converter',[body],'VICTRON_ORI122410110','own_conservative_envelope_supplier_STEP_verified_mounting_access',verification['source_url'])
    d.computeAll();print(json.dumps({'mount_ears_mm':p['ear_thickness']*1000,'verified_tool_access_diameter_mm':p['verified_access_radius']*2000,'supplier_geometry_redistributed':False}))
