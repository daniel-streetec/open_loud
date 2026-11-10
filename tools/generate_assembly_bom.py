"""Grouped model-derived assembly BOM; unknown purchasing data remains unknown."""
import csv,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/exports/E07'
def main():
    rows=list(csv.DictReader((OUT/'assembly_bom.csv').open(encoding='utf-8')))
    structure=json.loads((ROOT/'data/assembly_structure.json').read_text(encoding='utf-8'))
    prices=json.loads((ROOT/'data/wiring_procurement.json').read_text(encoding='utf-8'))
    counts=collections.Counter((r['assembly'],r['part'],r['status'],r['purchasing_included']) for r in rows)
    grouped=[]
    for (assembly,part,status,physical),quantity in sorted(counts.items()):
        source=prices['parts'].get(part,{})
        grouped.append(dict(assembly=assembly,part=part,model_quantity=quantity,unit='piece',model_status=status,
            purchasing_included=physical,manufacturer=source.get('manufacturer'),article=source.get('article'),
            gross_unit_EUR=source.get('gross_unit_EUR'),price_date=prices['date'] if source.get('gross_unit_EUR') is not None else None,
            procurement_status=source.get('status','NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA'),source=source.get('source')))
    with (OUT/'assembly_bom_grouped.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(grouped[0]));w.writeheader();w.writerows(grouped)
    text=['# Baugruppen E07','',
        'Modellstruktur und Montagegrenzen; keine vollständige Beschaffungs-/Fertigungsfreigabe. Quelle: data/assembly_structure.json.','',
        '| Teilenummer | Baugruppe | direkte Teile / rekursiv | Funktion |','|---|---|---:|---|']
    for entry in structure['assemblies']:
        path=entry['path'];direct=sum(r['assembly']==path for r in rows);recursive=sum(r['assembly']==path or r['assembly'].startswith(path+'/') for r in rows)
        text.append(f"| {entry['part_number']} | {path.replace('/', ' / ')} | {direct} / {recursive} | {entry['role']} |")
    text+=['','## Mengen nach Unterbaugruppe','',
        'Die Modellmenge beschreibt vorhandene Komponenteninstanzen. Insbesondere Kabel sind hier Konfektionen, keine Meterware; Zuschnitt separat in results/wiring/harness.csv. Nicht modellierte Dichtungen, Kontakte, Clips, Akku und äußere Beschläge fehlen weiterhin. Referenzräume werden nicht eingekauft.','',
        '| Unterbaugruppe | Artikel / Referenz | Modellmenge | Einkaufstatus |','|---|---|---:|---|']
    for r in grouped:
        if r['purchasing_included']!='True':continue
        text.append(f"| {r['assembly']} | {r['part']} | {r['model_quantity']} | {r['procurement_status']} |")
    text+=['','Die enthaltenen historischen Preisbeobachtungen sind nur verknüpfte Quelldaten. Unbekannte Preise, Packmengen und Bezugsquellen wurden nicht ergänzt oder als Nullkosten gerechnet.','',
        'Nicht modelliert: '+', '.join(x['path'] for x in structure['planned_not_modeled'])+'.']
    (OUT/'assemblies.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    assert sum(r['model_quantity'] for r in grouped)==len(rows)
    print(json.dumps({'leaf_instances':len(rows),'grouped_positions':len(grouped),'reference_instances':sum(int(r['quantity']) for r in rows if r['purchasing_included']=='False')}))
if __name__=='__main__':main()
