"""Join CAD inventory, cable cut list and verified procurement observations."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
    observations=json.loads((R/'data/wiring_procurement.json').read_text(encoding='utf-8'))
    calc=json.loads((R/'results/wiring/calculation.json').read_text(encoding='utf-8'))
    build=json.loads((R/'hardware/mechanical/exports/E05/build.json').read_text(encoding='utf-8'))
    counts={k:v for k,v in build['modeled_inventory'].items() if not k.startswith('Cordial_')}
    counts.update(Cordial_CLS215=math.ceil(calc['total_cut_m']),WAGO_221_2411=6,WAGO_221_2522=3,
        fuse_and_holder=1,DC_switch=1,UVLO_reverse_polarity=1,battery_adapter=1,
        driver_terminals_LF=2,driver_terminals_HF=2,cable_clamps=8,wire_labels=6,panel_seals=2,OEM_JAB_cable_set=1)
    rows=[]
    for key,qty in counts.items():
        entry=observations.get('parts',{}).get(key,{})
        rows.append(dict(id=key,quantity=qty,**entry))
    out=R/'results/wiring'
    (out/'bom.json').write_text(json.dumps(dict(date=observations['date'],scope='E05 additions only; NOT complete speaker BOM',parts=rows),indent=2)+'\n',encoding='utf-8')
    fields=['id','quantity','manufacturer','article','gross_unit_EUR','availability','source','status']
    with (out/'bom.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    known=sum(row['quantity']*row.get('gross_unit_EUR',0) for row in rows if row.get('gross_unit_EUR') is not None)
    print(json.dumps({'known_partial_material_EUR':round(known,2),'unknown_cost_items':[x['id'] for x in rows if x.get('gross_unit_EUR') is None],'note':'Not total cost; shipping and pack rounding separate.'}))
if __name__=='__main__':main()
