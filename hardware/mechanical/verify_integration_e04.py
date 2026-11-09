"""Real BRep insertion, extraction and tool-corridor checks; no physical claims."""
import adsk.core, adsk.fusion
import json, math, sys, importlib
from pathlib import Path

ROOT=Path(r'C:\Repositories\open_loud')
OUT=ROOT/'hardware/mechanical/exports/E04'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import integration as integration_module
importlib.reload(integration_module)

def run(_context: str):
    app=adsk.core.Application.get();design=adsk.fusion.Design.cast(app.activeProduct);root=design.rootComponent
    assert root.attributes.itemByName('OPEN_LOUD','integration_ready').value=='E04'
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    m={k:v['value'] for k,v in data['mechanical'].items() if isinstance(v,dict) and 'value' in v}
    p={k:v['value'] for k,v in data['integration'].items()}
    tm=adsk.fusion.TemporaryBRepManager.get();P=adsk.core.Point3D.create
    def point(a):return P(*(x*100 for x in a))
    def cylinder(a,b,r):return tm.createCylinderOrCone(point(a),r*100,point(b),r*100)
    # Restore only the genuine flange reference; the old optimistic basket stays hidden.
    legacy=next(o.component for o in root.occurrences if o.component.name=='REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE')
    for b in legacy.bRepBodies:
        if b.name=='LF_flange_envelope':b.isLightBulbOn=True
    items=[]
    for o in root.occurrences:
        for b in o.component.bRepBodies:
            if b.isLightBulbOn:items.append((o.component.name,b))
    numerical=[]
    def overlap(a,b):
        aa=a.boundingBox;bb=b.preciseBoundingBox
        return all(aa.maxPoint.asArray()[i]>bb.minPoint.asArray()[i]+1e-7 and bb.maxPoint.asArray()[i]>aa.minPoint.asArray()[i]+1e-7 for i in range(3))
    def clashes(tool,exclude=()):
        result=[]
        for name,b in items:
            if any(name.startswith(x) for x in exclude) or not overlap(tool,b):continue
            copy=tm.copy(tool)
            success=tm.booleanOperation(copy,b,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if not success:
                numerical.append(name);continue
            if copy.isValid and copy.faces.count and copy.volume>1e-6:
                result.append({'component':name,'intersection_cm3':copy.volume})
        return result
    base_exclude=('Rear_removable','E04_cable_','E04_RESERVE_')
    # Fitting the conservative basket into the changed ring is an actual kernel test.
    ring=next(b for n,b in items if n=='LF_steel_backing_ring_candidate')
    basket=[b for n,b in items if n=='E04_LF_conservative_basket_envelope']
    ring_hits=[]
    for b in basket:
        x=tm.copy(b);ok=tm.booleanOperation(x,ring,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        if not ok:numerical.append('basket_ring')
        elif x.isValid and x.faces.count and x.volume>1e-6:ring_hits.append(x.volume)
    # Eight LF nuts: first straight, then an articulated extension if obstructed.
    lf=[]
    for i in range(8):
        a=i*math.pi/4;x=m['width']/2+m['lf_pcd']/2*math.cos(a);y=m['lf_y']+m['lf_pcd']/2*math.sin(a)
        start=[x,y,2*m['wall']+m['lf_backing_thickness']+.0002]
        stub=[x,y,start[2]+p['tool_stub']]
        direct=clashes(cylinder(start,[x,y,m['depth']+.020],p['tool_socket_d']/2),base_exclude)
        entry_y=.280 if y>.330 else .200 if y<.160 else y
        entry=[x,entry_y,m['depth']+.020]
        angle=math.degrees(math.atan2(abs(entry_y-y),entry[2]-stub[2]))
        articulated=clashes(cylinder(start,stub,p['tool_socket_d']/2),base_exclude)
        articulated+=clashes(cylinder(stub,entry,p['tool_joint_d']/2),base_exclude)
        lf.append({'bolt_index':i,'straight_obstructions':direct,'articulated_angle_deg':angle,'articulated_obstructions':articulated,
                   'accepted':not direct or (not articulated and angle<=p['tool_max_angle'])})
    # Horn is serviced from the front against fixed thread plates, after grille removal.
    horn=[]
    front_exclude=('E04_front_grille','E04_port_splash_hood','E04_cable_','E04_RESERVE_')
    for ix in (-1,1):
        for iy in (-1,1):
            x=m['width']/2+ix*m['horn_bolt_pitch']/2;y=m['horn_y']+iy*m['horn_bolt_pitch']/2
            hits=clashes(cylinder([x,y,-.120],[x,y,-m['horn_flange']-.0002],.005),front_exclude)
            horn.append({'position_m':[x,y],'front_tool_obstructions':hits,'accepted':not hits})
    # All ten rear-cover heads are externally accessible despite guards/drip cap.
    rear=[]
    locations=[(x,m['height']*f) for x in (m['wall']+m['rear_cleat_width']/2,m['width']-m['wall']-m['rear_cleat_width']/2) for f in (.15,.5,.85)]
    locations += [(m['width']*f,y) for y in (m['wall']+m['rear_cleat_width']/2,m['height']-m['wall']-m['rear_cleat_width']/2) for f in (.27,.73)]
    for x,y in locations:
        hits=clashes(cylinder([x,y,m['depth']+.0002],[x,y,m['depth']+.100],.0055),('E04_cable_','E04_RESERVE_'))
        rear.append({'position_m':[x,y],'obstructions':hits,'accepted':not hits})
    def translation_test(prefixes,offsets,extra_exclude=()):
        moving=[(n,b) for n,b in items if any(n.startswith(x) for x in prefixes)]
        failures=[]
        for dz in offsets:
            matrix=adsk.core.Matrix3D.create();matrix.translation=adsk.core.Vector3D.create(0,0,dz*100)
            for name,b in moving:
                shape=tm.copy(b);tm.transform(shape,matrix)
                hits=clashes(shape,tuple(prefixes)+tuple(extra_exclude))
                if hits:failures.append({'moving':name,'dz_m':dz,'hits':hits})
        return {'moving_bodies':len(moving),'sampled_offsets_m':offsets,'failures':failures,'accepted':not failures}
    rear_motion=translation_test(('Rear_removable',),[.001,.010,.030,.100],('E04_cable_','E04_RESERVE_'))
    tray_motion=translation_test(('E04_electronics_tray','E04_REF_JAB3_','E04_PCB_standoff_'),[.001,.020,.060,.150],('Rear_removable','E04_cable_','E04_RESERVE_'))
    driver_motion=translation_test(('E04_LF_conservative_basket_envelope','REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE'),[-.120,-.080,-.040,-.010,-.001,0],('E04_front_grille','E04_port_splash_hood','E04_cable_','E04_RESERVE_'))
    # Check final wire envelopes against physical cabinetry, excluding intended gland passages.
    cables=[]
    for name,b in items:
        if not name.startswith('E04_cable_'):continue
        hits=clashes(b,('E04_cable_','E04_RESERVE_','E04_speaker_gland_','E04_power_entry_gland'))
        if hits:cables.append({'wire':name,'obstructions':hits})
    issues=[]
    for i in range(design.timeline.count):
        item=design.timeline.item(i)
        if item.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append({'name':item.name,'state':item.healthState,'message':item.errorOrWarningMessage})
    report={'revision':'E04','status':'passed' if not (ring_hits or numerical or issues or cables) and all(x['accepted'] for x in lf+horn+rear) and all(x['accepted'] for x in (rear_motion,tray_motion,driver_motion)) else 'requires_revision',
            'scope':'Nominal CAD kernels and sampled motions, not actual part tolerances, continuous-motion proof, tool catalogue geometry, hand access or physical assembly',
            'basket_ring_intersection_cm3':ring_hits,'lf_nut_tool_access':lf,'horn_front_tool_access':horn,'rear_screw_access':rear,
            'rear_cover_extraction':rear_motion,'tray_extraction_unplugged':tray_motion,'LF_insertion_grille_removed':driver_motion,
            'wire_interferences':cables,'timeline_issues':issues,'kernel_failures':sorted(set(numerical)),
            'assembly_states':'Rear open for LF nuts. For tray removal disconnect power/speakers/programmer and stow service tails. Grille/hood removed before horn or LF service.',
            'analytical_screening':{k:v for k,v in integration_module.calculate(data).items() if k!='routes'}}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'assembly_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'straight_LF_blocked':sum(bool(x['straight_obstructions']) for x in lf),'LF_accepted':sum(x['accepted'] for x in lf),
                      'horn_accepted':sum(x['accepted'] for x in horn),'rear_accepted':sum(x['accepted'] for x in rear),'motions':{k:report[k]['accepted'] for k in ('rear_cover_extraction','tray_extraction_unplugged','LF_insertion_grille_removed')},'wire_interferences':len(cables),'kernel_failures':report['kernel_failures'],'timeline_issues':issues}))
