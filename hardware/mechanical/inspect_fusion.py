import adsk.core, adsk.fusion, json

def run(_context: str):
    app=adsk.core.Application.get()
    d=adsk.fusion.Design.cast(app.activeProduct)
    print(json.dumps({'document':app.activeDocument.name,'components':[{'name':o.component.name,'bodies':o.component.bRepBodies.count,'sketches':[{'name':s.name,'fully_constrained':s.isFullyConstrained} for s in o.component.sketches]} for o in d.rootComponent.occurrences], 'libraries':[{'name':l.name,'appearances':[a.name for a in l.appearances if any(t in a.name.lower() for t in ['birch','wood','black','pine'])][:15]} for l in app.materialLibraries]}))
