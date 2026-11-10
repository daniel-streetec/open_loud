import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from calculate_power_e08 import calculate
class SelectedSupply(unittest.TestCase):
    def test_independent_energy_and_power_capacity(self):
        r=calculate(json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8')))
        self.assertAlmostEqual(r['battery_nominal_Wh'],640)
        self.assertAlmostEqual(r['limited_sine_audio_W'],48.5)
        self.assertLess(r['amplifier_worst_case_input_W'],100)
        self.assertLess(max(s['battery_A'] for s in r['scenarios']),12)
        self.assertEqual(r['charger_ideal_CC_h'],10)
