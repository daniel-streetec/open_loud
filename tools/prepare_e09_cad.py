"""Prepare a separate E09 candidate from checked E08 sources; E08 stays active/frozen."""
import json,copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'hardware/mechanical'
sys.path.insert(0,str(M));import layout
base=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
assert base['revision']=='E08','Review baseline before preparing E09'
study=json.loads((ROOT/'data/experiments/E09_packaging.json').read_text(encoding='utf-8'));d=copy.deepcopy(base)
d['revision']='E09'
d['date']='2026-11-10'
d['mechanical']['hf_mass']=dict(value=.8,unit='kg',source='https://bcspeakers.com/en/products/hf-driver/1-0/8/de10',status='manufacturer_nominal',uncertainty=None)
d['mechanical']['horn_mass']=dict(value=.17,unit='kg',source='https://www.bcspeakers.com/en/products/horn/1/0/ME10V3/',status='manufacturer_nominal',uncertainty=None)
d['dsp_draft']=json.loads((ROOT/'data/experiments/E09_dsp_draft.json').read_text(encoding='utf-8'))['parameters']
def rec(v,source='data/experiments/E09_packaging.json',unit='m'):
    return dict(value=v,unit=unit,source=source,status='design_candidate',uncertainty=None)
for group in ('battery_mount','electronics_mount'):
    for k,v in study[group].items():d[group][k]=rec(v)
d['battery_mount']['power_feed_xz']=rec(study['battery_roof_feed_xz'])
d['battery_mount']['lf_floor_feed_xz']=rec(study['LF_floor_feed_xz'])
d['battery_mount']['support_runner_z']=rec([.140,.270])
d['battery_mount']['support_runner_depth']=rec(.020,'own two25mm-high cross runners with3mm pad')
c=layout.calculate(d);d['battery_mount']['converter_origin']['value']=[.200,.400,c['service_z']+.012]
cm=d['connection_mounts_e08']
for key in ('bracket_vertical_origin','bracket_foot_origin','socket_body_origin','socket_flange_origin'):
    a=cm[key]['value'];cm[key]=rec([a[0]-.008,a[1]+.020,a[2]])
cm['socket_hole_x']=rec([.2825,.3075]);cm['socket_center_y']=rec(.219)
cm['roof_hole_x']=rec([.284,.309])
cm['bracket_vertical_origin']['value'][0]=.280
cm['bracket_vertical_size']['value'][0]=.034
cm['bracket_foot_origin']['value'][0]=.280
cm['socket_body_origin']['value'][0]=.28745
cm['socket_flange_origin']['value'][0]=.280
cm['socket_hole_x']=rec([.2845,.3095])
cm['roof_hole_x']=rec([.285,.309])
cm['roof_hole_z']=rec(.296,'own E09 screw-head clearance from XT60 housing')
cm['bracket_foot_origin']['value'][2]=.288
cm['bracket_foot_size']=rec([.034,.002,.0299],'own E09 foot extended10mm for screw-head access;34mm width clears moving battery envelope')
d['connection_mounts_e09']=d.pop('connection_mounts_e08')
h=copy.deepcopy(d.pop('harness_e08'))
h['main_plus_route']=rec([[.295,.226,.250],[.295,.390,.250],[.232,.390,.250]])
h['main_minus_route']=rec([[.295,.226,.275],[.295,.390,.275],[.260,.390,.275]])
h['output_route']=rec([[.286,.405,.270],[.286,.405,.310],[.114,.405,.310],[.114,.405,.245]])
h['lf_route']=rec([[.050,.420,.273],[.255,.420,.285],[.255,.285,.285],[.255,.285,.140],[.235,.280,.110]])
h['hf_route']=rec([[.194,.390,.273],[.170,.390,.305],[.170,.500,.305],[.170,.500,.145],[.240,.470,.145]])
h['tail_allowance']=rec(.300,'two150mm tails; actual terminals still to verify')
d['harness_e09']=h
d['orion_mount_e09']=d.pop('orion_mount_e08')
d['power_system']['lf_limit']=rec(10.5,'E09 conservative impedance/temperature sensitivity and100W converter margin; not deployed',unit='V_rms')
d['power_system']['hf_min_impedance']=rec(6.3,'https://bcspeakers.com/en/products/hf-driver/1-0/8/de10',unit='ohm')
d['power_system']['lf_re_factor_low']=rec(.9,'10percent below nominal Re sensitivity, not certified production or temperature tolerance',unit='1')
d['power_system']['planned_reverse_resistance']=rec(.003,'Pololu5389 planning2x1.5mOhm; module not installed, hot resistance not guaranteed',unit='ohm')
p=ROOT/'data/experiments/E09_parameters.json';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def emit(name,source):
    source=source.replace('E08','E09').replace('_e08','_e09').replace('data/parameters.json','data/experiments/E09_parameters.json')
    source='\n'.join(line.rstrip() for line in source.splitlines()).rstrip()+'\n'
    (M/name).write_text(source,encoding='utf-8')
