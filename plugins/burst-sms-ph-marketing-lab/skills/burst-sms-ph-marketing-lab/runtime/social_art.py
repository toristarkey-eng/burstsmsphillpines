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
    if motif != "phone-chat":
        # One conversation panel with a contrasting shadow. Do not stack duplicate
        # white cards: their shared edge disappears and makes the SMS look synthetic.
        rect(78,92,760,350,"navy",36)
        rect(50,60,760,350,"white",36)

    if motif == "phone-chat":
        # A complete native phone gives the message a clear context. The dark
        # bezel and navy bubble outline keep adjacent pale surfaces distinct.
        rect(300,18,340,564,"navy",52)
        rect(316,34,308,532,"white",38)
        rect(418,48,104,10,"navy",5)
        oval(535,46,14,14,"navy")
        text(campaign.sender_name,346,90,244,42,29,"navy",True,1)
        divider=box(338,146,244,2)
        d.line((divider[0],divider[1],divider[0]+divider[2],divider[1]),
               fill=palette["cyan"],width=max(2,round(3*scale)))
        rect(340,170,260,196,"cloud",24)
        a,b,c,e=box(340,170,260,196)
        d.rounded_rectangle((a,b,a+c-1,b+e-1),round(24*scale),outline=palette["navy"],width=max(2,round(3*scale)))
        text(campaign.message,358,185,224,166,28,"navy",False,4)
        rect(410,536,120,8,"navy",4)
        alt="A complete navy-framed phone on a colourful Burst background, showing one sender header and one readable outlined SMS bubble"
        name_y=90
        bubble_height=196
    elif motif == "mystery-sender":
        # Keep the disguise as a playful illustration, separate from the SMS UI.
        rect(180,92,210,68,"navy",28)
        rect(430,92,210,68,"navy",28)
        rect(390,116,50,16,"navy",7)
        rect(150,104,38,16,"navy",7)
        rect(640,104,38,16,"navy",7)
        poly([(205,108),(225,108),(300,148),(278,148)],"cyan")
        poly([(455,108),(475,108),(550,148),(528,148)],"cyan")
        oval(330,170,100,32,"violet")
        oval(425,170,100,32,"violet")
        poly([(331,186),(300,170),(312,205),(360,205)],"violet")
        poly([(524,186),(555,170),(543,205),(495,205)],"violet")
        alt="Playful sunglasses and moustache illustration above a single realistic-looking SMS conversation card"
        name_y=215
    else:
        alt="Single SMS conversation card with one sender header and one clearly bounded message bubble, with a "+("spotlight" if motif=="spotlight" else "bold colour pop")+" behind it"
        name_y=104

    # The phone-chat motif has its own complete, bounded device UI above.
    if motif == "phone-chat":
        frame=box(300,18,340,564)
        if frame[0]<64 or frame[0]+frame[2]>1016 or frame[1]<heading_bottom or frame[1]+frame[3]>footer-24:
            raise hold("Phone social motif leaves the protected body region")
        return {"motif":motif,"backdrop":bg,"frame":frame,"heading_bottom":heading_bottom,
                "illustrative_only":True,"alt":alt,"source":"registered native renderer geometry",
                "minimum_type_size":round(28*scale),"visual_inspection_required":True,
                "sender_header_count":1,"message_bubble_count":1,
                "stacked_same_fill_cards":False,"message_bubble_outline":"navy",
                "device":"complete-native-phone"}

    # The sender appears once in the conversation header. The message sits in a
    # separate, visibly bounded incoming bubble; do not duplicate either label.
    text(campaign.sender_name,104,name_y,650,54,38,"navy",True,1)
    divider=box(104,name_y+66,652,2)
    d.line((divider[0],divider[1],divider[0]+divider[2],divider[1]),
           fill=palette["cyan"],width=max(2,round(3*scale)))
    bubble_y=name_y+88
    bubble_height=98 if motif=="mystery-sender" else 148
    rect(100,bubble_y,660,bubble_height,"cloud",24)
    a,b,c,e=box(100,bubble_y,660,bubble_height)
    d.rounded_rectangle((a,b,a+c-1,b+e-1),round(24*scale),outline=palette["navy"],width=max(2,round(3*scale)))
    bubble_font=28 if motif=="mystery-sender" else 32
    text(campaign.message,126,bubble_y+10,608,bubble_height-18,bubble_font,"navy",False,2)
    frame=box(0,0,900,600)
    if frame[0]<64 or frame[0]+frame[2]>1016 or frame[1]<heading_bottom or frame[1]+frame[3]>footer-24:
        raise hold("Playful illustration leaves the protected body region")
    return {"motif":motif,"backdrop":bg,"frame":frame,"heading_bottom":heading_bottom,
            "illustrative_only":True,"alt":alt,"source":"registered native renderer geometry",
            "minimum_type_size":round(32*scale),"visual_inspection_required":True,
            "sender_header_count":1,"message_bubble_count":1,
            "stacked_same_fill_cards":False,"message_bubble_outline":"navy"}
