"""Run explicitly named Fusion stages sequentially; stop and record any real failure."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGES={
 'rear':'assemble_rear_e09.py','fasteners':'add_fasteners_e09.py','power':'add_power_e09.py',
 'electronics':'add_electronics_e09.py','charge':'add_charge_bracket_e09.py','orion':'refine_orion_mount_e09.py',
 'harness':'add_harness_e09.py','verify':'verify_power_e09.py','service':'check_battery_service_e09.py',
 'inventory':'inventory_mass_e09.py','view':'view_power_e09.py','exports':'check_exports_e09.py'}
STAGES.update(charge_refined='add_charge_bracket_e09.py',routes_refined='refine_routes_e09.py',verify_refined='verify_power_e09.py',service_refined='check_battery_service_e09.py',inventory_refined='inventory_mass_e09.py',view_refined='view_power_e09.py',exports_refined='check_exports_e09.py')
STAGES.update(charge_service='add_charge_bracket_e09.py',envelope='check_battery_envelope_e09.py',verify_service='verify_power_e09.py',inventory_service='inventory_mass_e09.py',assemblies_service='verify_assemblies_e09.py',view_service='view_power_e09.py',exports_service='check_exports_e09.py')
if __name__=='__main__':
    selected=sys.argv[1:];assert selected and all(n in STAGES for n in selected)
    out=ROOT/'hardware/mechanical/exports/E09';out.mkdir(exist_ok=True);log=out/'stage_run.json'
    history=json.loads(log.read_text()) if log.exists() else []
    for name in selected:
        assert not any(r['stage']==name and r['status']=='passed' for r in history),f'{name} previously executed; inspect model before another mutation'
        script='hardware/mechanical/'+STAGES[name]
        result=subprocess.run([sys.executable,'-B','tools/fusion_bridge.py','run',script],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        tool_returncode=result.returncode
        findings=None
        if result.returncode==0 and name.startswith('verify'):
            actual=json.loads((out/'power_validation.json').read_text(encoding='utf-8'))
            findings={k:len(actual[k]) for k in ('interferences','kernel_failures','timeline_issues')}
            if any(findings.values()):result.returncode=2
        (ROOT/'.tools'/f'E09_stage_{name}.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        record=dict(stage=name,script=script,status='passed' if result.returncode==0 else 'failed',returncode=result.returncode,scope='Tool execution only; actual geometric and service findings are in separate validation reports')
        record['tool_returncode']=tool_returncode
        if findings is not None:record['geometric_quality_counts']=findings
        if result.returncode:record['error_tail']=(result.stdout+result.stderr)[-1500:]
        history.append(record);log.write_text(json.dumps(history,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(record),flush=True)
        if result.returncode:raise SystemExit(result.returncode)
