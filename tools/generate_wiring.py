"""Reproducible low-voltage harness screening; SI geometry and explicit assumptions."""
import csv,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from integration import rounded_route

def calculate(data):
    p={k:v['value'] for k,v in data['wiring'].items()}
    temp=1+p['copper_alpha']*p['temperature_rise_from_20']
    loads=[]
    for v in (15,18,21):
        ac=p['rail_fraction']*v/math.sqrt(2)
        lf=ac*ac/4;hf=min(ac,p['hf_voltage_limit'])**2/8
        loads.append(dict(supply_V=v,lf_W=lf,hf_W=hf,dc_A=((lf+hf)/p['amplifier_efficiency_low']+p['amplifier_idle'])/v))
    branches={}
    for key,current in [('power',p['dc_design_current']),('lf',p['lf_design_current']),('hf',p['hf_design_current'])]:
        samples,length=rounded_route(p[key+'_route'],p['bend_radius'])
        cut=math.ceil((length+p['service_allowance']+p['termination_allowance'])*100)/100
        contact=p['dc_contact_budget'] if key=='power' else p['speaker_contact_budget']
        # Normalize manufacturer's resistance, rather than assume ideal bulk copper.
        rho=p['conductor_resistance']*p['conductor_area']
        tail=2*p['pigtail_length']*rho/p['pigtail_min_area']*temp
        cable=2*cut*p['conductor_resistance']*temp
        resistance=cable+tail+contact
        limit=.03*p['supply_min'] if key=='power' else .05*(4 if key=='lf' else 8)*current
        available=limit/current-tail-contact
        minimum_drop=2*cut*rho*temp/available if available>0 else None
        minimum_heat=2*current**2*rho*temp/p['loop_heat_budget']
        branches[key]=dict(route_length_m=length,cut_length_m=cut,route_points_m=samples,current_A=current,
            conductor_mm2=p['conductor_area'],cable_loop_R60_ohm=cable,pigtail_R60_assumed_ohm=tail,
            contact_budget_ohm=contact,total_loop_R60_ohm=resistance,drop_V=current*resistance,
            drop_limit_V=limit,cable_loss_W=current**2*cable,total_loop_loss_W=current**2*resistance,
            min_area_drop_mm2=minimum_drop,min_area_heat_proxy_mm2=minimum_heat,
            cable_heat_W_per_m=current**2*2*p['conductor_resistance']*temp,
            drop_pass=current*resistance<=limit,
            status='PROVISIONAL: OEM pigtail, contacts, thermal test and exact endpoints unverified')
    stack=.012-p['gland_counterbore_depth']+p['gland_seal_thickness']+p['gland_nut_thickness_reserve']
    return dict(revision='E05',method='electrical analytical screening; CAD route, NOT measured harness',loads=loads,
        branches=branches,gland_thread_margin_m=p['gland_thread_length']-stack,
        gland_diameter_margin_m=p['gland_clamp_max']-p['cable_diameter'],
        total_cut_m=sum(b['cut_length_m'] for b in branches.values()),
        cable_mass_kg=sum(b['cut_length_m'] for b in branches.values())*p['cable_mass'],
        release='NOT_RELEASED_FOR_ENERGIZATION')

def main():
    d=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));r=calculate(d)
    out=ROOT/'results/wiring';out.mkdir(parents=True,exist_ok=True)
    (out/'calculation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    fields=['id','current_A','conductor_mm2','route_length_m','cut_length_m','drop_V','cable_loss_W','status']
    with (out/'harness.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for k,b in r['branches'].items():w.writerow({'id':k,**{f:b[f] for f in fields[1:]}})
    print(json.dumps({k:v for k,v in r.items() if k!='branches'},indent=2))
    assert all(b['drop_pass'] for b in r['branches'].values())
    assert r['gland_thread_margin_m']>0
if __name__=='__main__':main()
