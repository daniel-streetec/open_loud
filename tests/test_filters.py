"""Independent closed-form bilinear Butterworth and LR sum references."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'simulation'))
from filters import lr4,butterworth4_highpass,cascade
class FilterReferences(unittest.TestCase):
    def test_butterworth4_matches_prewarped_closed_form(self):
        fs=48000;fc=45;sections=butterworth4_highpass(fc,fs)
        for f in (10,20,40,45,50,100,1000,10000):
            ratio=math.tan(math.pi*f/fs)/math.tan(math.pi*fc/fs)
            reference=1/math.sqrt(1+ratio**-8)
            self.assertAlmostEqual(abs(cascade(sections,f,fs)),reference,places=9)
    def test_lr4_complex_sum_is_allpass_without_driver_delay(self):
        fs=48000;fc=2500;lp=lr4('lp',fc,fs);hp=lr4('hp',fc,fs)
        for f in (20,500,1250,2500,5000,10000,20000):
            self.assertAlmostEqual(abs(cascade(lp,f,fs)+cascade(hp,f,fs)),1,places=12)
        self.assertAlmostEqual(abs(cascade(lp,fc,fs)),.5,places=12)
        self.assertAlmostEqual(abs(cascade(hp,fc,fs)),.5,places=12)
