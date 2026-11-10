"""One-time authoring; central JSON remains authoritative after creation."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'data/parameters.json';d=json.loads(path.read_text(encoding='utf-8'))
assert 'electronics_mount' not in d,'Do not overwrite existing engineering inputs'
def r(v,u,s,status='design_assumption',uncertainty=None):return dict(value=v,unit=u,source=s,status=status,uncertainty=uncertainty)
d['revision']='E06';d['electronics_mount']={
 'tray_origin':r([.040,.372,.182],'m','E06 floor-mounted removable tray, clear of rear left cleat'),
 'tray_size':r([.112,.002,.090],'m','own2mm aluminum5052/5754 plate, grade procurement pending'),
 'support_inset':r(.006,'m','M3 stand-off centres6mm inside tray edges'),
 'spacer_length':r(.010,'m','Wurth970100321 manufacturer datasheet','manufacturer_reference',{'absolute':.0002,'note':'ISO2768m planning; verify tolerance interpretation'}),
 'spacer_af':r(.0055,'m','Wurth970100321 manufacturer datasheet','manufacturer_reference'),
 'screw_diameter':r(.003,'m','M3 nominal thread envelope'),
 'floor_screw_length':r(.016,'m','12mmwood+0.5washer+3.5mm metal-thread engagement'),
 'small_screw_length':r(.006,'m','M3x6 for2mm tray or1.6mm PCB plus0.5mm washer'),
 'washer_thickness':r(.0005,'m','ISO7089 M3 nominal; purchased SKU pending'),
 'washer_od':r(.007,'m','ISO7089 M3 nominal envelope'),
 'washer_id':r(.0032,'m','ISO7089 M3 nominal envelope'),
 'pcb_width':r(.09144,'m','WONDOM AA-JA32173 datasheet p3','manufacturer_reference',{'absolute':.0005}),
 'pcb_depth':r(.0686,'m','WONDOM AA-JA32173 datasheet p3','manufacturer_reference',{'absolute':.0005}),
 'pcb_total_height':r(.020,'m','WONDOM AA-JA32173 datasheet p3; conservative full component envelope','manufacturer_reference',None),
 'pcb_thickness':r(.0016,'m','PCB laminate thickness assumption, not specified by WONDOM'),
 'pcb_pitch_x':r(.0838,'m','WONDOM AA-JA32173 datasheet p3','manufacturer_reference',{'absolute':.0005}),
 'pcb_pitch_z':r(.061,'m','WONDOM AA-JA32173 datasheet p3','manufacturer_reference',{'absolute':.0005}),
 'pcb_hole':r(.0036,'m','WONDOM AA-JA32173 datasheet p3 typical, not minimum','manufacturer_reference',None),
 'tray_pcb_bore':r(.004,'m','allows nominal pattern movement; washer7mm covers bore; verify actual PCB before drilling'),
 'floor_bore':r(.0034,'m','matched drilling through own tray template; wood not threaded'),
 'tray_support_bore':r(.0034,'m','own M3 clearance'),
 'spacer_thread_reference':r('970100321','part_number','https://www.we-online.com/components/products/datasheet/970100321.pdf','manufacturer_reference'),
 'floor_wood_thickness':r(.012,'m','mechanical.wall; duplicated for stack review only'),
}
path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
