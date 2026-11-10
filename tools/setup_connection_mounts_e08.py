"""Versioned own bracket dimensions; no guessed vendor mounting hole is released."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/parameters.json'
d=json.loads(p.read_text(encoding='utf-8'))
def record(value,unit,source='OPEN_LOUD E08 own mounting design',status='design_candidate'):
    return dict(value=value,unit=unit,source=source,status=status,uncertainty=None)
d['connection_mounts_e08']={
    'bracket_vertical_origin':record([.284,.190,.3159],'m'),
    'bracket_vertical_size':record([.038,.018,.002],'m'),
    'bracket_foot_origin':record([.284,.206,.298],'m'),
    'bracket_foot_size':record([.038,.002,.0199],'m'),
    'socket_body_origin':record([.29345,.193175,.3018],'m'),
    'socket_body_size':record([.0191,.01165,.0202],'m','AMASS XT60E-F drawing','manufacturer_reference'),
    'socket_flange_origin':record([.286,.1911,.3179],'m'),
    'socket_flange_size':record([.034,.0158,.0041],'m','AMASS XT60E-F drawing','manufacturer_reference'),
    'socket_hole_x':record([.2905,.3155],'m','AMASS XT60E-F 25mm pitch','manufacturer_reference'),
    'socket_center_y':record(.199,'m'),
    'socket_cutout':record([.0193,.01185,.0039],'m','AMASS XT60E-F drawing: width,height,corner radius','manufacturer_reference'),
    'own_bracket_cut_radius':record(.0002,'m','Own laser-cut aperture: smaller corner radius than recommended panel contour; extra corner clearance, not vendor housing geometry'),
    'roof_hole_x':record([.288,.318],'m'),
    'roof_hole_z':record(.307,'m'),
    'roof_bore':record(.0034,'m'),
    'socket_bolt_length':record(.010,'m'),
    'roof_bolt_length':record(.020,'m'),
}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
