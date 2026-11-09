"""SVG review drawing set from actual E05 CAD edges; no external libraries."""
import csv,html,json,math
from mesh_views import shaded
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/drawings/E05'
def esc(s):return html.escape(str(s))
def text(x,y,s,size=12,color='#24313f'):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" font-family="Arial,sans-serif">{esc(s)}</text>'
def line(x1,y1,x2,y2,color='#64748b',width=.7):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"/>'
def page(title,content,notes=()):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 850" width="1200" height="850">'
        '<rect width="1200" height="850" fill="white"/>'+text(30,35,'OPEN//LOUD  |  '+title,20)+
        text(30,58,'E05 · 2026-11-09 · CAD-derived review sheet · mm · NOT RELEASED FOR MANUFACTURE',11,'#9a3412')+
        content+line(25,765,1175,765)+''.join(text(30,787+i*18,s,11) for i,s in enumerate(notes))+'</svg>')
def projected(part,axis=(0,1),offset=(0,0,0),iso=False):
    result=[]
    for edge in part['edges_mm']:
        pts=[]
        for p in edge:
            x,y,z=[p[i]+offset[i] for i in range(3)]
            pts.append((x-.70*z,-y-.35*z) if iso else ([x,y,z][axis[0]],-[x,y,z][axis[1]]))
        if len(pts)>=2:result.append(pts)
    return result
