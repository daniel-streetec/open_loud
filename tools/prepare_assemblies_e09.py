"""Extend verified E07 maintenance boundaries for E09 supply hardware."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'data/assembly_structure.json').read_text(encoding='utf-8'));s['revision']='E09'
s['planned_not_modeled']=[e for e in s['planned_not_modeled'] if not e['path'].startswith('BG60_')]
extra=[('BG40_Elektronikmodul/BG43_Geregelte_Versorgung','OL-430','Orion supply with removable mounting hardware and output fuse holder'),
 ('BG60_Akkuversorgung','OL-600','battery supply and independent internal charging branch; electrical qualification incomplete'),
 ('BG60_Akkuversorgung/BG61_Akku_BMS','OL-610','factory battery with integral BMS, no DIY cell assembly'),
 ('BG60_Akkuversorgung/BG62_Akkuhalterung','OL-620','pads and straps, anchors incomplete; wooden sealed bay remains cabinet'),
 ('BG60_Akkuversorgung/BG63_DC_Schutz','OL-630','main and charge fuse holders; reverse protector and switch still missing'),
 ('BG60_Akkuversorgung/BG64_Ladeanschluss','OL-640','internal XT60 socket, own bracket and through-bolt counterparts'),
 ('BG80_Externes_Ladegeraet','OL-800','external mains accessory, excluded from carried mass')]
s['assemblies'] += [dict(path=a,part_number=b,role=c) for a,b,c in extra]
for entry in s['assemblies']:
    if entry['path']=='BG40_Elektronikmodul':entry['role']='Electronics service assembly; BG41+BG42 tray removes separately, BG43 converter has its own four mount screws and stays on partition during tray removal'
for r in s['rules']:
    r['pattern']=r['pattern'].replace('removable_tray_112x90x2','removable_tray_[0-9]+x[0-9]+x2')
rules=[
 ('E09_Battery_(front_wall|left_wall|right_wall|roof|support_runner_[0-9]+)','BG10_Gehaeuse/BG11_Holzstruktur'),
 ('E09_(LF_feed|HF_feed|BAT_[0-9]+|ELEC_[0-9]+)_(gland|locknut)','BG10_Gehaeuse/BG14_Kabeldurchfuehrungen'),
 ('E09_ROUTE_.*','BG50_Kabelbaum'),
 ('E09_Battery_EREMIT_50Ah_BMS','BG60_Akkuversorgung/BG61_Akku_BMS'),
 ('E09_Battery_(bottom_pad|strap_[0-9]+|buckle_[0-9]+)','BG60_Akkuversorgung/BG62_Akkuhalterung'),
 ('E09_F[12]_.*_holder','BG60_Akkuversorgung/BG63_DC_Schutz'),
 ('E09_(Charge_.*|XT60E_F_charge_socket)','BG60_Akkuversorgung/BG64_Ladeanschluss'),
 ('E09_(Orion_.*|F3_output5A_holder)','BG40_Elektronikmodul/BG43_Geregelte_Versorgung'),
 ('E09_External_.*','BG80_Externes_Ladegeraet'),
 ('E09_REF_.*','BG90_Referenzraeume')]
s['rules'] += [dict(pattern='^'+a+'$',path=b) for a,b in rules]
(ROOT/'data/assembly_structure_E09.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
source=(ROOT/'hardware/mechanical/organize_assemblies_e07.py').read_text(encoding='utf-8')
source=source.replace("exports/E07","exports/E09").replace('OPEN_LOUD_A0_E07_Assemblies','OPEN_LOUD_A0_E09_PowerSystem').replace('data/assembly_structure.json','data/assembly_structure_E09.json').replace("'E07'","'E09'")
(ROOT/'hardware/mechanical/organize_assemblies_e09.py').write_text(source,encoding='utf-8')
