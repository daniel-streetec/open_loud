"""Actually rerender all plot formats twice and inspect PDF, not just file presence."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/dsp/E09'
if __name__=='__main__':
    versions=[]
    for _ in range(2):
        subprocess.run([sys.executable,'-B','tools/plot_dsp_e09.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        versions.append(json.loads((OUT/'plot_manifest.json').read_text(encoding='utf-8')))
    assert versions[0]==versions[1],'Plot formats changed between identical renders'
    sys.path.insert(0,str(ROOT/'.tools/python'));from pypdf import PdfReader
    pdf=PdfReader(OUT/'LF_protection.pdf');assert len(pdf.pages)==1 and 'OPEN//LOUD' in pdf.pages[0].extract_text()
    report=dict(status='passed',formats=['PNG','SVG','PDF'],two_renders_byte_identical=True,pdf_pages=1,
        scope='Actual regenerated artifact bytes, PDF text/pages; visual review separately performed')
    (OUT/'plot_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
