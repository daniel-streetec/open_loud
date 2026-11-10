"""Dimensioned own-part review sheet from central inputs, not a bend blank release."""
import json,html,hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/drawings/E09'
def main():
    data=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'))
    p={k:r['value'] for k,r in data['connection_mounts_e09'].items()}
    OUT.mkdir(parents=True,exist_ok=True);parts=[]
    def text(x,y,s,size=4):parts.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>')
    def line(x1,y1,x2,y2):parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#111" stroke-width=".3"/>')
    def dim(x,y,w,label):
        line(x,y,x+w,y)
        for xx in (x,x+w):line(xx,y-1.5,xx,y+1.5)
        text(x+w/2-5,y-2,label,3.5)
    scale=2;vx,vy,vz=p['bracket_vertical_origin'];w,h,t=p['bracket_vertical_size']
    W=w*1000;H=h*1000;depth=p['bracket_foot_size'][2]*1000
    text(15,15,'OPEN//LOUD – E09 interner Ladebuchsenhalter',6)
    text(15,23,'Montage-/Prüfzeichnung, Maße in mm; Ansichten 2:1 auf A4 quer',4)
    text(15,30,'ENTWURF – keine Fertigungsfreigabe',4)
    x0=25;y0=50
    parts.append(f'<rect x="{x0}" y="{y0}" width="{W*scale}" height="{H*scale}" fill="none" stroke="#111" stroke-width=".4"/>')
    cw,ch,_=p['socket_cutout'];rr=p['own_bracket_cut_radius']
    cx=p['socket_flange_origin'][0]+p['socket_flange_size'][0]/2;cy=p['socket_center_y']
    cutx=x0+(cx-vx-cw/2)*1000*scale;cuty=y0+(vy+h-cy-ch/2)*1000*scale
    parts.append(f'<rect x="{cutx}" y="{cuty}" width="{cw*1000*scale}" height="{ch*1000*scale}" rx="{rr*1000*scale}" fill="none" stroke="#111" stroke-width=".3"/>')
    for hx in p['socket_hole_x']:
        xx=x0+(hx-vx)*1000*scale;yy=y0+(vy+h-cy)*1000*scale
        parts.append(f'<circle cx="{xx}" cy="{yy}" r="{1.7*scale}" fill="none" stroke="#111" stroke-width=".3"/>')
    dim(x0,y0-7,W*scale,f'{W:g}')
    text(x0,y0+H*scale+8,f'Frontplatte {W:g} × {H:g} × {t*1000:g}',4)
    text(135,49,'Steckerbohrungen relativ zu links/unten:',4)
    for i,hx in enumerate(p['socket_hole_x']):text(135,56+i*6,f'{i+1}: X={(hx-vx)*1000:.2f}, Y={(cy-vy)*1000:.2f}; Ø3,4',3.5)
    text(135,72,f'Ausschnitt {cw*1000:g} × {ch*1000:g}, R{rr*1000:g}',3.5)
    text(135,78,'Zusätzliche Eckfreiheit gegenüber Herstellerkontur.',3.5)
    x1=25;y1=113;foot=p['bracket_foot_origin']
    parts.append(f'<rect x="{x1}" y="{y1}" width="{W*scale}" height="{depth*scale}" fill="none" stroke="#111" stroke-width=".4"/>')
    for hx in p['roof_hole_x']:
        xx=x1+(hx-foot[0])*1000*scale;yy=y1+(p['roof_hole_z']-foot[2])*1000*scale
        parts.append(f'<circle cx="{xx}" cy="{yy}" r="{p["roof_bore"]*1000*scale/2}" fill="none" stroke="#111" stroke-width=".3"/>')
    text(x1,y1+depth*scale+8,f'Fuß {W:g} × {depth:g} × 2; Draufsicht',4)
    for i,hx in enumerate(p['roof_hole_x']):text(135,116+i*6,f'Fuß {i+1}: X={(hx-foot[0])*1000:g}, Z={(p["roof_hole_z"]-foot[2])*1000:g}; Ø3,4',3.5)
    text(135,135,'2× M3×10 + rückseitige Scheibe/Mutter am Stecker',3.5)
    text(135,141,'2× M3×20 + 2 Scheiben/Mutter durch 12-mm-Dach',3.5)
    text(15,177,'OFFEN: Werkstoff, Biegeradius/-zugabe, Toleranzen, Schraubensicherung und Dichtung.',3.8)
    text(15,184,'Vor Akku-Einsatz montieren. Polraum und Gegenstecker am Originalteil prüfen.',3.8)
    text(15,194,'Quelle: data/experiments/E09_parameters.json → connection_mounts_e09. Kein abgewickelter Zuschnitt.',3.5)
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><rect width="297" height="210" fill="white"/><g font-family="Arial,sans-serif">'+''.join(parts)+'</g></svg>'
    path=OUT/'charge_bracket_review.svg';path.write_text(svg,encoding='utf-8')
    book=OUT/'charge_bracket_review.html';book.write_text('<!doctype html><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}html,body{margin:0;padding:0;width:297mm;height:210mm;overflow:hidden}svg{display:block;width:297mm;height:210mm}</style>'+svg,encoding='utf-8')
    edge=Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe');assert edge.exists()
    profile=ROOT/'.tools/edge-e08-bracket';profile.mkdir(parents=True,exist_ok=True);pdf=OUT/'charge_bracket_review.pdf'
    subprocess.run([str(edge),'--headless','--disable-gpu',f'--user-data-dir={profile}','--no-pdf-header-footer',f'--print-to-pdf={pdf}',book.as_uri()],check=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sys.path.insert(0,str(ROOT/'.tools/python'));from pypdf import PdfReader
    doc=PdfReader(pdf);assert len(doc.pages)==1 and 'OPEN//LOUD' in doc.pages[0].extract_text()
    report=dict(status='passed',pages=1,scope='Generated PDF page and text extraction, not manufacturing approval',parameter_sha256=hashlib.sha256((ROOT/'data/experiments/E09_parameters.json').read_bytes()).hexdigest())
    (OUT/'charge_bracket_pdf_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
