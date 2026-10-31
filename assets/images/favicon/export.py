from pathlib import Path
from PIL import Image
import math

root=Path(__file__).resolve().parents[3]
master=Image.open(root/'assets/images/favicon/sp-master.png').convert('RGBA')
static=root/'static'
for size in (16,32):
    master.resize((size,size),Image.Resampling.LANCZOS).save(static/f'favicon-{size}x{size}.png',optimize=True)
master.save(static/'favicon.ico',format='ICO',sizes=[(size,size) for size in (16,32,48,64,128,256)])
touch=Image.new('RGBA',master.size,'#1D1E20')
touch.alpha_composite(master)
touch.convert('RGB').resize((180,180),Image.Resampling.LANCZOS).save(static/'apple-touch-icon.png',optimize=True)

# Trace only the approved design's white letter shapes for Safari's single-color mask.
mask=Image.new('1',master.size)
mask.putdata([r>=180 and g>=180 and b>=180 and a>=128 for r,g,b,a in master.getdata()])
bounds=mask.getbbox()
mask=mask.crop(bounds)
width,height=mask.size
pixels=mask.load()
edges={}
def edge(start,end):
    edges.setdefault(start,[]).append(end)
for y in range(height):
    for x in range(width):
        if not pixels[x,y]:continue
        if y==0 or not pixels[x,y-1]:edge((x,y),(x+1,y))
        if x==width-1 or not pixels[x+1,y]:edge((x+1,y),(x+1,y+1))
        if y==height-1 or not pixels[x,y+1]:edge((x+1,y+1),(x,y+1))
        if x==0 or not pixels[x-1,y]:edge((x,y+1),(x,y))
loops=[]
while edges:
    first=next(iter(edges));point=first;loop=[first]
    while True:
        targets=edges[point];next_point=targets.pop()
        if not targets:del edges[point]
        point=next_point
        if point==first:break
        loop.append(point)
    if len(loop)>8:loops.append(loop)

def simplify(points,epsilon):
    if len(points)<3:return points
    a,b=points[0],points[-1]
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    distances=[abs(dy*(p[0]-a[0])-dx*(p[1]-a[1]))/length if length else math.dist(a,p) for p in points]
    greatest=max(range(1,len(points)-1),key=lambda i:distances[i])
    if distances[greatest]>epsilon:
        return simplify(points[:greatest+1],epsilon)[:-1]+simplify(points[greatest:],epsilon)
    return [a,b]

scale=14/max(width,height)
offset_x=(16-width*scale)/2
offset_y=(16-height*scale)/2
paths=[]
for loop in loops:
    # Split closed loops at their farthest point before simplifying their two halves.
    split=max(range(len(loop)),key=lambda i:math.dist(loop[0],loop[i]))
    points=simplify(loop[:split+1],0.8)[:-1]+simplify(loop[split:]+[loop[0]],0.8)[:-1]
    coords=[(offset_x+x*scale,offset_y+y*scale) for x,y in points]
    paths.append('M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in coords)+' Z')
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">\n  <title>SP</title>\n  <path fill="#000" fill-rule="evenodd" d="'+' '.join(paths)+'"/>\n</svg>\n'
(static/'safari-pinned-tab.svg').write_text(svg)
print('Exported PNGs, multi-resolution ICO, Apple touch icon, and Safari vector mask.')
print('Safari mask letter bounds:',bounds,'contours:',len(loops))
