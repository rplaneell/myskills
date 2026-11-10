from style import *
import cv2
A=pickle.load(open('/mnt/user-data/working/an.pkl','rb'))
T=A['T']; R=A['pts']['R']; Lp=A['pts']['L']; sig=A['sig']; SEG=A['SEG']; phase=A['phase']; BB=A['bb']; MM=A['MM']; df_=A['df']
cap=cv2.VideoCapture('/mnt/user-data/working/ride.mp4')
def getframe(i):
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(i)); ok,fr=cap.read(); return cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
def hx(h,a=255): h=h.lstrip('#'); return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),a)
def pill(layer,xy,txt,fs,fill=(16,32,46,205),fg=(255,255,255,255),w='Medium'):
    d=ImageDraw.Draw(layer); f=F(fs,w); tw=d.textlength(txt,font=f); x,y=xy
    d.rounded_rectangle([x,y,x+tw+fs*.9,y+fs*1.55],radius=fs*.5,fill=fill); d.text((x+fs*.45,y+fs*.22),txt,font=f,fill=fg)
def skel(im,i,s=2,labels=('knee','hip','elbow'),bone='#56d4ff',lw=4,jr=6,fs=22,left=False,joint_cols=None,pts=None):
    P=pts or R
    pil=Image.fromarray(im).resize((im.shape[1]*s,im.shape[0]*s),Image.LANCZOS).convert('RGBA')
    ov=Image.new('RGBA',pil.size,(0,0,0,0)); d=ImageDraw.Draw(ov); pt=lambda D,n:tuple(np.array(D[n][i])*s)
    chain=[('ear','sh'),('sh','el'),('el','wr'),('sh','hip'),('hip','knee'),('knee','ank'),('ank','heel'),('heel','toe'),('ank','toe')]
    if left:
        for a,b in [('sh','hip'),('hip','knee'),('knee','ank'),('ank','toe')]: d.line([pt(Lp,a),pt(Lp,b)],fill=hx('#ffffff',90),width=2)
    for a,b in chain: d.line([pt(P,a),pt(P,b)],fill=(255,255,255,235),width=lw+3)
    for a,b in chain: d.line([pt(P,a),pt(P,b)],fill=hx(bone),width=lw)
    for n in ['sh','el','wr','hip','knee','ank','toe','heel','ear']:
        x,y=pt(P,n); c=hx(joint_cols[n]) if joint_cols and n in joint_cols else (255,255,255,255)
        d.ellipse([x-jr,y-jr,x+jr,y+jr],fill=c,outline=hx(INK),width=2)
    pil=Image.alpha_composite(pil,ov)
    off=dict(knee=(16,-10),hip=(-12-fs*5.2,-12),el=(14,-fs*2.3),ank=(16,6))
    lay=Image.new('RGBA',pil.size,(0,0,0,0))
    spec=dict(knee=('knee','genoll'),hip=('hip','maluc'),el=('elbow','colze'),ank=('ankle','turmell'))
    for n,(k,lab) in spec.items():
        if k in labels:
            x,y=pt(P,n); pill(lay,(x+off[n][0],y+off[n][1]),f"{lab} {sig[{'knee':'knee','hip':'hip','el':'elbow','ank':'ankle'}[n]][i]:.0f}°",fs)
    return Image.alpha_composite(pil,lay).convert('RGB')
def crop(pil,s=2,box=(0,230,464,832)): return pil.crop(tuple(int(v*s) for v in box))
def clock(img,cx,cy,r,ph):
    d=ImageDraw.Draw(img); d.ellipse([cx-r,cy-r,cx+r,cy+r],fill='white',outline=INK,width=3)
    for a in (0,90,180,270): t=math.radians(a); d.line([(cx+r*.78*math.sin(t),cy-r*.78*math.cos(t)),(cx+r*.95*math.sin(t),cy-r*.95*math.cos(t))],fill=INK,width=3)
    a=math.radians(ph); d.line([(cx,cy),(cx+r*.72*math.sin(a),cy-r*.72*math.cos(a))],fill=ST['red'],width=6); d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=INK)
