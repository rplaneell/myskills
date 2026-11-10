import sys; sys.path.insert(0,'/mnt/user-data/working/scripts')
import numpy as np, math, pickle, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image, ImageDraw, ImageFont
INTER='/usr/share/fonts/opentype/inter/Inter-%s.otf'
for w in ['Regular','Medium','SemiBold','Bold']: fm.fontManager.addfont(INTER%w)
def F(sz,w='Regular'): return ImageFont.truetype(INTER%w,int(sz))
INK='#16202e'; MUTED='#5b6675'; FAINT='#98a2b0'; RULE='#d9dee5'; PANEL='#f4f6f9'; ACCENT='#0a4d8c'
ST=dict(green='#009E73',amber='#E69F00',red='#D55E00')        # traffic lights (colour blind safe) + shapes
STYLE=dict(A='#0072B2',B='#CC79A7',C='#8c6d46',D='#56B4E9')   # one hue per riding style
NAMES={'A':'Estil 1 · assegut dret, mans a les manetes','B':'Estil 2 · assegut baix, a la part baixa','C':'Estil 3 · dret sobre els pedals','D':'Estil 1 (final) · assegut dret'}
NAMES={k:v.replace(' · ',', ',1) if False else v for k,v in NAMES.items()}
SHORT={'A':'Estil 1','B':'Estil 2','C':'Estil 3','D':'Estil 1 (final)'}
SUB={'A':'assegut dret, mans a les manetes','B':'assegut baix, a la part baixa del manillar','C':'dret sobre els pedals','D':'assegut dret, recomprovació'}
GRADE_TXT={'green':'BÉ','amber':'ATENCIÓ','red':'PROBLEMA'}
MARK={'green':'o','amber':'^','red':'s'}
def mpl_style():
    plt.rcParams.update({'font.family':'Inter','font.size':11,'text.color':INK,'axes.edgecolor':RULE,'axes.labelcolor':MUTED,'axes.titlecolor':INK,
      'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':1,'xtick.major.size':0,'ytick.major.size':0,
      'axes.grid':True,'grid.color':'#e9edf2','grid.linewidth':.8,'axes.axisbelow':True,'legend.frameon':False,'axes.titlesize':12.5,'axes.titleweight':'bold','axes.titlelocation':'left',
      'axes.labelsize':10.5,'xtick.labelsize':10,'ytick.labelsize':10,'figure.facecolor':'white','savefig.facecolor':'white','axes.unicode_minus':False})
mpl_style()
W_,M_=2400,110; CW=W_-2*M_
META='Anàlisi de pedalada  ·  vídeo del 28/10/2026  ·  seguiment MediaPipe (model heavy)  ·  escala calibrada amb 1,735 m'
def _wrap(d,text,font,maxw):
    out=[]
    for para in text.split('\n'):
        cur=''
        for w in para.split(' '):
            t=(cur+' '+w).strip()
            if d.textlength(t,font=font)>maxw and cur: out.append(cur); cur=w
            else: cur=t
        out.append(cur)
    return out
def spaced(d,xy,text,font,fill,sp=3):
    x,y=xy
    for ch in text: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
def plate(content,num,title,what,why,out,note=None):
    if isinstance(content,str): content=Image.open(content)
    c=content.convert('RGB'); c=c.resize((CW,int(c.height*CW/c.width)),Image.LANCZOS)
    tmp=Image.new('RGB',(W_,400),'white'); d=ImageDraw.Draw(tmp)
    f=F(31); fl=F(25,'SemiBold'); colw=(CW-70)//2
    wl=_wrap(d,what,f,colw); yl=_wrap(d,why,f,colw); nl=max(len(wl),len(yl)); lh=int(31*1.55)
    capH=40+36+nl*lh+(60 if note else 0)
    H=270+c.height+60+capH+120
    img=Image.new('RGB',(W_,H),'white'); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W_,12],fill=INK)
    spaced(d,(M_,66),f'FIGURA {num}',F(26,'SemiBold'),ACCENT,4)
    d.text((M_,108),title,font=F(62,'SemiBold'),fill=INK)
    d.line([(M_,214),(W_-M_,214)],fill=RULE,width=2)
    img.paste(c,(M_,250)); y=250+c.height+60
    d.line([(M_,y),(W_-M_,y)],fill=RULE,width=2); y+=36
    for j,(lab,lines) in enumerate((('QUÈ MOSTRA',wl),('PER QUÈ IMPORTA',yl))):
        x=M_+j*(colw+70); spaced(d,(x,y),lab,fl,ACCENT,3)
        for k,l in enumerate(lines): d.text((x,y+44+k*lh),l,font=f,fill=INK)
    y+=40+36+nl*lh
    if note:
        d.rounded_rectangle([M_,y+8,W_-M_,y+8+52],radius=10,fill=PANEL); d.text((M_+22,y+8+10),note,font=F(25,'Medium'),fill=MUTED)
    d.line([(M_,H-92),(W_-M_,H-92)],fill=RULE,width=2)
    d.text((M_,H-70),META,font=F(23),fill=FAINT); t=f'{num}'; d.text((W_-M_-d.textlength(t,font=F(23,'SemiBold')),H-70),t,font=F(23,'SemiBold'),fill=MUTED)
    img.save(out,optimize=True); return out
OUT='/home/user/ride_analysis/images/'
def newfig(h,w=CW/200): return plt.figure(figsize=(w,h))
def finish(fig,num,title,what,why,name,note=None):
    tmp='/tmp/_fig.png'; fig.savefig(tmp,dpi=200,bbox_inches='tight',pad_inches=0.06); plt.close(fig); plate(tmp,num,title,what,why,OUT+name,note)
