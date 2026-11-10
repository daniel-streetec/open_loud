"""Reproducible LF protection sweep and generic draft biquad coefficients."""
import json,sys,math,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'simulation'))
from filters import lr4,butterworth4_highpass,cascade
from model import response,values,db,crossing
if __name__=='__main__':
    d=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'))
    spec=json.loads((ROOT/'data/experiments/E09_dsp_draft.json').read_text(encoding='utf-8'));p=values(d['dsp_draft'])
    driver=values(d['drivers']['10FE200-4']);case=values(d['concepts']['A0']);env=values(d['environment']);model=values(d['model'])
    fs=p['sample_rate'];xo=p['crossover'];lp=lr4('lp',xo,fs);summary=[];rows=[]
    voltage=d['power_system']['lf_limit']['value']
    frequencies=[p['frequency_low']*(p['frequency_high']/p['frequency_low'])**(i/(p['points']-1)) for i in range(p['points'])]
    for cutoff in p['highpass_candidates']:
        sections=butterworth4_highpass(cutoff,fs)+lp;local=[]
        for f in frequencies:
            r=response(f,driver,case,env,model);gain=abs(cascade(sections,f,fs));v=voltage*gain
            row=dict(highpass_Hz=cutoff,frequency_Hz=f,voltage_Vrms=v,excursion_peak_mm=r['x_peak']*v*1000,port_peak_m_s=r['port_peak']*v,
                copper_W=r['power_copper']*v*v,SPL_dB=r['spl_1V']+db(v))
            rows.append(row);local.append(row)
        x=max(local,key=lambda r:r['excursion_peak_mm']);port=max(local,key=lambda r:r['port_peak_m_s'])
        band=[r['SPL_dB'] for r in local if model['norm_low']<=r['frequency_Hz']<=model['norm_high']];reference=sum(band)/len(band)
        f6=crossing(frequencies,[r['SPL_dB']-reference for r in local],-6,model['norm_low'])
        summary.append(dict(highpass_Hz=cutoff,max_excursion_peak_mm=x['excursion_peak_mm'],at_frequency_Hz=x['frequency_Hz'],
            Xmax_reference_mm=driver['Xmax']*1000,max_port_peak_m_s=port['port_peak_m_s'],port_limit_reference_m_s=model['port_peak_limit'],
            attenuation_50Hz_dB=db(cascade(sections,50,fs)),F6_Hz=f6,reference_band_Hz=[model['norm_low'],model['norm_high']],within_nominal_excursion=x['excursion_peak_mm']<=driver['Xmax']*1000))
    chosen=butterworth4_highpass(p['selected_highpass'],fs)+lp
    report=dict(status='OFFLINE_APPROXIMATION_NOT_MEASUREMENT_OR_FIRMWARE',sample_rate_assumed_Hz=fs,lf_target_Vrms=voltage,
        comparison=summary,LF_generic_biquads=chosen,HF_generic_biquads=lr4('hp',xo,fs),
        coefficient_convention='a0=1; y=b0*x+b1*x1+b2*x2-a1*y1-a2*y2',limitations=spec['limitations']+['No multitone/crest-factor proof, parameter tolerance or nonlinear compression included.','No combined LF/HF acoustic frequency response claimed.'])
    out=ROOT/'results/dsp/E09';out.mkdir(parents=True,exist_ok=True)
    (out/'draft.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (out/'LF_protection_sweep.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(summary,indent=2))
