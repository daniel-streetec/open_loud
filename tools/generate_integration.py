"""Generate E04 harness lengths, resistance and fit screening from data/."""
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from integration import calculate

def main():
    data=json.loads((ROOT/'data/experiments/e04_rejected_parameters.json').read_text(encoding='utf-8'))
    result=calculate(data)
    result['approval']='REJECTED_EXTERIOR_STUDY_NOT_CURRENT_CAD'
    result['scope']='Keep analytical findings only; harness routes include clashes and are not released' 
    output=ROOT/'results/integration';output.mkdir(parents=True,exist_ok=True)
    (output/'screening.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    p={k:v['value'] for k,v in data['integration'].items()}
    rows=[]
    for kind,r in result['routes'].items():
        current=p['supply_max_scenario'] if kind=='power' else (50/4)**.5 if kind=='lf' else (20/8)**.5
        rows.append({'id':kind,'route_length_m':r['route_length_m'],'cut_length_m':r['cut_length_m'],
                     'conductor_mm2_each':r['conductor_mm2'],'conductors':2,'jacket_OD_m_target':p['power_cable_od' if kind=='power' else 'speaker_cable_od'],
                     'loop_R_60C_ohm':r['loop_resistance_60C_ohm'],'stress_A':current,
                     'drop_at_stress_V':current*r['loop_resistance_60C_ohm'],'loss_at_stress_W':current**2*r['loop_resistance_60C_ohm'],
                     'status':'candidate_not_ampacity_or_voltage_source_certification'})
    with (output/'harness.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    architecture=json.loads((ROOT/'data/electrical_architecture.json').read_text(encoding='utf-8'))
    (output/'electronics_inventory.json').write_text(json.dumps(architecture,indent=2)+'\n',encoding='utf-8')
    print('E04 screening, harness CSV and electronics inventory generated in results/integration/')

if __name__=='__main__':main()
