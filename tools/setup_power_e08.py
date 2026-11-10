"""One-time migration to selected LFP/converter architecture; don't overwrite edits."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'data/parameters.json';d=json.loads(path.read_text(encoding='utf-8'))
assert 'power_system' not in d,'Already migrated; edit central inputs directly'
archive=ROOT/'data/experiments/E07_parameters.json';assert not archive.exists();archive.write_bytes(path.read_bytes())
def r(value,unit,source,status='design_assumption',uncertainty=None):return dict(value=value,unit=unit,source=source,status=status,uncertainty=uncertainty)
d['revision']='E08'
for k,v in dict(width=.360,depth=.340,service_floor_y=.330,port_y=.082,brace_y=.240).items():
    d['mechanical'][k].update(value=v,source='E08 internal50Ah battery, clear port channel and34L target; user allows quality/weight trade',status='design_candidate')
d['mechanical']['port_x']=r(.080,'m','E08 left acoustic channel beside sealed rear-right battery bay')
d['battery_mount']={
 'bay_left':r(.132,'m','E08 sealed corner bay outer boundary; 120mm-wide acoustic channel remains left'),
 'bay_front':r(.170,'m','E08 outer front face of rear battery bay'),
 'bay_top':r(.220,'m','E08 outer top of battery bay'),
 'battery_origin':r([.147,.018,.190],'m','E08 nominal upright box;6mm right/8mm rear gap, terminal cover allowance above'),
 'battery_size':r([.195,.170,.130],'m','EREMIT50Ah Gen7 BASIS technical dimensions; own box reference','manufacturer_reference',{'absolute':.002,'note':'planning reserve, vendor tolerance not specified'}),
 'battery_mass':r(4.9,'kg','EREMIT50Ah Gen7 BASIS product specification','manufacturer_reference'),
 'terminal_zone_height':r(.014,'m','Reserved M6 terminal/lug/cover space; actual terminal positions to confirm'),
 'pad':r(.003,'m','closed-cell elastomer candidate, material/compression test pending'),
 'strap_width':r(.025,'m','standard25mm cam buckle strap candidate'),
 'converter_origin':r([.200,.400,.238],'m','E08 upright isolated converter beside amplifier tray; terminals down'),
 'converter_size':r([.114,.1002,.0468],'m','Victron Orion-small Rev01 dimension drawing','manufacturer_reference'),
}
d['power_system']={
 'battery_nominal':r(12.8,'V','EREMIT50Ah Gen7 BASIS','manufacturer_reference'),
 'battery_full':r(14.6,'V','EREMIT50Ah Gen7 BASIS','manufacturer_reference'),
 'battery_cutoff':r(10,'V','EREMIT50Ah Gen7 BASIS BMS, not a user-adjusted threshold','manufacturer_reference'),
 'battery_capacity':r(50,'Ah','EREMIT50Ah Gen7 BASIS','manufacturer_reference'),
 'usable_fraction_low':r(.75,'1','cold/age/reserve planning scenario, not measured'),
 'usable_fraction_high':r(.90,'1','warm/new battery planning scenario, not measured'),
 'converter_output':r(20,'V','Selected Orion12/24-5 adjustment18-30V; set and verify before amplifier connection','design_selection'),
 'converter_efficiency_low':r(.80,'1','derated planning lower bound; nominal manufacturer88%'),
 'converter_efficiency_high':r(.88,'1','Victron Orion12/24-5 nominal efficiency','manufacturer_reference'),
 'converter_output_current':r(5,'A','Victron Orion12/24-5 continuous; output20V -> conservatively100W','manufacturer_reference'),
 'converter_idle_current_max':r(.080,'A','Victron Orion12/24-5 no-load input current','manufacturer_reference'),
 'converter_disabled_current_max':r(.0002,'A','Victron Orion12/24-5 remote disabled','manufacturer_reference'),
 'amplifier_idle':r(1.8,'W','WONDOM AA-JA32173 datasheet','manufacturer_reference'),
 'amplifier_efficiency_low':r(.65,'1','conservative E05 planning assumption'),
 'lf_limit':r(12,'V_rms','DSP target; not hardware deployed or gain-calibrated'),
 'hf_limit':r(10,'V_rms','DSP target; not hardware deployed or gain-calibrated'),
 'charger_voltage':r(14.6,'V','EREMIT external12V5A LiFePO4 charger; verify variant output before use','manufacturer_reference'),
 'charger_current':r(5,'A','EREMIT external12V5A LiFePO4 charger','manufacturer_reference'),
 'main_design_current':r(12,'A','power budget over10V battery minimum with efficiency reserve'),
 'main_conductor':r(4,'mm2','H07V-K OFC; fits converter6mm2 maximum; no factory-contact assumption'),
 'main_fuse':r(15,'A','ATO287 candidate; inrush/I2t/short-circuit coordination pending'),
 'charge_fuse':r(7.5,'A','ATO287 candidate for5A charger; holder and actual lead qualification pending'),
 'output_fuse':r(5,'A','ATO287 candidate for converter-to-JAB branch, inrush test pending'),
 'remote_switch_current':r(.010,'A','low-current control planning bound; manufacturer interface current verify'),
}
d['electronics_mount']['tray_origin']['value']=[.040,.352,.220]
d['electronics_mount']['tray_origin']['source']='E08 new service floor330mm,10mm supports; clear partition and rear cleats'
path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('E08 central inputs selected; E07 input snapshot preserved.')
