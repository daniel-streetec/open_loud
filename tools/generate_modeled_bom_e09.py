"""Actual CAD inventory joined to dated observations; not a complete shopping list."""
import json,csv,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=json.loads((ROOT/'hardware/mechanical/exports/E09/inventory_mass.json').read_text(encoding='utf-8'))
    offers=json.loads((ROOT/'data/procurement_E08.json').read_text(encoding='utf-8'))
    old=json.loads((ROOT/'data/wiring_procurement.json').read_text(encoding='utf-8'))
    mapping={'EREMIT_12V50Ah_MICRO_GEN7_BASIS':0,'VICTRON_ORI122410110':1,'EREMIT_12V5A_LFP_CHARGER':2,'AMASS_XT60E_F':3}
    groups=collections.defaultdict(list);excluded=[]
    for item in inventory['items']:
        n=item['component']
        if 'RESERVE' in n or n.startswith('E08_REF_'):excluded.append(n);continue
        groups[item['part']].append(item)
    rows=[]
    for part,items in sorted(groups.items()):
        offer=offers['items'][mapping[part]] if part in mapping else None
        previous=old['parts'].get(part,{})
        row=dict(id=part,modeled_quantity=len(items),unit='piece',manufacturer=offer['manufacturer'] if offer else previous.get('manufacturer'),
            mpn=offer['mpn'] if offer else previous.get('article'),gross_unit_EUR=offer['gross_price_EUR'] if offer else previous.get('gross_unit_EUR'),
            price_date=offer['price_date'] if offer else old['date'] if previous else None,
            source=offer['consumer_retailer_url'] if offer else previous.get('source'),
            approval=offer['approval'] if offer else previous.get('status','unqualified_model_reference'),
            components=[i['component'] for i in items],assemblies=sorted(set(i['assembly_path'].split('+')[0] for i in items)))
        if part.startswith(('WIRE_','CORDIAL_')):
            row['unit']='modeled_route_not_purchase_length';row['gross_unit_EUR']=None
        rows.append(row)
    out=ROOT/'results/power/E09'
    result=dict(revision='E09',scope='Modeled inventory only, not complete procurement BOM; use harness.json for wire lengths',
        parts=rows,excluded_nonphysical=excluded,
        missing=['WAGO terminals/carriers','Cable strain reliefs and clips','Strap anchors','Reverse protector and remote switch','Mating charge plug and insulation','Fuse elements, extra pigtails and crimp terminals','Grille, handles, corners, feet','Glue, seals, coating and thread locking'])
    (out/'modeled_bom.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    fields=['id','modeled_quantity','unit','manufacturer','mpn','gross_unit_EUR','price_date','source','approval']
    with (out/'modeled_bom.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    print(json.dumps({'modeled_line_items':len(rows),'unknown_unit_prices':sum(r['gross_unit_EUR'] is None for r in rows),'scope':'not a complete shopping list'}))
if __name__=='__main__':main()
