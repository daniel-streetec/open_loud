"""Audit E07 structure/BOM and actual CAD verification records; hash deliverables."""
import csv,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/mechanical/exports/E07'
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from assemblies import classify
def main():
    structure=json.loads((ROOT/'data/assembly_structure.json').read_text(encoding='utf-8'))
    baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))
    mapping=json.loads((OUT/'assembly_mapping.json').read_text(encoding='utf-8'))['moved']
    hierarchy=json.loads((OUT/'hierarchy_validation.json').read_text(encoding='utf-8'))
    exports=json.loads((OUT/'export_validation.json').read_text(encoding='utf-8'))
    assert hierarchy['status']==exports['status']=='passed' and exports['saved']
    assert len(mapping)==len(baseline['components'])==hierarchy['leaf_components']
    assert {r['component'] for r in mapping}=={r['component'] for r in baseline['components']}
    assert all(classify(r['component'],structure)==r['assembly'] for r in mapping)
    grouped=list(csv.DictReader((OUT/'assembly_bom_grouped.csv').open(encoding='utf-8')))
    assert sum(int(r['model_quantity']) for r in grouped)==len(mapping)
    assert len(exports['physical_subassemblies'])==5
    assert sum(r['observed']['bodies'] for r in exports['physical_subassemblies'])==exports['step']['observed']['bodies']
    assert hierarchy['solid_bodies']==exports['step']['observed']['bodies']+exports['reference_bodies_not_in_STEP']
    files=list(OUT.glob('*.step'))+list((OUT/'subassemblies').glob('*.step'))
    assert len(files)==6
    for path in files:
        content=path.read_text(encoding='utf-8');assert content.startswith('ISO-10303-21;') and 'END-ISO-10303-21;' in content
    sources=['data/parameters.json','data/assembly_structure.json',baseline['source_archive'],
        'hardware/mechanical/assemblies.py','hardware/mechanical/prepare_assemblies_e07.py',
        'hardware/mechanical/organize_assemblies_e07.py','hardware/mechanical/verify_assemblies_e07.py',
        'hardware/mechanical/check_exports_e07.py','hardware/mechanical/capture_assemblies_e07.py',
        'tools/generate_assembly_bom.py','tools/check_assembly_outputs.py']
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    report=dict(status='passed',scope='Structure/BOM completeness, actual CAD verification records, STEP syntax and artifact hashes; not new physical validation',
        leaf_components=len(mapping),grouped_positions=len(grouped),source_sha256={s:digest(ROOT/s) for s in sources},
        output_sha256={str(p.relative_to(OUT)).replace('\\','/'):digest(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'})
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','leaves':len(mapping),'individual_modules':5,'STEP_files':len(files)}))
if __name__=='__main__':main()
