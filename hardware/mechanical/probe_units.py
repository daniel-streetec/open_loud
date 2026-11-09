import adsk.core, adsk.fusion, json

def run(_context: str):
    app=adsk.core.Application.get()
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name='OPEN_LOUD_API_unit_probe'
    d=adsk.fusion.Design.cast(app.activeProduct)
    for name,expr,unit in [('qa_area','6500 mm^2','mm^2'),('qa_d1','2*sqrt(qa_area/PI)','mm'),('qa_d2','2*sqrt(qa_area/(1 mm^2)/PI)*(1 mm)','mm'),('qa_vol','41890176 mm^3','mm^3'),('qa_vol2','34000000 mm^3','mm^3'),('qa_vol3','qa_vol-qa_vol2','mm^3'),('qa_vol4','(qa_vol-qa_vol2)','mm^3'),('qa_vol5','qa_vol / (1 mm^3) - qa_vol2 / (1 mm^3)',''),('qa_vol6','(qa_vol / (1 mm^3) - qa_vol2 / (1 mm^3)) * (1 mm^3)','mm^3')]:
        d.userParameters.add(name,adsk.core.ValueInput.createByString(expr),unit,'unit diagnostic')
    print(json.dumps([(p.name,p.expression,p.value,p.unit) for p in d.userParameters]))
