"""Continuous straight service sweep of a conservative rectangular battery envelope.
For an axis-aligned box translated alongZ, its swept union is another exact box.
No actual battery terminals, deformation, wire disconnection or human access certified.
"""
import adsk.core,adsk.fusion,json,sys,importlib
from pathlib import Path
ROOT=Path(r'C:\Repositories\open_loud');sys.path.insert(0,str(ROOT/'hardware/mechanical'))
import cad_parts;importlib.reload(cad_parts)
def run(_context: str):
    app=adsk.core.Application.get();doc=app.activeDocument
    assert doc.name.startswith('OPEN_LOUD_A0_E09_PowerSystem')
    d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));F=cad_parts.Parts(d.rootComponent);tm=F.tm
    data=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'))
    study=json.loads((ROOT/'data/experiments/E09_packaging.json').read_text(encoding='utf-8'))
    p={k:r['value'] for k,r in data['battery_mount'].items()};tol=study['planning_tolerance_each_face_m'];terminal=study['terminal_zone_height_m']
    origin=[v-tol for v in p['battery_origin']];size=[v+2*tol for v in p['battery_size']]
    # The supported lower face is a seating datum, not a free ± tolerance face.
    # Carry the pad with the battery; it need not be pulled from under a loaded pack.
    origin[1]=p['battery_origin'][1]-p['pad'];size[1]=p['battery_size'][1]+p['pad']+terminal+tol
    travel=data['mechanical']['depth']['value']-origin[2]+study['exit_clearance_m'];size[2]+=travel
    swept=F.box(origin,size);aa=swept.boundingBox;hits=[];count=0
    for o in d.rootComponent.allOccurrences:
        name=o.component.name
        if name=='E09_Battery_EREMIT_50Ah_BMS':continue
        if any(s in o.fullPathName for s in ('BG30_Service_Rueckwand','BG62_Akkuhalterung','BG90_Referenzraeume','BG80_Externes_Ladegeraet')):continue
        # This test is run after hierarchy creation; refuse a flat scene that would retain its service cover.
        assert any(q.component.name=='BG60_Akkuversorgung' for q in d.rootComponent.occurrences),'Structured E09 required'
        for b in o.component.bRepBodies:
            if not b.isLightBulbOn:continue
            fixed=tm.copy(b);assert tm.transform(fixed,o.transform2);bb=fixed.boundingBox;count+=1
            if not all(aa.maxPoint.asArray()[i]>bb.minPoint.asArray()[i]+1e-6 and bb.maxPoint.asArray()[i]>aa.minPoint.asArray()[i]+1e-6 for i in range(3)):continue
            clone=tm.copy(swept);assert tm.booleanOperation(clone,fixed,adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if clone.isValid and clone.faces.count and clone.volume>1e-5:hits.append(dict(part=name,overlap_cm3=clone.volume))
    report=dict(status='passed_for_assumed_envelope' if not hits else 'blocked',method='Exact rectangular swept union along+Z, kernel intersection with fixed model solids',
        travel_m=travel,case_free_face_tolerance_m=tol,lower_face='seated pad bottom datum; no negative seating tolerance',additional_top_terminal_zone_m=terminal,swept_origin_m=origin,swept_size_m=size,
        fixed_bodies_screened=count,hits=hits,
        removed_for_service=['Rear cover and screws','Straps released','Battery leads disconnected; service disconnect not yet selected'],pad='included in moving envelope',
        limitations=['Exact sweep applies to this assumed box and path, not a measured real battery assembly.',
        'Holder envelopes, real post positions, hand/tool access and unmodeled connectors/anchors still need qualification.'])
    out=ROOT/'hardware/mechanical/exports/E09';(out/'battery_continuous_envelope.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'travel_mm':travel*1000,'hits':len(hits),'fixed_bodies':count}));assert not hits
