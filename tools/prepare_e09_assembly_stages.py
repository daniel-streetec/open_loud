"""Generate E09 assembly stage sources from own E08 maintenance mapping."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'hardware/mechanical'
s=(ROOT/'tools/prepare_assemblies_e08.py').read_text(encoding='utf-8').replace('E08','E09').replace('_e08','_e09')
s=s.replace('(front_wall|left_wall|roof)','(front_wall|left_wall|right_wall|roof|support_runner_[0-9]+)')
(ROOT/'tools/prepare_assemblies_e09.py').write_text(s,encoding='utf-8')
s=(M/'verify_assemblies_e08.py').read_text(encoding='utf-8').replace('E08','E09').replace('_e08','_e09')
(M/'verify_assemblies_e09.py').write_text(s,encoding='utf-8')
s=(ROOT/'tools/generate_modeled_bom_e08.py').read_text(encoding='utf-8').replace('exports/E08','exports/E09').replace('results/power/E08','results/power/E09').replace("revision='E08'","revision='E09'")
(ROOT/'tools/generate_modeled_bom_e09.py').write_text(s,encoding='utf-8')
s=(ROOT/'tools/draw_charge_bracket_e08.py').read_text(encoding='utf-8').replace('E08','E09').replace('_e08','_e09').replace('data/parameters.json','data/experiments/E09_parameters.json')
(ROOT/'tools/draw_charge_bracket_e09.py').write_text(s,encoding='utf-8')
