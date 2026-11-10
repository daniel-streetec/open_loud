"""Actual modeled wood volumes with explicitly partial mass screening."""
import adsk.core,adsk.fusion,json
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');OUT=ROOT/'hardware/mechanical/exports/E08'
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    wood_names={'Side_left','Side_right','Bottom','Top','Baffle','Baffle_inner_lamination','Rear_removable','Service_partition','Service_floor','Brace_lower','E08_Battery_front_wall','E08_Battery_left_wall','E08_Battery_roof'}
    rows=[];wood_volume=0
    for o in d.rootComponent.allOccurrences:
        cp=o.component;volume=sum(b.volume for b in cp.bRepBodies)*1e-6
        if not cp.bRepBodies.count:continue
        wood=cp.name in wood_names or cp.name.startswith('Rear_cleat_')
        if wood:wood_volume+=volume
        part=cp.attributes.itemByName('OPEN_LOUD','part');status=cp.attributes.itemByName('OPEN_LOUD','status')
        rows.append(dict(component=cp.name,part=part.value if part else 'component:'+cp.name,assembly_path=o.fullPathName,body_volume_m3=volume,wood=wood,status=status.value if status else 'legacy_reference'))
    fixed=data['battery_mount']['battery_mass']['value']+data['drivers']['10FE200-4']['mass']['value']+data['orion_mount_e08']['mass']['value']
    bounds=[wood_volume*data['mechanical'][key]['value']+fixed for key in ('density_low','density_high')]
    report=dict(status='PARTIAL_MASS_SCREEN_NOT_MEASURED',wood_volume_m3=wood_volume,
        wood_density_assumption_kg_m3=[data['mechanical'][key]['value'] for key in ('density_low','density_high')],
        counted_nonwood_kg=fixed,partial_subtotal_kg=bounds,items=rows,
        uncounted=['HF driver and horn','Steel ring, screws, nuts and plates','Amplifier, cables, terminals and fuse holders','Grille, handles, corners, feet, finish, glue, seals and straps'],
        early_A0_10kg_goal_met=False if bounds[0]>10 else None,
        limitations=['Uniform wood density assumptions from project report, not selected supplier certified mass.',
        'Use model volume only for wood; driver and battery bounding-box volumes are not material volumes.',
        'Subtotal excludes listed items and is not finished product weight.'])
    (OUT/'inventory_mass.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'partial_subtotal_kg':bounds,'wood_litres':wood_volume*1000,'excluded_items':len(report['uncounted'])}))
