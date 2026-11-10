import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from assemblies import classify
class AssemblyOwnership(unittest.TestCase):
    def setUp(self):self.s=json.loads((ROOT/'data/assembly_structure.json').read_text(encoding='utf-8'))
    def test_maintenance_boundary_keeps_counterparts_on_cabinet(self):
        self.assertIn('Feste_Rueckwandgewinde',classify('E05_Rear_0_retainer_1',self.s))
        self.assertEqual(classify('E05_Rear_0_M5x40',self.s),'BG30_Service_Rueckwand')
        self.assertIn('Elektronikstuetzen',classify('E06_floor_bottom_M3x16_0',self.s))
        self.assertIn('BG41_Traeger',classify('E06_tray_top_M3x6_0',self.s))
    def test_glands_are_not_misclassified_as_loudspeaker_hardware(self):
        self.assertIn('Kabeldurchfuehrungen',classify('E05_LF_M16_gland',self.s))
        self.assertIn('Tieftoener',classify('E05_LF_0_M5x45',self.s))
        self.assertIn('Hochton',classify('E05_HF_-1_1_M4x40',self.s))
        with self.assertRaises(ValueError):classify('unknown_new_part',self.s)
