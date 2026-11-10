"""One-time concrete routing inputs for the selected complete power chain."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/parameters.json';d=json.loads(p.read_text(encoding='utf-8'))
assert 'harness_e08' not in d
def r(v,u,s,status='design_assumption',uncertainty=None):return dict(value=v,unit=u,source=s,status=status,uncertainty=uncertainty)
d['harness_e08']={
 'main_od':r(.0048,'m','H07V-K4mm2 single insulated wire conservative OD; actual selected SKU measure'),
 'main_bend':r(.020,'m','4xOD static planning bound; verify selected H07V-K datasheet'),
 'speaker_od':r(.007,'m','Cordial CLS215 nominal, manufacturing OD tolerance verify','manufacturer_reference'),
 'speaker_bend':r(.035,'m','5x7mm static planning; compare current CLS215 manufacturer PDF'),
 'main_area':r(4,'mm2','E08 power input4mm2, converter accepts<=6mm2'),
 'main_r20':r(.00495,'ohm/m','IEC60228-class5 planning upper resistance; verify purchased wire'),
 'speaker_r20':r(.0133,'ohm/m','Cordial CLS215 manufacturer','manufacturer_reference'),
 'temperature_delta':r(40,'K','60C conductor screening vs20C resistance reference'),
 'copper_alpha':r(.00393,'1/K','copper approximation'),
 'contact_budget':r(.010,'ohm','main pair combined measured acceptance allowance, including fuse'),
 'speaker_contact_budget':r(.010,'ohm','combined pigtail/terminal acceptance budget'),
 'main_plus_route':r([[.232,.204,.315],[.232,.390,.315],[.232,.390,.245]],'m','E08 after F1 through rear roof/floor glands to VIN+ station; actual converter terminal entry verify'),
 'main_minus_route':r([[.260,.196,.288],[.260,.196,.315],[.260,.390,.315],[.260,.390,.245]],'m','E08 negative to VIN-; first short bend replaced by loose insulated lead if geometric min-radius fails'),
 'output_route':r([[.286,.400,.250],[.286,.400,.310],[.180,.400,.310]],'m','converter OUT to power WAGO station; bare insulated tails complete actual connectors'),
 'lf_route':r([[.050,.420,.275],[.275,.420,.275],[.275,.285,.275],[.275,.285,.140],[.235,.280,.110]],'m','WAGO LF station through floor M16 to LF terminal reserve'),
 'hf_route':r([[.050,.400,.305],[.170,.400,.305],[.170,.500,.305],[.170,.500,.130],[.240,.470,.130]],'m','WAGO HF station through partition M16 to HF terminal reserve'),
 'tail_allowance':r(.160,'m','two insulated tails80mm each; actual pigtail/terminal lengths measure'),
 'service_allowance':r(.100,'m','dry-bay service reserve; loop dressing checked separately'),
 'charge_route':r([[.303,.195,.316],[.280,.195,.316],[.280,.196,.288]],'m','short jacket-free internal charging leads to F2 and battery; no external cabinet hole'),
 'charge_area':r(1.5,'mm2','5A external charging branch'),
 'remote_area':r(.25,'mm2','low-current dry-contact control, not battery load switching'),
}
d['wiring_reference_status']='wiring group is legacy E05 screening only; E08 uses power_system and harness_e08'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
