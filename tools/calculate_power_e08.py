"""E08 selected supply: loads, warm harness loss, energy and compatibility."""
import json,csv,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def calculate(data):
    p={k:r['value'] for k,r in data['power_system'].items()};e={k:r['value'] for k,r in data['energy'].items() if isinstance(r,dict) and 'value' in r}
    nominal=p['battery_nominal']*p['battery_capacity'];audio=p['lf_limit']**2/4+p['hf_limit']**2/8
    load=audio/p['amplifier_efficiency_low']+p['amplifier_idle'];maxout=p['converter_output']*p['converter_output_current']
    rows=[]
    for voltage in (p['battery_cutoff'],p['battery_nominal'],p['battery_full']):
        watts=load/p['converter_efficiency_low']+voltage*p['converter_idle_current_max']
        rows.append(dict(battery_terminal_V=voltage,amplifier_input_W=load,converter_output_A=load/p['converter_output'],battery_A=watts/voltage))
    runtimes=[]
    for name in ('background','normal','loud','near_max'):
        low,high=data['energy']['profiles'][name]['value']
        lo=(low/e['eta_high']+p['amplifier_idle'])/p['converter_efficiency_high']+p['battery_nominal']*p['converter_idle_current_max']
        hi=(high/p['amplifier_efficiency_low']+p['amplifier_idle'])/p['converter_efficiency_low']+p['battery_nominal']*p['converter_idle_current_max']
        runtimes.append(dict(profile=name,mean_audio_low_W=low,mean_audio_high_W=high,pack_low_W=lo,pack_high_W=hi,
            runtime_low_h=nominal*p['usable_fraction_low']/hi,runtime_high_h=nominal*p['usable_fraction_high']/lo))
    assert load<maxout and max(r['battery_A'] for r in rows)<p['main_design_current']
    return dict(status='DESIGN_CALCULATION_NOT_MEASUREMENT',battery_nominal_Wh=nominal,usable_Wh=[nominal*p['usable_fraction_low'],nominal*p['usable_fraction_high']],
        limited_sine_audio_W=audio,amplifier_worst_case_input_W=load,converter_conservative_output_capacity_W=maxout,
        converter_capacity_margin_percent=(1-load/maxout)*100,worst_converter_heat_W=load*(1/p['converter_efficiency_low']-1)+p['battery_nominal']*p['converter_idle_current_max'],
        scenarios=rows,runtimes=runtimes,charger_ideal_CC_h=p['battery_capacity']/p['charger_current'],
        recharge_note='10h ideal full-depth CC, CV tail adds time; cold-charge limits and actual charger termination verify',
        board_voltage_range_V=[p['converter_output']-.2,p['converter_output']+.2],
        prerequisites=['Set converter20.0V unloaded, then test under load BEFORE amplifier connection.',
            'DSP voltage limits are targets, not deployed/calibrated firmware. Do not enable HF before bench calibration.',
            'Converter UVLO7V does not protect4S LFP; rely on qualified battery BMS, verify BMS operation at intended terminals.',
            'Fuse values pending inrush/temperature/interrupt coordination. Unknown pack prospective short current is not invented.',
            'No USB load; festival days do not imply continuous music hours.'])
def main():
    d=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));r=calculate(d);out=ROOT/'results/power/E08';out.mkdir(parents=True,exist_ok=True)
    (out/'budget.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    with (out/'runtime.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(r['runtimes'][0]));w.writeheader();w.writerows(r['runtimes'])
    print(json.dumps({k:v for k,v in r.items() if k not in ('prerequisites','runtimes','scenarios')},indent=2))
if __name__=='__main__':main()
