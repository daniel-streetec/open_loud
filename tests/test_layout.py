import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/mechanical'))
from layout import calculate


class MechanicalBudget(unittest.TestCase):
    def test_net_air_budget_and_fastener_lands(self):
        data=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
        result=calculate(data);m=result['dimensions']
        excluded=sum(result[k] for k in ('service_excluded','port_displacement','reinforcement_displacement','cleat_acoustic_displacement','backing_displacement','hf_displacement','brace_displacement','rear_fixing_displacement'))
        excluded+=data['drivers']['10FE200-4']['displacement']['value']+m['horn_displacement']
        self.assertAlmostEqual(result['gross_internal']-excluded,.034,places=12)
        # Independent layout checks: wood webs between actual aperture edges.
        lf_radius=(m['lf_cutout']+2*m['baffle_clearance'])/2
        port_radius=(result['port_d']+2*m['port_wall']+2*m['baffle_clearance'])/2
        self.assertGreater(m['lf_y']-lf_radius-m['port_y']-port_radius,.020)
        self.assertGreater(m['horn_y']-m['horn_cutout']/2-m['lf_y']-lf_radius,.020)
        # Steel ring supports the M5 holes with a larger edge ligament than the wood cutout.
        self.assertGreater(m['lf_pcd']/2-m['lf_backing_inner_d']/2-m['lf_bolt_clearance']/2,.006)
        # Rear-cover cleats leave a real bearing land around each 5.5mm clearance bore.
        self.assertGreater((m['rear_cleat_width']-m['rear_bolt_clearance'])/2,.007)
