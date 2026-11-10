"""Voltage-dependent LF limits using the existing validated small-signal solver."""
import csv,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'simulation'))
from model import values,response,limits
def main():
    data=json.loads((R/'data/parameters.json').read_text(encoding='utf-8'))
    case=values(data['concepts']['A0']);driver=values(data['drivers'][data['concepts']['A0']['driver']]);env=values(data['environment']);model=values(data['model'])
    rails=[12,12.8,14.4,18,19.2,21.9];rows=[];summary=[]
    for rail in rails:
        cfg=dict(case,rail=rail)
        for i in range(401):
            f=20*10**(i/400);r=response(f,driver,cfg,env,model);voltage,first,bounds=limits(r,driver,cfg,model)
            rows.append(dict(rail_at_amplifier_V=rail,frequency_Hz=f,max_SLP_ideal_2pi_1m_dB=r['spl_1V']+20*math.log10(voltage),
                voltage_limit_Vrms=voltage,first_limit=first,excursion_peak_mm=1000*r['x_peak']*voltage,
                port_peak_m_s=r['port_peak']*voltage,power_real_W=r['power_real']*voltage**2))
        r=response(50,driver,cfg,env,model);v,first,_=limits(r,driver,cfg,model)
        summary.append(dict(rail_V=rail,SPL_50Hz_ideal_2pi_1m_dB=r['spl_1V']+20*math.log10(v),voltage_limit_Vrms=v,first_limit=first))
    out=R/'results/battery';out.mkdir(parents=True,exist_ok=True)
    with (out/'supply_acoustics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report=dict(status='LF_SIMULATION_NOT_MEASUREMENT',summary=summary,conditions=['A0 fixed34L50Hz; existing losses and reference tests apply.',
        'Voltage is AT amplifier terminals; battery sag, switch and harness loss must be deducted upstream.',
        'Frequency-by-frequency maximum envelope requires DSP limits, not yet implemented. No HF response/polar prediction.',
        '4S LFP below12V is outside board specification; no full-discharge runtime claim.'])
    (out/'supply_acoustics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    colors=['#7c3aed','#2563eb','#0891b2','#16a34a','#d97706','#dc2626'];svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 660"><rect width="1100" height="660" fill="white"/>',
        '<text x="55" y="35" font-size="23" font-family="Arial">OPEN//LOUD A0: voltage-dependent LF maximum envelope</text>',
        '<text x="55" y="59" font-size="13" font-family="Arial">SIMULATION · ideal2pi/1m ·20–200Hz · not measured · DSP limiting not implemented</text>']
    def xy(f,level):return 80+850*math.log10(f/20),545-8*(level-65)
    for spl in range(65,126,10):
        y=xy(20,spl)[1];svg.append(f'<path d="M80 {y}H930" stroke="#cbd5e1"/><text x="38" y="{y+4}" font-size="12">{spl}</text>')
    for freq in (20,30,40,50,63,80,100,160,200):
        x=xy(freq,65)[0];svg.append(f'<path d="M{x} 65V545" stroke="#e2e8f0"/><text x="{x-10}" y="566" font-size="12">{freq}</text>')
    for rail,color in zip(rails,colors):
        pts=' '.join(f'{xy(r["frequency_Hz"],r["max_SLP_ideal_2pi_1m_dB"])[0]:.2f},{xy(r["frequency_Hz"],r["max_SLP_ideal_2pi_1m_dB"])[1]:.2f}' for r in rows if r['rail_at_amplifier_V']==rail)
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>')
        y=100+rails.index(rail)*26;svg.append(f'<text x="950" y="{y}" fill="{color}" font-size="15">{rail} V</text>')
    svg+=['<text x="80" y="615" font-size="13">Voltage quoted at amplifier input. Battery/connector/cable drops are additional. No full two-way frequency-response claim.</text></svg>']
    (out/'supply_acoustics.svg').write_text(''.join(svg),encoding='utf-8')
    print(json.dumps(summary))
if __name__=='__main__':main()
