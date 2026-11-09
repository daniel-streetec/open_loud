import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from integration import calculate,rounded_route

class IntegrationReferences(unittest.TestCase):
    def test_quarter_circle_fillet(self):
        samples,length=rounded_route([[0,0,0],[1,0,0],[1,1,0]],.1)
        self.assertAlmostEqual(length,1.8+math.pi*.1/2)
        self.assertEqual(samples[0],[0,0,0])
        self.assertEqual(samples[-1],[1,1,0])

    def test_rejected_study_analytical_checks_only(self):
        d=json.loads((ROOT/'data/experiments/e04_rejected_parameters.json').read_text(encoding='utf-8'))
        result=calculate(d)
        self.assertFalse(result['standard_gland_direct_12mm_wood_fits'])
        self.assertGreaterEqual(result['gland_thread_margin_m'],.0009)
        self.assertGreaterEqual(result['ring_clearance_conservative_m'],result['ring_required_m'])
        self.assertGreaterEqual(result['hood_bottom_free_m2'],result['port_area_m2'])
        self.assertGreaterEqual(result['mesh_open_fraction_ideal'],.60)
        self.assertGreaterEqual(result['rear_guard_panel_edge_clearance_m'],.002)
