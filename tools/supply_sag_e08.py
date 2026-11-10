"""Constant-power source sag sensitivity; pack resistance is unknown, not measured."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def solve(voc,watts,resistance):
    disc=voc*voc-4*resistance*watts
    if disc<0:return None
    volts=(voc+math.sqrt(disc))/2
    return dict(load_V=volts,current_A=watts/volts,loss_W=(watts/volts)**2*resistance)
if __name__=='__main__':
    h=json.loads((ROOT/'results/power/E08/harness.json').read_text())
    b=json.loads((ROOT/'results/power/E08/budget.json').read_text())
    wire=h['main_at_12A']['loop_resistance_60C_ohm']
    watts=b['amplifier_worst_case_input_W']/.8
    rows=[]
    for voc in (10,11,12.8,14.6):
        for pack_r in (.01,.03,.06):
            result=solve(voc,watts,wire+pack_r)
            rows.append(dict(open_circuit_V=voc,assumed_pack_BMS_resistance_ohm=pack_r,
                result=result,below_10V_terminal_cutoff=result is None or result['load_V']<10))
    out=dict(status='sensitivity_only_pack_BMS_resistance_unknown',load_W=watts,
        harness_loop_ohm=wire,scenarios=rows,
        limitations=['10/30/60 milliohm pack values are hypothetical sensitivity cases, not EREMIT specifications.',
        'Pack BMS cutoff senses internal cells, not converter terminals; terminal threshold is a conservative screen.',
        'Measure pack/BMS DC resistance at state of charge and temperature; do not infer capacity from these scenarios.'])
    (ROOT/'results/power/E08/sag.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(scenarios=len(rows),harness_loop_ohm=wire)))
