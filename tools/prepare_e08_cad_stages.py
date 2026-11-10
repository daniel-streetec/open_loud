"""Generate E08 stages from own proven native-feature builders, with explicit edits.
Only this authoring step generates scripts. Inputs remain data/parameters.json.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'hardware/mechanical'
def emit(name,source):
    (M/name).write_text(source,encoding='utf-8')
base=(M/'build_fusion_e03.py').read_text(encoding='utf-8').replace('E03','E08').replace('_Concept','_PowerSystem')
base=base.replace("name+'_cutout','width/2',y", "name+'_cutout','port_x' if name=='Port' else 'width/2',y")
base=base.replace("label+'_reinforcement_cutout','width/2',cy", "label+'_reinforcement_cutout','port_x' if label=='Port' else 'width/2',cy")
base=base.replace("'Port_relief','width/2','port_y'", "'Port_relief','port_x','port_y'")
base=base.replace("'Port_tube_profile','width/2','port_y'", "'Port_tube_profile','port_x','port_y'")
base=base.replace("    add('port_d',", "    add('battery_reserve',f'{layout[\"battery_excluded\"]*1e9:.12g} mm^3','mm^3','E08 sealed battery bay excluded envelope')\n    add('port_d',")
base=base.replace("'rear_fixing_displacement','target_net'", "'rear_fixing_displacement','battery_reserve','target_net'")
emit('build_case_e08.py',base)
rear=(M/'assemble_fusion_e03.py').read_text(encoding='utf-8').replace('E03','E08')
emit('assemble_rear_e08.py',rear)
fix=(M/'repair_cut_scope_e03.py').read_text(encoding='utf-8').replace("=='E03'","=='E08'")
emit('repair_cut_scope_e08.py',fix)
wiring=(M/'build_wiring_e05.py').read_text(encoding='utf-8')
start=wiring.index('    assert not any(d.name.startswith(')
end=wiring.index("    d=json.loads",start)
wiring=wiring[:start]+"    doc=app.activeDocument\n    assert doc and doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')\n    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent\n"+wiring[end:]
wiring=wiring.replace("OUT=ROOT/'hardware/mechanical/exports/E05'","OUT=ROOT/'hardware/mechanical/exports/E08'")
wiring=wiring.replace("root.attributes.add('OPEN_LOUD','revision','E05')","root.attributes.add('OPEN_LOUD','revision','E08')")
start=wiring.index("    for key,b in calc['branches'].items():")
end=wiring.index("    root.attributes.add('OPEN_LOUD','wiring_ready'",start)
wiring=wiring[:start]+"    # Cable bodies are added from the E08 complete harness, not the legacy reference.\n"+wiring[end:]
wiring=wiring.replace("(OUT/'build.json')", "(OUT/'fasteners_build.json')")
emit('add_fasteners_e08.py',wiring)
electronics=(M/'build_electronics_e06.py').read_text(encoding='utf-8')
start=electronics.index("    app=adsk.core.Application.get();target=")
end=electronics.index("    data=json.loads",start)
electronics=electronics[:start]+"    app=adsk.core.Application.get();doc=app.activeDocument\n    assert doc and doc.name.startswith('OPEN_LOUD_A0_E08_PowerSystem')\n    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=design.rootComponent\n"+electronics[end:]
electronics=electronics.replace("OUT=ROOT/'hardware/mechanical/exports/E06'", "OUT=ROOT/'hardware/mechanical/exports/E08'")
electronics=electronics.replace("root.attributes.add('OPEN_LOUD','revision','E06')","root.attributes.add('OPEN_LOUD','revision','E08')")
electronics=electronics.replace("(OUT/'build.json')", "(OUT/'electronics_build.json')")
electronics=electronics.replace('112x90x2','152x126x2').replace('OWN_AL_TRAY_112_90_2','OWN_AL_TRAY_152_126_2')
emit('add_electronics_e08.py',electronics)
print('Generated five E08 CAD stages plus cut-scope repair from own versioned builders.')
