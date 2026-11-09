"""One-shot authoring helper; versioned JSON is the input after initialization."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'data/parameters.json';d=json.loads(p.read_text(encoding='utf-8'))
def record(value,unit,source,status='design_assumption',uncertainty=None):
    return dict(value=value,unit=unit,source=source,status=status,uncertainty=uncertainty)
d['revision']='E05'
d['wiring']={
 'supply_min':record(15,'V','A0: 5S design window; pack UVLO not verified'),
 'supply_max':record(21,'V','5S Li-ion 4.2 V/cell assumption'),
 'amplifier_efficiency_low':record(.65,'1','conservative planning assumption; manufacturer 83% at different test point'),
 'amplifier_idle':record(1.8,'W','WONDOM AA-JA32173 manufacturer data PDF','manufacturer_reference'),
 'rail_fraction':record(.9,'1','simulation/model.py voltage-headroom assumption'),
 'hf_voltage_limit':record(12.6491106407,'V_rms','sqrt(20 W * 8 ohm); DSP setting NOT implemented'),
 'dc_design_current':record(6,'A','rounded 25% reserve over simultaneous sine-load screening'),
 'dc_short_test_current':record(10,'A','inrush test scenario ONLY; no measured inrush'),
 'lf_design_current':record(4,'A_rms','13.365 Vrms / 3.6 ohm min plus reserve'),
 'hf_design_current':record(2.1,'A_rms','12.649 Vrms / 6.3 ohm min plus reserve'),
 'conductor_area':record(1.5,'mm2','Cordial CLS215 manufacturer','manufacturer_reference'),
 'conductor_resistance':record(.0133,'ohm/m','Cordial CLS215 manufacturer at nominal reference temperature','manufacturer_reference'),
 'copper_alpha':record(.00393,'1/K','copper linear temperature approximation'),
 'temperature_rise_from_20':record(40,'K','60 C conductor screening, not measured'),
 'cable_diameter':record(.007,'m','Cordial CLS215 manufacturer nominal','manufacturer_reference'),
 'cable_mass':record(.079,'kg/m','Cordial CLS215 manufacturer','manufacturer_reference'),
 'bend_radius':record(.028,'m','4x nominal OD static planning rule; vendor minimum unknown'),
 'service_allowance':record(.10,'m','removable service loop; accommodated in dry bay, final dressing at mock-up'),
 'termination_allowance':record(.06,'m','both ends combined; spare jacket/stripping allowance'),
 'pigtail_length':record(.10,'m','each branch factory cable assumed 100 mm; MEASURE before release'),
 'pigtail_min_area':record(.326,'mm2','AWG22 worst-case planning hypothesis, not board cable specification'),
 'dc_contact_budget':record(.030,'ohm','combined fuse, holder, switch, adapter, terminals acceptance budget'),
 'speaker_contact_budget':record(.010,'ohm','combined OEM connector, WAGO, driver terminals acceptance budget'),
 'loop_heat_budget':record(1.2,'W/m','design screening proxy; not an ampacity standard'),
 'lf_route':record([[.230,.425,.240],[.275,.425,.240],[.275,.310,.240],[.275,.310,.145],[.225,.280,.115]],'m','E05 rear service bay to LF terminal reserve; actual terminal endpoint unverified'),
 'hf_route':record([[.230,.460,.240],[.275,.460,.240],[.275,.460,.145],[.225,.470,.145]],'m','E05 partition feedthrough to HF terminal reserve; endpoint unverified'),
 'power_route':record([[.285,.385,.250],[.285,.425,.250],[.230,.425,.250]],'m','E05 provisional battery-adapter station to amplifier; pack mount absent'),
 'gland_thread_length':record(.012,'m','LAPP 53017210 manufacturer datasheet','manufacturer_reference'),
 'gland_clamp_min':record(.0035,'m','LAPP 53017210 manufacturer datasheet','manufacturer_reference'),
 'gland_clamp_max':record(.008,'m','LAPP 53017210 manufacturer datasheet','manufacturer_reference'),
 'gland_nut_thickness_reserve':record(.003,'m','counter-nut reserved thickness; actual PN to verify'),
 'gland_seal_thickness':record(.0005,'m','compressed panel seal planning hypothesis'),
 'gland_counterbore_depth':record(.005,'m','internal relief in 12 mm panel leaves 7 mm wood'),
 'gland_bore':record(.0165,'m','M16 clearance design'),
 'gland_counterbore_diameter':record(.028,'m','socket/locknut installation reserve; actual nut verify'),
}
d['fasteners']={
 'm5_head_d':record(.0085,'m','Bossard/Bollhoff ISO4762 technical table','manufacturer_reference'),
 'm5_head_h':record(.005,'m','Bossard/Bollhoff ISO4762 technical table','manufacturer_reference'),
 'm4_head_d':record(.007,'m','ISO4762 nominal design; verify purchased SKU'),
 'm4_head_h':record(.004,'m','ISO4762 nominal design; verify purchased SKU'),
 'lf_screw_length':record(.045,'m','E05 stack: 8+24+3+2x1+4.7 mm =41.7 mm; 3.3 mm protrusion'),
 'horn_screw_length':record(.040,'m','E05 stack: 5.5+24+2x0.8+3.2 mm=34.3 mm'),
 'rear_screw_length':record(.040,'m','E05 stack washer1+panel12+cleat20+plate5=38 mm'),
 'm5_nut_h':record(.0047,'m','ISO4032 nominal envelope; SKU verification pending'),
 'm4_nut_h':record(.0032,'m','DIN934 nominal envelope; SKU verification pending'),
 'm5_washer_h':record(.001,'m','ISO7089 nominal envelope'),
 'm4_washer_h':record(.0008,'m','ISO7089 nominal envelope'),
}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