def fitted(shapes,rect,color='#25384b'):
    pts=[p for shape in shapes for p in shape]
    if not pts:return ''
    lo=[min(p[i] for p in pts) for i in range(2)];hi=[max(p[i] for p in pts) for i in range(2)]
    rx,ry,rw,rh=rect;scale=min(rw/max(hi[0]-lo[0],.01),rh/max(hi[1]-lo[1],.01))
    ox=rx+(rw-(hi[0]-lo[0])*scale)/2;oy=ry+(rh-(hi[1]-lo[1])*scale)/2
    return ''.join('<polyline points="'+' '.join(f'{ox+(x-lo[0])*scale:.2f},{oy+(y-lo[1])*scale:.2f}' for x,y in shape)+f'" fill="none" stroke="{color}" stroke-width="0.65"/>' for shape in shapes)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    geo=json.loads((ROOT/'hardware/mechanical/exports/E05/drawing_geometry.json').read_text(encoding='utf-8'));parts=geo['parts'];byname={p['name']:p for p in parts}
    cutlist=list(csv.DictReader((ROOT/'hardware/mechanical/exports/E03/cutlist_DRAFT.csv').open(encoding='utf-8')))
    created=[];index=['# E05 CAD review drawing set','',
        'Actual edge geometry from the checked E05 model. All edges shown; hidden-line removal is NOT implemented. No dimensional/tolerance, fit, safety or manufacturing release. SVGs are scalable; print without assuming a scale.','',
        '| Pos. | Part | Qty | Material | Nominal blank mm | Review sheet |','|---:|---|---:|---|---|---|']
    for number,row in enumerate(cutlist,1):
        name=row['component'];part=byname[name];pts=[p for edge in part['edges_mm'] for p in edge]
        span=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)];thin=min(range(3),key=lambda i:span[i]);axes=tuple(i for i in range(3) if i!=thin)
        body=fitted(projected(part,axes),(100,110,720,550))
        lengths=sorted(span);blank=f'{lengths[2]:.2f} x {lengths[1]:.2f} x {lengths[0]:.2f}'
        body+=text(870,125,f'POSITION {number:02d}',16)+text(870,153,'Quantity: 1')+text(870,180,'Material:')+text(870,201,row['material'],11)
        body+=text(870,235,'Nominal blank [mm]:')+text(870,257,blank,11)+text(870,290,'Coordinate axes: '+','.join('XYZ'[i] for i in axes))
        body+=text(870,320,'All CAD edges visible',11)+text(870,341,'Pockets may overlap in projection',10)
        if name.startswith('Rear_thread_plate_'):body+=text(870,380,'4.2 pilot -> TAP M5x0.8',12,'#9a3412')
        if name=='Service_floor':body+=text(870,380,'E05 LF: bore16.5; relief28x5',11,'#9a3412')
        if name=='Service_partition':body+=text(870,380,'E05 HF: bore16.5; relief28x5',11,'#9a3412')
        # Real global datum extents avoid inventing ordinate hole dimensions.
        body+=text(70,700,'CAD datum bounds (global XYZ, mm):',12)
        for i in range(3):body+=text(70+i*285,725,f"{'XYZ'[i]}: {min(p[i] for p in pts):.3f} ... {max(p[i] for p in pts):.3f}",11)
        filename=f'{number:02d}_{name}.svg';created.append(filename)
        (OUT/filename).write_text(page(f'{number:02d} / {name}',body,(
            'Geometry: own E05 CAD; chord tolerance0.3mm. Blank dimensions are geometric envelopes, not toleranced machining dimensions.',
            'Use checked STEP/DXF and E05 pocket definitions together. Fastener counterpieces, seals and tool access require remaining review.',
            'Unspecified tolerances/finish/adhesive joints: OPEN. Do not treat this review sheet as a released part drawing.')),encoding='utf-8')
        index.append(f"| {number} | {name} | 1 | {row['material']} | {blank} | [{filename}]({filename}) |")
    # Orthographic assembly review: fasteners visible, internal surfaces all shown.
    shown=[p for p in parts if not p['name'].startswith('RESERVE_')]
    body=''
    for label,axes,rect in [('FRONT X/Y',(0,1),(40,115,320,590)),('SIDE Z/Y',(2,1),(430,115,320,590)),('TOP X/Z',(0,2),(820,115,320,590))]:
        body+=text(rect[0],95,label,15)
        body+=fitted([shape for p in shown for shape in projected(p,axes)],rect)
    (OUT/'assembly_orthographic.svg').write_text(page('Assembly / orthographic',body,(
        '330x560x300mm cabinet reference. Screw heads extend beyond envelope. Wireframe shows interior edges too.',
        'Simplified driver/horn envelopes; no acoustic mesh, weatherproofing or assembly certification.')),encoding='utf-8');created.append('assembly_orthographic.svg')
    # Explode actual panel/driver/representative fastening geometries virtually; source model unchanged.
    translations={'Side_left':(-160,0,0),'Side_right':(160,0,0),'Top':(0,150,0),'Bottom':(0,-130,0),
        'Baffle':(0,0,-210),'Baffle_inner_lamination':(0,0,-140),'LF_steel_backing_ring_candidate':(0,0,-75),
        'Rear_removable':(0,0,230),'Service_partition':(0,115,70),'Service_floor':(0,60,100),
        'REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE':(0,0,-340),'REF_BC_ME10V3_DATASHEET_ENVELOPE':(0,0,-340),
        'REF_BC_DE10_DATASHEET_ENVELOPE':(0,0,-240),'Port_tube_candidate':(0,0,-240)}
    explode=[]
    for p in parts:
        n=p['name']
        if n in translations:explode+=projected(p,offset=translations[n],iso=True)
        elif not n.startswith(('E05_','RESERVE_')):explode+=projected(p,offset=(0,0,90 if n.startswith('Rear_') else 0),iso=True)
    mesh=json.loads((ROOT/'hardware/mechanical/exports/E05/mesh_geometry.json').read_text(encoding='utf-8'))
    translations.update(Side_left=(-260,0,0),Side_right=(260,0,0),Top=(0,220,0),Bottom=(0,-180,0),
        Baffle=(0,0,-420),Baffle_inner_lamination=(0,0,-270),LF_steel_backing_ring_candidate=(0,0,-130),
        Rear_removable=(0,0,310),REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE=(0,0,-720),
        REF_BC_ME10V3_DATASHEET_ENVELOPE=(0,0,-720),REF_BC_DE10_DATASHEET_ENVELOPE=(0,0,-570))
    body=shaded(mesh,translations,(40,105,870,630))
    body+=text(930,130,'Virtual exploded layout',15)+text(930,160,'Panels, port, LF and HF',11)+text(930,185,'Actual CAD edge geometry',11)
    body+=text(930,225,'Fasteners omitted here;',11)+text(930,244,'see fastener assembly sheet',11)
    (OUT/'assembly_exploded.svg').write_text(page('Assembly / exploded review',body,(
        'Virtual translations only; does not alter the assembled CAD. Explosion directions are presentation directions, not insertion proofs.',
        'See individual sheets and wiring documentation for fastener quantities and counterpieces. Positions follow part index.')),encoding='utf-8');created.append('assembly_exploded.svg')
    # Explicit fastening cross-sections diagram: every metric screw has a mate.
    body=''
    for title,x,y,layers in [('LF M5x45 / 8x',80,145,[('head',5),('washer',1),('LF flange',8),('baffle',24),('steel ring',3),('washer',1),('M5 nut',4.7)]),
        ('Horn M4x40 / 4x',80,330,[('head',4),('washer',.8),('horn flange',5.5),('baffle',24),('washer',.8),('M4 nut',3.2)]),
        ('Rear M5x40 / 10x',80,515,[('head',5),('washer',1),('rear panel',12),('cleat',20),('M5 tapped plate',5)])]:
        body+=text(x,y-28,title,17);cur=x
        for j,(label,length) in enumerate(layers):
            width=max(length*9,15);body+=f'<rect x="{cur}" y="{y}" width="{width}" height="50" fill="{["#cbd5e1","#e2e8f0","#c7b49b"][j%3]}" stroke="#475569"/>'
            body+=text(cur,y+70,str(j+1),11)+text(cur,y+87,str(length)+'mm',10)
            body+=text(850,y+4+j*18,f'{j+1}. {label}: {length} mm',11);cur+=width+12
        body+=line(x,y+25,cur,y+25,'#334155',3)
    (OUT/'fastener_stacks.svg').write_text(page('Fastener assemblies / nominal stacks',body,(
        'Schematic layer stacks, not geometric scale. Standard nuts/threaded plates receive all metric threads; no metric thread cut in wood.',
        'LF ring/nut access tested geometrically. Horn nut service access, actual gaskets/tolerances and tightening torque remain open.')),encoding='utf-8');created.append('fastener_stacks.svg')
    (OUT/'README.md').write_text('\n'.join(index)+'\n\nAssemblies: [orthographic](assembly_orthographic.svg), [exploded](assembly_exploded.svg), [fastener stacks](fastener_stacks.svg).\n',encoding='utf-8')
    (OUT/'drawing_manifest.json').write_text(json.dumps(dict(revision='E05',status='REVIEW_NOT_MANUFACTURING_RELEASE',part_sheets=len(cutlist),files=created,source='hardware/mechanical/exports/E05/drawing_geometry.json'),indent=2)+'\n',encoding='utf-8')
    # Parse all SVGs: malformed XML is a real failure.
    import xml.etree.ElementTree as ET
    for name in created:ET.parse(OUT/name)
    print(json.dumps({'part_sheets':len(cutlist),'assembly_sheets':3,'svg_xml_checked':len(created)}))
if __name__=='__main__':main()
