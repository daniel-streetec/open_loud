"""Render own SVG review pages with locally installed Edge; validate actual PDF."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/drawings/E05'
def main():
    manifest=json.loads((OUT/'drawing_manifest.json').read_text(encoding='utf-8'))
    pages=['assembly_exploded.svg','assembly_orthographic.svg','fastener_stacks.svg']+[n for n in manifest['files'] if n not in ('assembly_exploded.svg','assembly_orthographic.svg','fastener_stacks.svg')]
    html='<!doctype html><html><head><meta charset="utf-8"><title>OPEN LOUD E05 review</title><style>@page{size:A3 landscape;margin:0}html,body{margin:0;padding:0}section{display:block;break-after:page;break-inside:avoid;width:419mm;height:296mm;overflow:hidden}section:last-child{break-after:auto}svg{display:block;width:100%;height:100%}</style></head><body>'
    for name in pages:html+='<section>'+(OUT/name).read_text(encoding='utf-8')+'</section>'
    html+='</body></html>';book=OUT/'review_drawings.html';book.write_text(html,encoding='utf-8')
    edge=Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe');assert edge.exists(),'Edge unavailable; SVG sheets still usable'
    profile=ROOT/'.tools/edge-drawings';profile.mkdir(parents=True,exist_ok=True)
    pdf=OUT/'OPEN_LOUD_E05_review_drawings.pdf'
    subprocess.run([str(edge),'--headless','--disable-gpu',f'--user-data-dir={profile}','--no-pdf-header-footer',f'--print-to-pdf={pdf}',book.as_uri()],check=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sys.path.insert(0,str(ROOT/'.tools/python'))
    from pypdf import PdfReader
    document=PdfReader(pdf);assert len(document.pages)==len(pages),(len(document.pages),len(pages))
    assert all('OPEN//LOUD' in (page.extract_text() or '') for page in document.pages)
    report=dict(status='passed',pdf_pages=len(document.pages),bytes=pdf.stat().st_size,scope='Actual page count and text extraction; review sheets, not manufacturing approval')
    (OUT/'pdf_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':main()
