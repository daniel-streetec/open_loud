"""Small deterministic triangle painter for CAD review sheets, no AI geometry."""
import math
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def shaded(mesh,translations,rect):
    triangles=[];pts=[]
    for part in mesh['parts']:
        name=part['name'];offset=translations.get(name,(0,0,0));vertices=[[p[i]+offset[i] for i in range(3)] for p in part['nodes_mm']]
        color=(188,163,126)
        if name.startswith('REF_'):color=(55,64,71)
        elif 'steel' in name or 'thread_plate' in name:color=(151,163,174)
        elif 'Port' in name:color=(50,58,66)
        for j in range(0,len(part['indices']),3):
            tri=[vertices[part['indices'][j+k]] for k in range(3)];normal=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]));length=math.sqrt(dot(normal,normal))
            if length<1e-10:continue
            lighting=.58+.42*abs(dot([v/length for v in normal],[-.45,.45,-.77]))
            fill='#'+''.join(f'{max(0,min(255,round(v*lighting))):02x}' for v in color)
            shape=[(p[0]-.70*p[2],-p[1]-.35*p[2]) for p in tri];pts+=shape
            depth=sum(dot(p,[-.7,.35,-1]) for p in tri)/3
            triangles.append((depth,shape,fill))
    lo=[min(p[i] for p in pts) for i in range(2)];hi=[max(p[i] for p in pts) for i in range(2)];rx,ry,rw,rh=rect
    scale=min(rw/(hi[0]-lo[0]),rh/(hi[1]-lo[1]));ox=rx+(rw-(hi[0]-lo[0])*scale)/2;oy=ry+(rh-(hi[1]-lo[1])*scale)/2
    return ''.join('<polygon points="'+' '.join(f'{ox+(x-lo[0])*scale:.2f},{oy+(y-lo[1])*scale:.2f}' for x,y in shape)+f'" fill="{fill}" stroke="{fill}" stroke-width="0.2"/>' for depth,shape,fill in sorted(triangles,key=lambda t:t[0]))
