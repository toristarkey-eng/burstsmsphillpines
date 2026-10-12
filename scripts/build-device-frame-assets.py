"""Maintainer: build editable blank device frames from locked palette geometry.

These source assets contain no product UI, logos, screenshots or campaign copy.
Final advertisements still use the bundled renderer and its delivery validator.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/assets/device-frames'
OUT.mkdir(parents=True,exist_ok=True)
NAVY='#002A66'; CLOUD='#F4F5FF'; WHITE='#FFFFFF'; CYAN='#00AEC4'

def build(name,size,shapes):
    im=Image.new('RGBA',size,(0,0,0,0));d=ImageDraw.Draw(im);svg=[]
    for shape in shapes:
        kind,values,fill=shape
        if kind=='rect':
            x,y,w,h,r=values;d.rounded_rectangle((x,y,x+w-1,y+h-1),r,fill=fill)
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>')
        elif kind=='ellipse':
            x,y,w,h=values;d.ellipse((x,y,x+w-1,y+h-1),fill=fill)
            svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}"/>')
        else:
            d.polygon(values,fill=fill);svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in values)+f'" fill="{fill}"/>')
    im.save(OUT/(name+'.png'))
    (OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size[0]} {size[1]}">'+''.join(svg)+'</svg>\n')

build('phone-frame',(800,1440),[
 ('rect',(80,40,640,1280,72),NAVY),('rect',(102,62,596,1236,54),CYAN),
 ('rect',(110,70,580,1220,48),WHITE),('rect',(128,140,544,1088,14),CLOUD),
 ('rect',(302,96,144,14,7),NAVY),('ellipse',(468,94,18,18),NAVY),
 ('rect',(302,1250,196,10,5),NAVY)])
build('laptop-frame',(1440,1000),[
 ('rect',(190,70,1060,650,34),NAVY),('rect',(210,90,1020,610,18),CYAN),
 ('rect',(224,108,992,570,8),WHITE),('ellipse',(713,80,14,14),WHITE),
 ('polygon',[(190,720),(1250,720),(1390,820),(50,820)],NAVY),
 ('polygon',[(250,744),(1190,744),(1270,796),(170,796)],CLOUD),
 ('rect',(50,818,1340,32,10),NAVY),('rect',(624,809,192,13,6),CYAN)])
print('Built phone and laptop PNG/SVG masters.')
