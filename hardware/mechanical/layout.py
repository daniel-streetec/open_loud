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
    battery=data.get('battery_mount',{})
    b={k:r['value'] for k,r in battery.items()}
    battery_box=None
    if b:
        battery_box=([b['bay_left'],m['wall'],b['bay_front']],
                     [m['width']-m['wall']-b['bay_left'],b['bay_top']-m['wall'],m['depth']-m['wall']-b['bay_front']])
    def volume(box):return math.prod(box[1])
    def overlap(a,b):
        return math.prod(max(0,min(a[0][i]+a[1][i],b[0][i]+b[1][i])-max(a[0][i],b[0][i])) for i in range(3))
    cw=m['rear_cleat_width'];cd=m['rear_cleat_depth'];wall=m['wall'];rear=m['depth']-wall-cd
    boxes=[([wall,wall,rear],[cw,hi,cd]),([m['width']-wall-cw,wall,rear],[cw,hi,cd]),
           ([wall+cw,wall,rear],[wi-2*cw,cw,cd]),([wall+cw,m['height']-wall-cw,rear],[wi-2*cw,cw,cd])]
    service_mask=([wall,m['service_floor_y'],0],[wi,m['height']-wall-m['service_floor_y'],m['depth']])
    cleats=sum(volume(q)-overlap(q,service_mask)-(overlap(q,battery_box) if battery_box else 0) for q in boxes)
    ro=m['lf_backing_outer_d']/2;ri=m['lf_backing_inner_d']/2
    rp=(diameter+2*m['port_wall'])/2+m['port_backing_relief'];gap=math.hypot(m.get('port_x',m['width']/2)-m['width']/2,m['lf_y']-m['port_y'])
    lens=0.0
    if gap<ro+rp:
        lens=ro*ro*math.acos((gap*gap+ro*ro-rp*rp)/(2*gap*ro))+rp*rp*math.acos((gap*gap+rp*rp-ro*ro)/(2*gap*rp))-.5*math.sqrt((-gap+ro+rp)*(gap+ro-rp)*(gap-ro+rp)*(gap+ro+rp))
    backing=(math.pi*(ro*ro-ri*ri)-lens-8*math.pi/4*m['lf_bolt_clearance']**2)*m['lf_backing_thickness']
    hf=math.pi/4*m['hf_diameter']**2*m['hf_depth']
    brace=wi*m['brace_height']*m['wall']
    lf=data['drivers']['10FE200-4']['displacement']['value']
    rear_plate_volume=(m['rear_plate_width']*m['rear_plate_length']-math.pi/4*(m['rear_tap_pilot']**2+2*m['rear_retainer_bore']**2))*m['rear_plate_thickness']
    positions=[(x,m['height']*f) for x in (wall+cw/2,m['width']-wall-cw/2) for f in (.15,.5,.85)]
    positions += [(m['width']*f,y) for y in (wall+cw/2,m['height']-wall-cw/2) for f in (.27,.73)]
    acoustic_plates=sum(y<m['service_floor_y'] and not(b and x>=b['bay_left'] and y<b['bay_top']) for x,y in positions)
    rear_fixing=acoustic_plates*(rear_plate_volume-math.pi/4*m['rear_bolt_clearance']**2*cd)
    battery_excluded=volume(battery_box) if battery_box else 0
    exclusion=wi*hi*di-vb-reinforcement-cleats-backing-port-lf-m['horn_displacement']-hf-brace-rear_fixing-battery_excluded
    z=m['depth']-m['wall']-exclusion/(wi*(m['height']-m['wall']-m['service_floor_y']))
    assert z>m['horn_depth']-m['horn_flange']+m['hf_depth']+.01
    assert length<m['depth']-m['wall']-diameter
    assert z<rear,'Service mask assumes rear cleats are entirely behind the partition'
    return dict(dimensions=m,inner_width=wi,inner_height=hi,inner_depth=di,port_d=diameter,port_length=length,
                port_displacement=port,reinforcement_displacement=reinforcement,cleat_acoustic_displacement=cleats,
                backing_displacement=backing,hf_displacement=hf,brace_displacement=brace,
                rear_fixing_displacement=rear_fixing,rear_plate_volume=rear_plate_volume,
                battery_excluded=battery_excluded,acoustic_rear_plates=acoustic_plates,
                service_excluded=exclusion,service_z=z,relief_required=bool(lens),gross_internal=wi*hi*di,target_net=vb)
