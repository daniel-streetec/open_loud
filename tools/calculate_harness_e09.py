"""Reproduce E09 routing lengths and resistance screening (not ampacity approval)."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from integration import rounded_route
def calculate(data):
    p={k:r['value'] for k,r in data['harness_e09'].items()}
    power={k:r['value'] for k,r in data['power_system'].items()}
    routes={}
    for name in ('main_plus','main_minus','output','lf','hf'):
        main=name.startswith('main')
        samples,length=rounded_route(p[name+'_route'],p['main_bend' if main else 'speaker_bend'])
        cut=length+p['tail_allowance']+p['service_allowance']
        resistance=cut*p['main_r20' if main else 'speaker_r20']
        routes[name]=dict(points_m=samples,route_length_m=length,cut_length_m=cut,
            area_mm2=4 if main else 1.5,outer_diameter_m=p['main_od' if main else 'speaker_od'],
            conductor_resistance_20C_ohm=resistance,
            conductor_resistance_60C_ohm=resistance*(1+p['temperature_delta']*p['copper_alpha']))
    loop=sum(routes[n]['conductor_resistance_60C_ohm'] for n in ('main_plus','main_minus'))+p['contact_budget']
    return dict(revision='E09',status='analytical_screening_not_installation_release',routes=routes,
        main_at_12A=dict(loop_resistance_60C_ohm=loop,drop_V=12*loop,loss_W=144*loop),
        limitations=['Cut lengths include unlocated 100mm service allowance and 160mm terminal tails; physical dressing pending.',
        'Fuse holder pigtails, amplifier supplied pigtails and contact resistance require measurement.',
        'No ampacity certification follows from voltage-drop calculation. Terminal locations require supplier verification.'])
if __name__=='__main__':
    result=calculate(json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8')))
    out=ROOT/'results/power/E09';out.mkdir(parents=True,exist_ok=True)
    (out/'harness.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:round(v['cut_length_m'],3) for k,v in result['routes'].items()}))
