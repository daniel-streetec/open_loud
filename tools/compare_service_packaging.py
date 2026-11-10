"""Compare active E08 and independent E09 assembly-space proposal, no CAD mutation."""
import json,sys,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from layout import calculate
if __name__=='__main__':
    base=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    study=json.loads((ROOT/'data/experiments/E09_packaging.json').read_text(encoding='utf-8'))
    trial=copy.deepcopy(base)
    for group in ('battery_mount','electronics_mount'):
        for k,v in study[group].items():
            trial[group][k]=dict(value=v,unit='m',source='data/experiments/E09_packaging.json',status='unbuilt_study',uncertainty=None)
    rows=[]
    for name,data in [('E08_active',base),('E09_study',trial)]:
        c=calculate(data);b={k:v['value'] for k,v in data['battery_mount'].items()};m=c['dimensions']
        x,y,z=b['battery_origin'];w,h,depth=b['battery_size'];tol=study['planning_tolerance_each_face_m']
        rows.append(dict(name=name,battery_excluded_l=c['battery_excluded']*1000,service_partition_z_mm=c['service_z']*1000,
            straight_rear_width_clearance_right_mm=(m['width']-m['wall']-m['rear_cleat_width']-x-w-tol)*1000,
            straight_rear_bottom_clearance_mm=(y-tol-m['wall']-m['rear_cleat_width'])*1000,
            planned_roof_terminal_clearance_mm=(b['bay_top']-m['wall']-y-h-study['terminal_zone_height_m']-tol)*1000,
            planned_tray_partition_gap_mm=(data['electronics_mount']['tray_origin']['value'][2]-c['service_z']-m['wall'])*1000))
    out=ROOT/'results/service';out.mkdir(exist_ok=True)
    report=dict(status='analytical_comparison_not_geometry_release',source_parameters_sha256=hashlib.sha256((ROOT/'data/parameters.json').read_bytes()).hexdigest(),cases=rows,
        limitations=['Clearance tests only rectangular straight-access conditions, not full assembly simulation.',
        'Terminal zone14mm and2mm case-face tolerance are planning assumptions; actual terminal geometry unknown.',
        'E09 needs its own supports, bay right wall, cable routing and mounting rebuild before CAD or manufacturing approval.'])
    (out/'packaging_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
