"""SI layout and volume budget, independent of Fusion's expression evaluator."""
import math


def calculate(data):
    m={k:r['value'] for k,r in data['mechanical'].items() if isinstance(r,dict) and 'value' in r}
    case={k:r['value'] for k,r in data['concepts']['A0'].items() if isinstance(r,dict) and 'value' in r}
    wi=m['width']-2*m['wall'];hi=m['height']-2*m['wall'];di=m['depth']-2*m['wall']
    area=case['port_area'];vb=case['Vb'];fb=case['Fb']
    diameter=2*math.sqrt(area/math.pi)
    length=data['environment']['c']['value']**2*area/((2*math.pi*fb)**2*vb)-data['model']['end_correction']['value']*diameter
    port=math.pi/4*(diameter+2*m['port_wall'])**2*(length-2*m['wall'])
    reinforcement=(wi*hi-math.pi/4*(m['lf_cutout']+2*m['baffle_clearance'])**2-math.pi/4*(diameter+2*m['port_wall']+2*m['baffle_clearance'])**2-m['horn_cutout']**2-8*math.pi/4*m['lf_bolt_clearance']**2-4*math.pi/4*m['horn_bolt_clearance']**2)*m['wall']
    cleats=(2*m['rear_cleat_width']*(m['service_floor_y']-m['wall'])+(wi-2*m['rear_cleat_width'])*m['rear_cleat_width'])*m['rear_cleat_depth']
    ro=m['lf_backing_outer_d']/2;ri=m['lf_backing_inner_d']/2
    rp=(diameter+2*m['port_wall'])/2+m['port_backing_relief'];gap=m['lf_y']-m['port_y']
    lens=0.0
    if gap<ro+rp:
        lens=ro*ro*math.acos((gap*gap+ro*ro-rp*rp)/(2*gap*ro))+rp*rp*math.acos((gap*gap+rp*rp-ro*ro)/(2*gap*rp))-.5*math.sqrt((-gap+ro+rp)*(gap+ro-rp)*(gap-ro+rp)*(gap+ro+rp))
    backing=(math.pi*(ro*ro-ri*ri)-lens-8*math.pi/4*m['lf_bolt_clearance']**2)*m['lf_backing_thickness']
    hf=math.pi/4*m['hf_diameter']**2*m['hf_depth']
    brace=wi*m['brace_height']*m['wall']
    lf=data['drivers']['10FE200-4']['displacement']['value']
    rear_plate_volume=(m['rear_plate_width']*m['rear_plate_length']-math.pi/4*(m['rear_tap_pilot']**2+2*m['rear_retainer_bore']**2))*m['rear_plate_thickness']
    # Six lower plates lie in the acoustic chamber; four upper ones lie in service space.
    rear_fixing=6*(rear_plate_volume-math.pi/4*m['rear_bolt_clearance']**2*m['rear_cleat_depth'])
    exclusion=wi*hi*di-vb-reinforcement-cleats-backing-port-lf-m['horn_displacement']-hf-brace-rear_fixing
    z=m['depth']-m['wall']-exclusion/(wi*(m['height']-m['wall']-m['service_floor_y']))
    assert z>m['horn_depth']-m['horn_flange']+m['hf_depth']+.01
    assert length<m['depth']-m['wall']-diameter
    return dict(dimensions=m,inner_width=wi,inner_height=hi,inner_depth=di,port_d=diameter,port_length=length,
                port_displacement=port,reinforcement_displacement=reinforcement,cleat_acoustic_displacement=cleats,
                backing_displacement=backing,hf_displacement=hf,brace_displacement=brace,
                rear_fixing_displacement=rear_fixing,rear_plate_volume=rear_plate_volume,
                service_excluded=exclusion,service_z=z,relief_required=bool(lens),gross_internal=wi*hi*di,target_net=vb)
