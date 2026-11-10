"""E09 impedance-bound supply budget including warm wiring and source sag."""
import json,sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'simulation'));from model import constant_power_pack
sys.path.insert(0,str(ROOT/'tools'));from calculate_harness_e09 import calculate as harness_calculate
def calculate(data):
    p={k:r['value'] for k,r in data['power_system'].items()};h={k:r['value'] for k,r in data['harness_e09'].items()}
    e={k:r['value'] for k,r in data['energy'].items() if isinstance(r,dict) and 'value' in r};harness=harness_calculate(data)
    output_r=2*harness['routes']['output']['conductor_resistance_60C_ohm']+h['speaker_contact_budget']
    main_r=harness['main_at_12A']['loop_resistance_60C_ohm']+p['planned_reverse_resistance']
    nominal_audio=p['lf_limit']**2/4+p['hf_limit']**2/8
    lf_re=data['drivers']['10FE200-4']['Re']['value']*p['lf_re_factor_low']
    bounded_audio=p['lf_limit']**2/lf_re+p['hf_limit']**2/p['hf_min_impedance']
    def chain(audio,battery,amp_eta,dc_eta,vs):
        amp=audio/amp_eta+p['amplifier_idle']
        solved=constant_power_pack(vs,output_r,amp);assert solved is not None
        board,iout=solved;pout=vs*iout
        pin=pout/dc_eta+battery*p['converter_idle_current_max']
        source=constant_power_pack(battery,main_r,pin);assert source is not None
        vin,ibatt=source
        return dict(mean_audio_W=audio,amplifier_input_W=amp,board_terminal_V=board,converter_output_W=pout,
            converter_output_A=iout,output_wire_loss_W=iout*iout*output_r,converter_input_V=vin,
            battery_A=ibatt,battery_W=battery*ibatt,input_wire_and_planned_protector_loss_W=ibatt*ibatt*main_r,
            estimated_converter_heat_W=pin-pout)
    cases=[dict(battery_terminal_V=v,**chain(bounded_audio,v,p['amplifier_efficiency_low'],p['converter_efficiency_low'],p['converter_output']-.2)) for v in (p['battery_cutoff'],p['battery_nominal'],p['battery_full'])]
    cap=p['converter_output']*p['converter_output_current'];worst=max(cases,key=lambda c:c['converter_output_W'])
    assert worst['converter_output_W']<cap
    assert max(c['battery_A'] for c in cases)<p['main_design_current']
    assert min(c['converter_input_V'] for c in cases)>8
    nominal=p['battery_nominal']*p['battery_capacity'];runtime=[]
    for name in ('background','normal','loud','near_max'):
        low,high=data['energy']['profiles'][name]['value']
        good=chain(low,p['battery_nominal'],e['eta_high'],p['converter_efficiency_high'],p['converter_output'])
        poor=chain(high,p['battery_nominal'],p['amplifier_efficiency_low'],p['converter_efficiency_low'],p['converter_output']-.2)
        runtime.append(dict(profile=name,mean_audio_range_W=[low,high],runtime_h=[nominal*p['usable_fraction_low']/poor['battery_W'],nominal*p['usable_fraction_high']/good['battery_W']]))
    return dict(revision='E09',status='SOURCE_BASED_PLANNING_NOT_MEASUREMENT',nominal_load_sine_audio_W=nominal_audio,
        conservative_impedance_bound_audio_W=bounded_audio,LF_resistance_sensitivity_ohm=lf_re,HF_minimum_impedance_ohm=p['hf_min_impedance'],
        input_warm_loop_including_planned_protector_ohm=main_r,output_warm_loop_ohm=output_r,
        scenarios=cases,converter_capacity_W=cap,converter_capacity_margin_percent=100*(1-worst['converter_output_W']/cap),
        nominal_battery_Wh=nominal,runtimes=runtime,
        limitations=['LF Re multiplied by0.9 is a sensitivity assumption, not certified tolerance or measured minimum impedance.',
        'Amplifier efficiency65percent, converter80percent, idle current and contact budgets are conservative planning inputs.',
        'Reverse module is a planned load allowance, not installed or fully qualified. Pigtail/contact resistance needs measurement.',
        '20V setting, channel gain and10.5/10Vrms DSP targets must be calibrated; no DSP image deployed.',
        'Thermal path, pack/BMS fault coordination, cold-charge protection and actual audio duty cycle remain unproven.'])
if __name__=='__main__':
    data=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'));result=calculate(data)
    out=ROOT/'results/power/E09';out.mkdir(parents=True,exist_ok=True)
    (out/'supply_budget.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('nominal_load_sine_audio_W','conservative_impedance_bound_audio_W','converter_capacity_margin_percent')}))
