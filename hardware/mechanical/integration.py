"""E04 SI cable geometry and independent mechanical/electrical checks."""
import math


def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,k):return [x*k for x in a]
def norm(a):return math.sqrt(dot(a,a))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def rounded_route(points,radius):
    """Sample exact circular fillets, checking available tangent lengths."""
    nodes=[]
    for i in range(1,len(points)-1):
        b=points[i];incoming=sub(b,points[i-1]);outgoing=sub(points[i+1],b)
        u=mul(incoming,1/norm(incoming));v=mul(outgoing,1/norm(outgoing))
        angle=math.acos(max(-1,min(1,dot(u,v))))
        if angle<1e-8:
            nodes.append((b,b,[b],0,0));continue
        tangent=radius*math.tan(angle/2)
        assert tangent<norm(incoming) and tangent<norm(outgoing),(i,'bend too tight')
        entry=sub(b,mul(u,tangent));exit_=add(b,mul(v,tangent))
        n=cross(u,v);n=mul(n,1/norm(n))
        center=add(entry,mul(cross(n,u),radius));radial=sub(entry,center)
        samples=[]
        for j in range(9):
            a=angle*j/8
            samples.append(add(center,add(mul(radial,math.cos(a)),mul(cross(n,radial),math.sin(a)))))
        nodes.append((entry,exit_,samples,tangent,angle))
    for i in range(len(nodes)-1):
        assert nodes[i][3]+nodes[i+1][3]<norm(sub(points[i+2],points[i+1])),('overlapping fillets',i)
    result=[points[0]]
    for node in nodes:result+=node[2]
    result.append(points[-1])
    raw=sum(norm(sub(b,a)) for a,b in zip(points,points[1:]))
    length=raw-sum(2*n[3]-radius*n[4] for n in nodes)
    return result,length


def calculate(data):
    p={k:v['value'] for k,v in data['integration'].items()}
    m={k:v['value'] for k,v in data['mechanical'].items() if isinstance(v,dict) and 'value' in v}
    basket_rear=m['lf_depth']-m['lf_flange']-m['lf_magnet_depth']
    z=2*m['wall']
    basket_d=m['lf_basket_d']+(m['lf_magnet_d']-m['lf_basket_d'])*(z-p['basket_lip_depth'])/(basket_rear-p['basket_lip_depth'])
    ring_clearance=(m['lf_backing_inner_d']-basket_d)/2
    gland_stack=p['bulkhead_plate_size'][1]+p['bulkhead_seal']+p['gland_nut_depth']
    routes={}
    for kind in ('power','lf','hf'):
        samples,length=rounded_route(p[kind+'_route'],p['cable_bend_radius'])
        cut_length=length*(1+p['slack_fraction'])+p['termination_allowance']
        conductor=p[kind+'_conductor']
        resistance=2*cut_length*p['copper_resistivity_20C']/conductor
        routes[kind]={'sampled_points_m':samples,'route_length_m':length,'cut_length_m':cut_length,'conductor_mm2':conductor,
                      'loop_resistance_20C_ohm':resistance,'loop_resistance_60C_ohm':resistance*(1+40*p['copper_alpha'])}
    open_fraction=(1-p['mesh_wire']/p['mesh_pitch'])**2
    hood_exit=(p['port_hood_size'][0]-2*p['hood_wall'])*(p['port_hood_size'][2]-p['hood_wall'])
    return {'status':'analytical_screening_not_physical_validation','ring_clearance_conservative_m':ring_clearance,
            'ring_required_m':p['ring_radial_min'],'gland_thread_margin_m':p['gland_thread_length']-gland_stack,
            'standard_gland_direct_12mm_wood_fits':p['gland_thread_length']>=m['wall']+p['bulkhead_seal']+p['gland_nut_depth'],
            'mesh_open_fraction_ideal':open_fraction,'hood_bottom_free_m2':hood_exit,
            'port_area_m2':data['concepts']['A0']['port_area']['value'],'routes':routes,
            'rear_guard_panel_edge_clearance_m':m['wall']-p['rear_guard_lip']}