for old,new in [('build_case_e08.py','build_case_e09.py'),('assemble_rear_e08.py','assemble_rear_e09.py'),('add_fasteners_e08.py','add_fasteners_e09.py'),('refine_orion_mount_e08.py','refine_orion_mount_e09.py')]:emit(new,(M/old).read_text(encoding='utf-8'))
s=(M/'add_electronics_e08.py').read_text(encoding='utf-8').replace('152x126x2','180x102x2').replace('OWN_AL_TRAY_152_126_2','OWN_AL_TRAY_180_102_2');emit('add_electronics_e09.py',s)
s=(M/'add_power_e08.py').read_text(encoding='utf-8')
s=s.replace("width=m['width']-wall-left","width=p['bay_right']-left")
s=s.replace("    F.subtract(roof,F.box([m['width']-wall-cw,top-wall-.001,rear-cd],[cw+.001,wall+.002,cd+.001]))", "    # New bay ends before the fixed right rear cleat; no roof corner notch needed.")
s=s.replace("    origin=p['battery_origin'];size=p['battery_size']", "    rightwall=F.box([p['bay_right']-wall,wall,front+wall],[wall,top-2*wall,rear-front-wall])\n    F.subtract(rightwall,F.box([p['bay_right']-wall-.001,wall-.001,rear-cd],[wall+.002,cw+.001,cd+.001]))\n    F.component('E08_Battery_right_wall',[rightwall],'OWN_PLY12_BATTERY_RIGHT')\n    origin=p['battery_origin'];size=p['battery_size']")
start=s.index('    pad=F.component(');end=s.index('    zone=F.component(',start)
s=s[:start]+'''    padbody=F.box([origin[0],origin[1]-p['pad'],origin[2]],[size[0],p['pad'],size[2]])
    for axis_x in (.175,.245):F.subtract(padbody,F.box([axis_x-.0125,origin[1]-p['pad']-.001,origin[2]-.002],[.025,.0035,size[2]+.004]))
    F.component('E08_Battery_bottom_pad',[padbody],'OWN_BATTERY_PAD_3MM','foam_with_strap_reliefs_compression_unverified')
    for i,z in enumerate(p['support_runner_z']):
        F.component(f'E08_Battery_support_runner_{i}',[F.box([origin[0],wall,z],[size[0],origin[1]-p['pad']-wall,p['support_runner_depth']])],'OWN_WOOD_BATTERY_RUNNER_25_20_130','support_geometry_glue_and_retention_test_pending')
'''+s[end:]
s=s.replace("enumerate((.190,.280))","enumerate((.175,.245))")
s=s.replace("F.box([x-.016,.135,origin[2]-.012],[.032,.025,.008])","F.box([x-.016,.120,origin[2]+size[2]+.003],[.032,.025,.008])")
s=s.replace("[.220,.182,.307]","[.280,.182,.270]").replace("[.265,.155,.307]","[.280,.150,.270]").replace("[.200,.350,.270]","[.235,.350,.230]")
s=s.replace("[.275,m['service_floor_y'],.275]","[p['lf_floor_feed_xz'][0],m['service_floor_y'],p['lf_floor_feed_xz'][1]]")
s=s.replace("for axis_x in (.232,.260):","for slot,(axis_x,axis_z) in enumerate(p['power_feed_xz']):")
s=s.replace("tag+'_'+str(round(axis_x*1000)),cp,'y',[axis_x,y,.315]","tag+'_'+str(slot),cp,'y',[axis_x,y,axis_z]")
emit('add_power_e09.py',s)
s=(M/'add_charge_bracket_e08.py').read_text(encoding='utf-8')
for a,b in [('.208','.228'),('.2055','.2255'),('.2025','.2225'),('.2205','.2405'),('.2195','.2395'),('.2239','.2439'),("('top',.220)","('top',.240)")]:s=s.replace(a,b)
s=s.replace('OWN_AL2_XT60_INTERNAL_BRACKET','OWN_AL2_XT60_INTERNAL_BRACKET_E09');emit('add_charge_bracket_e09.py',s)
s=(M/'add_harness_e08.py').read_text(encoding='utf-8')
start=s.index('    # Move the reserved F3');end=s.index('    for name,route',start);s=s[:start]+s[end:];emit('add_harness_e09.py',s)
for old,new in [('verify_power_e08.py','verify_power_e09.py'),('view_power_e08.py','view_power_e09.py'),('check_exports_e08.py','check_exports_e09.py'),('inventory_mass_e08.py','inventory_mass_e09.py'),('check_battery_service_e08.py','check_battery_service_e09.py')]:
    s=(M/old).read_text(encoding='utf-8')
    if old.startswith('inventory_mass'):
        s=s.replace("cp.name.startswith('Rear_cleat_')","cp.name.startswith(('Rear_cleat_','E08_Battery_support_runner_')) or cp.name=='E08_Battery_right_wall'")
    if old.startswith('check_battery_service'):
        s=s.replace('import adsk.core,adsk.fusion,json','import adsk.core,adsk.fusion,json,re')
        s=s.replace('        if not o.component.bRepBodies.count or o==battery:continue',"        if not o.component.bRepBodies.count or o==battery:continue\n        if name=='Rear_removable' or re.fullmatch(r'E05_Rear_[0-9]+_(washer|M5x40)',name):continue\n        if name.startswith(('E08_Battery_strap_','E08_Battery_buckle_')) or name=='E08_Battery_bottom_pad':continue")
        s=s.replace('range(0,201,5)','range(0,226,5)')
    emit(new,s)
for old,new in [('calculate_harness_e08.py','calculate_harness_e09.py')]:
    s=(ROOT/'tools'/old).read_text(encoding='utf-8').replace('E08','E09').replace('harness_e08','harness_e09').replace('data/parameters.json','data/experiments/E09_parameters.json').replace('board_voltage_range_V','converter_terminal_voltage_range_V')
    (ROOT/'tools'/new).write_text(s,encoding='utf-8')
print(json.dumps({'candidate':'E09','service_z_mm':c['service_z']*1000,'active_E08_unchanged':True}))
