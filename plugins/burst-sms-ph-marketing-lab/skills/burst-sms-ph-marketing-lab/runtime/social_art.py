"""Bounded native illustration for playful social posts; no external assets or UI claims."""
import math


def paint_social(canvas, campaign, footer, palette, hold):
    d = canvas.draw
    bg = campaign.social_backdrop
    d.rectangle((0, 0, 1079, footer-1), fill=palette[bg])
    # Measure the complete header before allocating one proportionate visual group.
    header_height = canvas.copy_block(campaign, 64, 32, 952, min(360, footer-400),
                                      dark=True, paint=False, heading_sizes=(88, 80, 72))
    heading_bottom = 32+header_height+28
    # Cyan text only has adequate contrast on navy. Violet uses white emphasis.
    before = len(canvas.pending_text)
    canvas.copy_block(campaign, 64, 32, 952, header_height, dark=True,
                      heading_sizes=(88, 80, 72))
    if bg == "violet":
        for i in range(before, len(canvas.pending_text)):
            pos, text, face, colour = canvas.pending_text[i]
            if colour == "cyan":
                canvas.pending_text[i] = (pos, text, face, "white")
    available = footer-heading_bottom-28
    scale = min(1.04, available/620)
    if scale < .65:
        raise hold("Playful social needs a larger readable motif; shorten the header or choose portrait")
    ox = (1080-900*scale)/2
    oy = heading_bottom+(available-620*scale)/2

    def box(x, y, w, h):
        return [round(ox+x*scale), round(oy+y*scale), round(w*scale), round(h*scale)]

    def rect(x, y, w, h, colour, radius=0):
        a,b,c,e=box(x,y,w,h)
        if radius:
            d.rounded_rectangle((a,b,a+c-1,b+e-1), round(radius*scale), fill=palette[colour])
        else:
            d.rectangle((a,b,a+c-1,b+e-1), fill=palette[colour])

    def oval(x,y,w,h,colour):
        a,b,c,e=box(x,y,w,h)
        d.ellipse((a,b,a+c-1,b+e-1),fill=palette[colour])

    def poly(points,colour):
        d.polygon([(round(ox+x*scale), round(oy+y*scale)) for x,y in points],fill=palette[colour])

    def text(value,x,y,w,h,size,colour="navy",bold=False,lines=2):
        canvas.text(value,tuple(box(x,y,w,h)),round(size*scale),colour,bold,lines)

    motif=campaign.social_motif
    if motif == "spotlight":
        poly([(380,10),(520,10),(890,600),(10,600)],"cyan")
        oval(35,420,830,170,"violet")
    else:
        oval(0,0,900,600,"cyan" if bg=="violet" else "violet")
    # Only three deliberate impact strokes, behind the complete illustration.
    for x,y,angle in [(55,82,-.8),(840,66,.8),(873,167,1.2)]:
        dx,dy=math.cos(angle)*22,math.sin(angle)*22
        a,b,_,_=box(x-dx,y-dy,1,1);c,e,_,_=box(x+dx,y+dy,1,1)
        d.line((a,b,c,e),fill=palette['white'],width=max(4,round(8*scale)))
    rect(78,92,760,350,"navy",60)
    poly([(150,390),(150,510),(300,390)],"navy")
    rect(50,60,760,350,"white",60)
    poly([(126,350),(126,475),(290,350)],"white")

    if motif == "mystery-sender":
        # Sunglasses and a curled moustache turn an anonymous SMS into a visual joke.
        rect(180,120,230,120,"navy",40)
        rect(440,120,230,120,"navy",40)
        rect(398,140,56,22,"navy",8)
        rect(147,128,50,22,"navy",8)
        rect(655,128,50,22,"navy",8)
        poly([(206,142),(229,142),(315,218),(286,218)],"cyan")
        poly([(470,142),(493,142),(579,218),(550,218)],"cyan")
        # Two solid curved lobes, not third-party iconography.
        oval(322,270,112,52,"violet")
        oval(420,270,112,52,"violet")
        poly([(323,296),(286,270),(303,319),(355,320)],"violet")
        poly([(530,296),(568,270),(551,319),(500,320)],"violet")
        alt="Playful SMS character in sunglasses and a curled moustache, with its brand name revealed on a folded label"
        name_y=386
    else:
        # Message-pop and spotlight are useful for other SMS topics without a disguise.
        text(campaign.sender_name,104,110,650,75,58,"navy",True,1)
        for x in (135,230,325):
            oval(x,235,48,48,"violet")
        alt="Oversized illustrative SMS bubble with "+("a spotlight" if motif=="spotlight" else "a bold colour pop")+" and a folded sender label"
        name_y=386

    # The label reveal carries the exact sender and fictional message, never baked raster copy.
    rect(160,368,660,212,"navy",24)
    rect(136,346,660,212,"white",24)
    poly([(738,346),(796,404),(738,404)],"cyan")
    # Keep sender lettering clear of the folded corner.
    text(campaign.sender_name,170,name_y-16,552,68,48,"violet",True,1)
    text(campaign.message,170,452,582,82,30,"navy",False,2)
    frame=box(0,0,900,600)
    if frame[0]<64 or frame[0]+frame[2]>1016 or frame[1]<heading_bottom or frame[1]+frame[3]>footer-24:
        raise hold("Playful illustration leaves the protected body region")
    return {"motif":motif,"backdrop":bg,"frame":frame,"heading_bottom":heading_bottom,
            "illustrative_only":True,"alt":alt,"source":"registered native renderer geometry",
            "minimum_type_size":round(30*scale),"visual_inspection_required":True}
