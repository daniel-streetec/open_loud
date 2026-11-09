"""Audit own ASCII DXF outlines, native archive and recorded STEP roundtrip."""
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/mechanical/exports/E03'


def read_dxf(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    assert len(lines)%2==0,path
    pairs=[(int(lines[i]),lines[i+1].strip()) for i in range(0,len(lines),2)]
    units=next(pairs[i+1][1] for i,p in enumerate(pairs) if p==(9,'$INSUNITS'))
    assert units=='4','DXF must declare millimetres'
    start=next(i for i,p in enumerate(pairs) if p==(2,'ENTITIES'))+1
    entities=[]
    for code,value in pairs[start:]:
        if code==0:
            if value=='ENDSEC':break
            entities.append({'type':value,'pairs':[]})
        else:entities[-1]['pairs'].append((code,value))
    points=[];circles=[];closed=0
    for e in entities:
        assert e['type'] in ('CIRCLE','LWPOLYLINE'),(path,e['type'])
        ps=e['pairs']
        def first(code):return next(float(v) for k,v in ps if k==code)
        if e['type']=='CIRCLE':
            x,y,r=first(10),first(20),first(40)
            assert r>0
            points += [(x-r,y-r),(x+r,y+r)]
            circles.append(2*r)
        else:
            assert int(first(70))&1,'Open cut contour'
            xs=[float(v) for k,v in ps if k==10];ys=[float(v) for k,v in ps if k==20]
            assert len(xs)==len(ys)>=4
            points += list(zip(xs,ys));closed+=1
    assert points
    size=[max(p[i] for p in points)-min(p[i] for p in points) for i in (0,1)]
    return dict(size_mm=size,circle_diameters_mm=sorted(circles),closed_polylines=closed)


def main():
    report=json.loads((OUT/'fusion_validation.json').read_text(encoding='utf-8'))
    roundtrip=json.loads((OUT/'step_roundtrip.json').read_text(encoding='utf-8'))
    assert roundtrip['status']=='passed'
    native=json.loads((OUT/'native_roundtrip.json').read_text(encoding='utf-8'))
    assert native['status']=='passed'
    assert not report['timeline_issues'] and not report['interferences']
    assert report['saved']
    data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    m={k:r['value'] for k,r in data['mechanical'].items() if isinstance(r,dict) and 'value' in r}
    metrics={};cutlist=[]
    for name in report['dxf_exports']:
        path=OUT/name
        metric=read_dxf(path);metrics[name]=metric
        if name.startswith('Rear_gasket_'):continue
        component=name.replace('_E03_DRAFT.dxf','')
        body=next(b for b in report['solid_bodies'] if b['component']==component)
        expected=sorted(body['size_mm'])[1:]
        assert all(abs(a-b)<.001 for a,b in zip(sorted(metric['size_mm']),expected)),(name,metric['size_mm'],expected)
        steel=component.startswith(('LF_steel_','Rear_thread_plate_'))
        cutlist.append({'component':component,'quantity':1,'material':'steel_candidate' if steel else 'birch_plywood_candidate',
                        'length_mm':max(expected),'width_mm':min(expected),'thickness_mm':min(body['size_mm']),
                        'volume_cm3':body['volume_cm3'],'status':'DRAFT_not_released','dxf':name})
    baffle=metrics['Baffle_E03_DRAFT.dxf']
    assert len(baffle['circle_diameters_mm'])==14,baffle
    assert baffle['closed_polylines']==2
    assert sum(abs(x-m['lf_bolt_clearance']*1000)<.001 for x in baffle['circle_diameters_mm'])==8
    assert sum(abs(x-m['horn_bolt_clearance']*1000)<.001 for x in baffle['circle_diameters_mm'])==4
    assert len(metrics['Rear_removable_E03_DRAFT.dxf']['circle_diameters_mm'])==10
    for name,metric in metrics.items():
        if name.startswith('Rear_thread_plate_'):assert len(metric['circle_diameters_mm'])==3
    archive=OUT/'OPEN_LOUD_A0_E03.f3d'
    assert zipfile.is_zipfile(archive)
    with zipfile.ZipFile(archive) as z:
        assert z.infolist(),'Empty native archive'
        compression_methods=sorted({i.compress_type for i in z.infolist()})
        supported={zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED,zipfile.ZIP_BZIP2,zipfile.ZIP_LZMA}
        crc_checked=all(method in supported for method in compression_methods)
        if crc_checked:assert z.testzip() is None
    step=(OUT/'OPEN_LOUD_A0_E03.step').read_text(encoding='utf-8')
    assert step.startswith('ISO-10303-21;') and 'END-ISO-10303-21;' in step
    with (OUT/'cutlist_DRAFT.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(cutlist[0]));writer.writeheader();writer.writerows(cutlist)
    sources=[ROOT/'data/parameters.json',ROOT/'tools/check_cad_exports.py',ROOT/'tools/fusion_bridge.py']
    sources+=list((ROOT/'hardware/mechanical').glob('*.py'))
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    output={'status':'passed','scope':'DXF units, closed contours, panel dimensions and mounting bores; F3D archive directory and actual Fusion native reimport; STEP syntax and actual Fusion reimport',
            'native_zip_compression_methods':compression_methods,'native_zip_crc_checked_by_python':crc_checked,
            'native_integrity_basis':'Actual Fusion import with parameter/body/timeline verification; Python ZIP CRC unavailable for unsupported compression methods',
            'dxf':metrics,'source_sha256':hashes,'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='cad_validation.json'}}
    (OUT/'cad_validation.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(f"CAD export audit passed: {len(metrics)} DXFs, {len(cutlist)} fabricated parts, F3D and STEP.")


if __name__=='__main__':main()
