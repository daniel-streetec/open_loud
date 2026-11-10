import json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'hardware/mechanical'))
from electronics import calculate
class ElectronicsMount(unittest.TestCase):
    def test_independent_thread_stacks_and_wood_counterpart(self):
        result=calculate(json.loads((R/'data/parameters.json').read_text(encoding='utf-8')))
        # 16-12-.5=3.5;6-2-.5=3.5;6-1.6-.5=3.9 mm.
        self.assertAlmostEqual(result['thread_engagement_m']['floor_bottom'],.0035)
        self.assertAlmostEqual(result['thread_engagement_m']['board_top'],.0039)
        self.assertTrue(all(v>=.003 for v in result['thread_engagement_m'].values()))
        self.assertAlmostEqual(result['screw_tip_gap_m']['board_pair'],.0026)
        self.assertEqual(len(result['support_centres_m']),4)
        self.assertEqual(len(result['pcb_hole_centres_m']),4)
        # At nominal3.6mm PCB holes, summed radial freedom0.8mm exceeds sqrt2*0.5mm.
        self.assertGreater(result['hole_pattern_tolerance_capacity_m'],2**.5*.0005)
