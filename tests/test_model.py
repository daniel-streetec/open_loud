"""Analytical references independent of the box-network implementation."""
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulation"))
from model import values, response, port_geometry, constant_power_pack


class ReferenceCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / "data/parameters.json").read_text(encoding="utf-8"))
        cls.env = values(data["environment"])
        cls.model = values(data["model"])
        cls.driver = values(data["drivers"]["10FE200-4"])
        cls.case = values(data["concepts"]["A0"])

    def test_sealed_second_order_closed_form(self):
        """Pressure shape equals classic sealed-box high-pass transfer function."""
        d, e, b = self.driver, self.env, self.case
        ws = 2 * math.pi * d["Fs"]
        cms = 1 / (ws ** 2 * d["Mms"])
        vas = e["rho"] * e["c"] ** 2 * d["Sd"] ** 2 * cms
        wc = ws * math.sqrt(1 + vas / b["Vb"])
        qc = wc * d["Mms"] / (d["Rms"] + d["Bl"] ** 2 / d["Re"])
        asymptote = e["rho"] * d["Sd"] * d["Bl"] / (2 * math.pi * e["distance"] * d["Re"] * d["Mms"])
        for frequency in (10, 30, 60, 100, 200, 1000):
            w = 2 * math.pi * frequency
            expected = asymptote * (-w ** 2) / (wc ** 2 - w ** 2 + 1j * w * wc / qc)
            actual = response(frequency, d, b, e, self.model, sealed=True)["pressure"]
            self.assertLess(abs(actual - expected) / abs(expected), 1e-12)

    def test_helmholtz_frequency_from_length(self):
        length, _ = port_geometry(self.case, self.env, self.model)
        independently = self.env["c"] / (2 * math.pi) * math.sqrt(self.case["port_area"] / (self.case["Vb"] * length))
        self.assertAlmostEqual(independently, self.case["Fb"], places=11)

    def test_electromechanical_power_conservation(self):
        """Re(I*) = copper + suspension + port resistance + enclosure leakage."""
        d, e, b, m = self.driver, self.env, self.case, self.model
        cab = b["Vb"] / (e["rho"] * e["c"] ** 2)
        wb = 2 * math.pi * b["Fb"]
        port_mass = 1 / (wb ** 2 * cab)
        for frequency in (20, 30, 50, 63, 100, 250):
            r = response(frequency, d, b, e, m)
            port_loss = abs(r["port_flow"]) ** 2 * port_mass * wb / m["qp"]
            w = 2 * math.pi * frequency
            zp = port_mass * (wb / m["qp"] + 1j * w)
            box_pressure = -r["port_flow"] * zp
            leak_loss = abs(box_pressure) ** 2 * wb * cab / m["ql"]
            dissipated = r["power_copper"] + d["Rms"] * abs(r["velocity"]) ** 2 + port_loss + leak_loss
            self.assertAlmostEqual(r["power_real"], dissipated, places=12)

    def test_distance_reference(self):
        r1 = response(50, self.driver, self.case, self.env, self.model)
        r2 = response(50, self.driver, self.case, dict(self.env, distance=2), self.model)
        self.assertAlmostEqual(r1["spl_1V"] - r2["spl_1V"], 6.020599913, places=8)

    def test_pack_resistive_reference_and_collapse(self):
        # Known 3 A operating point: 18V OCV - 3A*0.2ohm = 17.4V; P=52.2W.
        v, i = constant_power_pack(18, 0.2, 52.2)
        self.assertAlmostEqual(v, 17.4)
        self.assertAlmostEqual(i, 3)
        self.assertIsNone(constant_power_pack(10, 1, 26))
        self.assertEqual(constant_power_pack(18, 0, 36), (18, 2))


if __name__ == "__main__":
    unittest.main()
