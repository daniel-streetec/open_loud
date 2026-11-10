"""Small SI BRep factory for own regenerated purchase-part references and hardware."""
import adsk.core,adsk.fusion,math
class Parts:
    def __init__(self,root):self.root=root;self.tm=adsk.fusion.TemporaryBRepManager.get();self.created=[]
    def point(self,a):return adsk.core.Point3D.create(*(v*100 for v in a))
    def box(self,origin,size):
        center=[a+b/2 for a,b in zip(origin,size)]
        return self.tm.createBox(adsk.core.OrientedBoundingBox3D.create(self.point(center),adsk.core.Vector3D.create(1,0,0),adsk.core.Vector3D.create(0,1,0),*(v*100 for v in size)))
    def cylinder(self,a,b,r):return self.tm.createCylinderOrCone(self.point(a),r*100,self.point(b),r*100)
    def subtract(self,a,b):
        assert self.tm.booleanOperation(a,b,adsk.fusion.BooleanTypes.DifferenceBooleanType);return a
    def hexz(self,x,y,z,h,af):
        body=self.cylinder([x,y,z],[x,y,z+h],af/math.sqrt(3))
        for angle in (0,math.pi/3,2*math.pi/3):
            slab=self.tm.createBox(adsk.core.OrientedBoundingBox3D.create(self.point([x,y,z+h/2]),
                adsk.core.Vector3D.create(math.cos(angle),math.sin(angle),0),adsk.core.Vector3D.create(-math.sin(angle),math.cos(angle),0),af*100,af*200,h*100))
            assert self.tm.booleanOperation(body,slab,adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return body
    def component(self,name,bodies,part,status='prototype_candidate',source=None):
        cp=self.root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component;cp.name=name;cp.partNumber=part
        cp.attributes.add('OPEN_LOUD','part',part);cp.attributes.add('OPEN_LOUD','status',status)
        if source:cp.attributes.add('OPEN_LOUD','source',source)
        base=cp.features.baseFeatures.add();base.startEdit()
        for i,body in enumerate(bodies):
            assert body and body.isSolid and body.volume>0
            item=cp.bRepBodies.add(body,base);item.name=name+'_'+str(i)
        base.finishEdit();self.created.append(name);return cp
    def washerz(self,name,x,y,z,diameter,od=None):
        h={3:.0005,4:.0008,5:.001}[diameter];outer=od or {3:.007,4:.009,5:.010}[diameter];inner={3:.0032,4:.0043,5:.0053}[diameter]
        body=self.subtract(self.cylinder([x,y,z],[x,y,z+h],outer/2),self.cylinder([x,y,z-.001],[x,y,z+h+.001],inner/2))
        return self.component(name,[body],f'ISO7089_M{diameter}')
    def nutz(self,name,x,y,z,diameter):
        h={3:.0024,4:.0032,5:.0047}[diameter];af={3:.0055,4:.007,5:.008}[diameter]
        body=self.subtract(self.hexz(x,y,z,h,af),self.cylinder([x,y,z-.001],[x,y,z+h+.001],diameter*.0005))
        return self.component(name,[body],f'ISO4032_M{diameter}','nominal_thread_envelope_verify_actual_SKU')
    def boltz(self,name,x,y,under,diameter,length):
        hh={3:.003,4:.004,5:.005}[diameter];hd={3:.0055,4:.007,5:.0085}[diameter];af={3:.0025,4:.003,5:.004}[diameter]
        head=self.cylinder([x,y,under-hh],[x,y,under],hd/2)
        self.subtract(head,self.hexz(x,y,under-hh-.0001,hh*.5,af))
        shaft=self.cylinder([x,y,under],[x,y,under+length],diameter*.0005)
        assert self.tm.booleanOperation(head,shaft,adsk.fusion.BooleanTypes.UnionBooleanType)
        return self.component(name,[head],f'ISO4762_M{diameter}x{round(length*1000)}','nominal_thread_envelope')
    def cut_circle(self,cp,axis,at,diameter,length,name):
        assert axis in ('x','y','z');index='xyz'.index(axis)
        base={'x':cp.yZConstructionPlane,'y':cp.xZConstructionPlane,'z':cp.xYConstructionPlane}[axis]
        V=adsk.core.ValueInput.createByString
        pin=cp.constructionPlanes.createInput();pin.setByOffset(base,V(f'{at[index]*1000:.12g} mm'))
        plane=cp.constructionPlanes.add(pin);plane.isLightBulbOn=False
        sk=cp.sketches.add(plane);sk.name=name
        c=sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(self.point(at)),diameter*50);c.isFixed=True
        inp=cp.features.extrudeFeatures.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(f'{length*1000:.12g} mm')),adsk.fusion.ExtentDirections.PositiveExtentDirection)
        inp.participantBodies=list(cp.bRepBodies);cp.features.extrudeFeatures.add(inp);sk.isLightBulbOn=False
