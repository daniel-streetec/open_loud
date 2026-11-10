"""Promote derived numeric facts, never supplier solids, from local inspection."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'.tools/orion_inspection.json').read_text(encoding='utf-8'))
assert r['sha256']=='cc9bc9940f969d7af3b24d411727f16d678f2b6408672059060d990c2a288598','Manufacturer file changed; review nominal geometry before promoting facts'
assert len(r['mounting_cylinders'])==4 and len(r['mount_tool_access'])==4
assert all(not a['overlaps_cm3'] for a in r['mount_tool_access'])
thicknesses=[(h['max_cm'][1]-h['min_cm'][1])*.01 for h in r['mounting_cylinders']]
assert max(abs(t-.002) for t in thicknesses)<1e-8
out=ROOT/'data/verification';out.mkdir(exist_ok=True)
report=dict(source_url=r['source_url'],source_sha256=r['sha256'],date='2026-11-10',
    ear_thickness_m=thicknesses,mount_access_radius_m=.004,access_from_ear_base_m=.0020001,access_to_m=.015,
    access_overlap_cm3=[a['overlaps_cm3'] for a in r['mount_tool_access']],
    scope='Own measured numeric facts from nominal manufacturer STEP, not a physical sample; vendor solids excluded')
(out/'orion_mount.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
p=ROOT/'data/parameters.json';d=json.loads(p.read_text(encoding='utf-8'))
def rec(value,unit,status='manufacturer_CAD_verified'):
    return dict(value=value,unit=unit,source='data/verification/orion_mount.json',status=status,uncertainty=None)
d['orion_mount_e08']={
    'ear_thickness':rec(.002,'m'),'hole_pitch':rec([.0988,.0842],'m'),
    'hole_diameter':rec(.0038,'m'),'verified_access_radius':rec(.004,'m'),
    'verified_access_depth':rec(.015,'m'),
    'depth_keepout':rec(.0475,'m','conservative_round_up_of_official_STEP_47p34mm_bounds'),
}
d['orion_mount_e08']['mass']=dict(value=.42,unit='kg',source='https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-DC-DC-converters-isolated-100-250-400W-EN.pdf',status='manufacturer_nominal',uncertainty=None)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
