"""Recorded E08 packaging refinement; safe before the electronics CAD stage."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/parameters.json'
d=json.loads(p.read_text(encoding='utf-8'))
d['electronics_mount']['tray_size']['value']=[.152,.002,.126]
d['electronics_mount']['tray_origin']['value']=[.040,.352,.198]
d['harness_e08']['main_minus_route']['value']=[[.260,.204,.315],[.260,.390,.315],[.260,.390,.245]]
d['harness_e08']['main_minus_route']['source']='E08 straight passage through both roof glands; battery terminal tail remains provisional until terminal drawing is verified'
d['harness_e08']['hf_route']['value']=[[.050,.400,.305],[.170,.400,.305],[.170,.500,.305],[.170,.500,.145],[.240,.470,.145]]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cad=ROOT/'hardware/mechanical/add_electronics_e08.py'
s=cad.read_text(encoding='utf-8').replace('152x90x2','152x126x2').replace('OWN_AL_TRAY_152_90_2','OWN_AL_TRAY_152_126_2')
cad.write_text(s,encoding='utf-8')
