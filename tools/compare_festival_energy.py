"""Capacity and voltage trade study; no inference of old-box music consumption."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    study=json.loads((ROOT/'data/battery_study.json').read_text(encoding='utf-8'))
    d=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'));e={k:v['value'] for k,v in d['energy'].items() if isinstance(v,dict) and 'value' in v}
    a=study['assumptions'];rows=[]
    for o in study['options']:
        for profile in ('normal','loud'):
            low,high=d['energy']['profiles'][profile]['value']
            for path in ('direct','boost'):
                pmin=low/e['eta_high']+e['idle']+e['aux_low'];pmax=high/e['eta_low']+e['idle']+e['aux_high']
                if path=='boost':pmin=pmin/e['boost_eta_high']+e['boost_idle'];pmax=pmax/e['boost_eta_low']+e['boost_idle']
                rows.append(dict(option=o['id'],path=path,profile=profile,nominal_Wh=o['nominal_Wh'],
                    power_low_W=pmin,power_high_W=pmax,runtime_low_h=o['nominal_Wh']*a['usable_fraction_low']/pmax,
                    runtime_high_h=o['nominal_Wh']*a['usable_fraction_high']/pmin,
                    status='unmeasured_energy_scenario; voltage cutoff/thermal/pack limits may reduce this'))
    out=ROOT/'results/battery';out.mkdir(parents=True,exist_ok=True)
    with (out/'runtime_scenarios.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    demands=[]
    for hours in a['music_hours_scenarios']:
        for profile in ('normal','loud'):
            row=next(r for r in rows if r['profile']==profile and r['path']=='boost')
            demands.append(dict(music_h=hours,profile=profile,required_nominal_low_Wh=hours*row['power_low_W']/a['usable_fraction_high'],
                required_nominal_high_Wh=hours*row['power_high_W']/a['usable_fraction_low']))
    report=dict(status='trade_study_not_runtime_guarantee',usb_required=False,festival_reference='Wednesday-Sunday from user, duty unknown',
        demands=demands,nominal_voltage_limited_SPL_delta_12p8_vs18_dB=20*math.log10(12.8/18),
        note='Voltage SPL delta applies only when LF output is rail limited; full system limit may be excursion/thermal/limiter. Direct4S LFP below12V outside JAB supply specification.')
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Festivalversorgung: vorläufiger Vergleich','',
        'Kein USB-Verbrauch. Nutzungsstunden sind Szenarien, keine neue Anforderung. 75-90% nutzbare Energie angenommen; Akkukennlinien, Wandler und reale Lautstärke nicht gemessen. Standby zwischen Musikeinsätzen ausgeschaltet.','',
        '| Option | nominal Wh | Masse kg | Akku brutto EUR | Lieferbeobachtung |','|---|---:|---:|---:|---|']
    for o in study['options']:lines.append(f"| {o['id']} | {o['nominal_Wh']:.1f} | {o.get('mass_kg') or 'offen'} | {o.get('gross_pack_EUR') or 'offen'} | {o['availability']} |")
    lines+=['','Preisstand '+study['date']+'; Lader, Anschlüsse, Halter, Sicherung, Versand und ggf. Wandler zusätzlich. Kein0%-PV-Preis für Lautsprecherbau. Werkzeugakku-Set enthält Lader. Quellen und Einschränkungen in data/battery_study.json.','',
        '| Musikstunden | Profil | benötigte nominale Energie mit angenommenem Wandler, Wh |','|---:|---|---:|']
    for row in demands:lines.append(f"| {row['music_h']} | {row['profile']} | {row['required_nominal_low_Wh']:.0f}-{row['required_nominal_high_Wh']:.0f} |")
    lines+=['','Ein größerer12,8V-Fertigblock ist elektrisch und beim Einkauf einfacher als ein eigener Zellpack, liefert am jetzigen Verstärker direkt aber weniger Spannung. Ein Boost ergänzt Verluste, Ruhestrom, Spitzenstrom und einen zu prüfenden Wärmeweg. Ein6S-LFP-Konzept passt spannungsseitig eher zum18V-Entwurf, hat aber noch keine qualifizierte Endkunden-BOM. Eine einzelne3,2V-Zelle braucht bei gleicher Leistung sehr viel mehr Eingangsstrom und einen Wandler.','',
        '50Ah-Fertigblock passt nicht in den aktuellen Wartungsraum; externe Festivalversorgung oder neue Innenaufteilung erforderlich.18Ah passt nominal als Hülle eher, beweist aber keine mehrtägige Versorgung.100Ah-Erfahrung der alten Box wird nicht auf diesen Entwurf übertragen. Vor Versorgungswechsel Verkabelung und Schutz vollständig neu rechnen.']
    (out/'comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
