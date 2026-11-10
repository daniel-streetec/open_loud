"""Standalone scientific LF plots; actual import/render execution checked."""
import json,csv,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.tools/python'))
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='OPEN_LOUD_E09_LF'
import matplotlib.pyplot as plt
import numpy as np
if __name__=='__main__':
    out=ROOT/'results/dsp/E09';report=json.loads((out/'draft.json').read_text(encoding='utf-8'))
    params=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'))
    rows=list(csv.DictReader((out/'LF_protection_sweep.csv').open(encoding='utf-8')))
    fig,axes=plt.subplots(2,2,figsize=(11.7,8.3),layout='constrained')
    fields=[('SPL_dB','SPL [dB re20µPa, 1m/2π]'),('excursion_peak_mm','Membranhub, Spitze [mm]'),('port_peak_m_s','Portgeschwindigkeit, Spitze [m/s]'),('voltage_Vrms','Lautsprecherspannung [Vrms]')]
    for cutoff in (35,40,45,50):
        curve=[r for r in rows if int(r['highpass_Hz'])==cutoff];f=[float(r['frequency_Hz']) for r in curve]
        for ax,(key,label) in zip(axes.flat,fields):
            ax.semilogx(f,[float(r[key]) for r in curve],label=f'HP {cutoff}Hz',linewidth=2 if cutoff==40 else 1)
            ax.set(xlim=(10,400),xlabel='Frequenz [Hz]',ylabel=label);ax.grid(True,which='both',alpha=.25)
    axes[0,1].axhline(report['comparison'][0]['Xmax_reference_mm'],color='black',linestyle='--',label='Xmax-Referenz, kein THD-Nachweis')
    axes[1,0].axhline(report['comparison'][0]['port_limit_reference_m_s'],color='black',linestyle='--',label='Planungsgrenze, kein Geräuschnachweis')
    for ax in axes.flat:
        ax.axvspan(250,400,color='grey',alpha=.12);ax.legend(fontsize=7)
    vb=params['concepts']['A0']['Vb']['value']*1000;fb=params['concepts']['A0']['Fb']['value']
    fig.suptitle(f'OPEN//LOUD E09 – LF-Näherung, {vb:g}L / Fb{fb:g}Hz / {report["lf_target_Vrms"]:g}Vrms\nButterworth4-HP + LR4-LP2,5kHz; keine Messung, oberhalb250Hz begrenzte Aussage',fontsize=12)
    fig.savefig(out/'LF_protection.png',dpi=160,metadata={'Software':'OPEN_LOUD matplotlib'})
    fig.savefig(out/'LF_protection.svg',metadata={'Date':None,'Creator':'OPEN_LOUD own LF model'})
    fig.savefig(out/'LF_protection.pdf',metadata={'CreationDate':None,'ModDate':None,'Creator':'OPEN_LOUD own LF model'})
    plt.close(fig)
    manifest=dict(matplotlib=matplotlib.__version__,numpy=np.__version__,source_csv_sha256=hashlib.sha256((out/'LF_protection_sweep.csv').read_bytes()).hexdigest(),
        files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [out/'LF_protection.png',out/'LF_protection.svg',out/'LF_protection.pdf']})
    (out/'plot_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest))
