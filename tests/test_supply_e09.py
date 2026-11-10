"""Independent energy balance across both resistive wiring segments and converter."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from calculate_supply_e09 import calculate
class SupplyBalance(unittest.TestCase):
    def test_conservation_with_both_wire_losses(self):
        d=json.loads((ROOT/'data/experiments/E09_parameters.json').read_text(encoding='utf-8'))
        report=calculate(d)
        for c in report['scenarios']:
            self.assertAlmostEqual(c['converter_output_W'],c['amplifier_input_W']+c['output_wire_loss_W'],places=9)
            self.assertAlmostEqual(c['battery_W'],c['converter_output_W']+c['estimated_converter_heat_W']+c['input_wire_and_planned_protector_loss_W'],places=9)
            self.assertLess(c['board_terminal_V'],d['power_system']['converter_output']['value'])
            self.assertLess(c['converter_input_V'],c['battery_terminal_V'])
