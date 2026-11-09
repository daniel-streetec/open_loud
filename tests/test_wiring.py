import copy,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from generate_wiring import calculate

class WiringReferences(unittest.TestCase):
    def setUp(self):self.data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    def test_one_metre_pair_reference(self):
        d=copy.deepcopy(self.data)
        for k in ('power','lf','hf'):d['wiring'][k+'_route']['value']=[[0,0,0],[1,0,0]]
        for k in ('service_allowance','termination_allowance','temperature_rise_from_20','pigtail_length','dc_contact_budget','speaker_contact_budget'):d['wiring'][k]['value']=0
        r=calculate(d)
        # Independent reference: two 1m conductors, each manufacturer 13.3 milliohm.
        self.assertAlmostEqual(r['branches']['power']['total_loop_R60_ohm'],.0266)
        self.assertAlmostEqual(r['branches']['power']['drop_V'],.1596)
    def test_hot_load_budget_and_cut_allowance(self):
        r=calculate(self.data)
        self.assertTrue(all(b['drop_pass'] for b in r['branches'].values()))
        self.assertGreaterEqual(6,max(x['dc_A'] for x in r['loads'])*1.24)
        self.assertGreater(r['gland_thread_margin_m'],.001)
        for b in r['branches'].values():
            self.assertGreaterEqual(b['cut_length_m'],b['route_length_m']+.159999)
            self.assertLessEqual(b['min_area_heat_proxy_mm2'],b['conductor_mm2'])
    def test_double_length_doubles_wire_loss(self):
        d=copy.deepcopy(self.data)
        for k in ('service_allowance','termination_allowance'):d['wiring'][k]['value']=0
        d['wiring']['power_route']['value']=[[0,0,0],[.5,0,0]]
        a=calculate(d)['branches']['power']
        d['wiring']['power_route']['value']=[[0,0,0],[1,0,0]]
        b=calculate(d)['branches']['power']
        self.assertAlmostEqual(b['cable_loss_W'],2*a['cable_loss_W'])
