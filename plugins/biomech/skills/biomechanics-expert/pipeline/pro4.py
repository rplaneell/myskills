from common2 import *
import textwrap
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Polygon
LS,LT,LU,LF,LH=16.5,17,12,11,22   # shank, thigh, upper arm, forearm, torso (stick units)
def ik(p0,p1,l1,l2,side=1):
    p0=np.array(p0,float); p1=np.array(p1,float); d=np.linalg.norm(p1-p0); d=min(d,l1+l2-1e-6)
    a=(l1**2-l2**2+d**2)/(2*d); h=math.sqrt(max(l1**2-a**2,0)); u=(p1-p0)/np.linalg.norm(p1-p0); n=np.array([-u[1],u[0]])*side
    return p0+u*a+n*h
INKC='#2b3544'
def limb(ax,pts,lw=5.2,col=INKC):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; ax.plot(xs,ys,color='white',lw=lw+3,solid_capstyle='round',solid_joinstyle='round',zorder=3); ax.plot(xs,ys,color=col,lw=lw,solid_capstyle='round',solid_joinstyle='round',zorder=4)
def head(ax,c,r=4.6): ax.add_patch(Circle(c,r,fc='white',ec=INKC,lw=2.6,zorder=5))
def glow(ax,c,w,h,ang=0): ax.add_patch(Ellipse(c,w,h,angle=ang,fc=ST['red'],ec='none',alpha=.28,zorder=2))
def arrow(ax,a,b,col=ACCENT,lw=2.4): ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=14,color=col,lw=lw,zorder=7))
def pose(ax,hip,sh,knee,ank,toe,el,wr,hd):
    limb(ax,[sh,hip]); limb(ax,[hip,knee,ank,toe]); limb(ax,[sh,el,wr],lw=4.4); head(ax,hd)
def setup(ax):
    ax.set_xlim(0,100); ax.set_ylim(-1,62); ax.set_aspect('equal'); ax.axis('off'); ax.grid(False); ax.plot([4,96],[0,0],color=RULE,lw=2,zorder=1,solid_capstyle='round')
def label(fig,tax,n,title,text,dose):
    tax.axis('off'); tax.set_xlim(-5,100); tax.set_ylim(0,100); tax.grid(False)
    wi=tax.get_position().width*fig.get_figwidth(); hi=tax.get_position().height*fig.get_figheight(); u=hi/100; fs=8.6
    tax.add_patch(Circle((3.2,93),3.1,fc=ACCENT,ec='none',transform=tax.transData)) if False else None
    tax.text(0,95,f"{n}",fontsize=10,fontweight='bold',color='white',va='center',ha='center',bbox=dict(boxstyle='circle,pad=.35',fc=ACCENT,ec='none')); tax.text(7,95,title,fontsize=10.5,fontweight='bold',va='center')
    w=textwrap.wrap(text,int(wi*72/(fs*0.52))); lh=(fs*1.5/72)/u
    tax.text(0,84,'\n'.join(w),fontsize=fs,va='top',color=INK,linespacing=1.5); tax.text(0,3,dose,fontsize=fs,va='bottom',color=ACCENT,fontweight='bold')
fig=newfig(8.9); gs=fig.add_gridspec(4,3,height_ratios=[1,.92,1,.92],hspace=.06,wspace=.1)
LWN=3.4
def L_(ax,pts,col=INKC,lw=LWN,z=4):
    xs=[q[0] for q in pts]; ys=[q[1] for q in pts]; ax.plot(xs,ys,color='white',lw=lw+2.4,solid_capstyle='round',solid_joinstyle='round',zorder=z-1); ax.plot(xs,ys,color=col,lw=lw,solid_capstyle='round',solid_joinstyle='round',zorder=z)
def H_(ax,c,r=4.2): ax.add_patch(Circle(c,r,fc='white',ec=INKC,lw=2.4,zorder=5))
def G_(ax,c,w,h,ang=0): ax.add_patch(Ellipse(c,w,h,angle=ang,fc=ST['red'],ec='none',alpha=.30,zorder=2))
def AR(ax,a,b): ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,color=ACCENT,lw=2.2,zorder=8))
# 1 hip flexor stretch
ax=fig.add_subplot(gs[0,0]); setup(ax); G_(ax,(37,19),9,15,25)
hip=(38.5,17.2); L_(ax,[(39.5,37.2),hip]); L_(ax,[hip,(53,16.4),(51,2.5),(59,1.2)]); L_(ax,[hip,(33,2.8),(19,2.2),(14.5,1.2)]); L_(ax,[(39.5,37.2),(46,28.5),(50,22)],lw=3); H_(ax,(41,44.5)); AR(ax,(30,23),(40,23))
label(fig,fig.add_subplot(gs[1,0]),1,'Estirament del flexor del maluc',"Un genoll a terra, abdomen actiu. Porta el maluc endavant fins a notar l'estirament al davant del maluc de darrere.",'30 s per costat, 2 cops')
# 2 glute bridge
ax=fig.add_subplot(gs[0,1]); setup(ax); sh=(18,3.4); hip=(36.3,11.5); kn=(50,17.6); G_(ax,hip,13,9,24)
L_(ax,[sh,(27.5,1.8),(36.5,1.3)],lw=3); L_(ax,[sh,hip,kn,(54.5,3.4),(61,1.2)]); H_(ax,(11.2,4.6)); AR(ax,(36.3,18),(36.3,25))
label(fig,fig.add_subplot(gs[1,1]),2,'Pont de glutis',"Estirat d'esquena, peus a terra. Puja la pelvis fins que tors i cuixes facin una línia. Millora l'estabilitat de la pelvis a la bici.",'12 repeticions, 3 sèries')
# 3 side plank
ax=fig.add_subplot(gs[0,2]); setup(ax); sh=(21,12.5); hip=(40.6,8.3); kn=(55.3,5.2); an=(69,2.3); G_(ax,(41,9.5),12,8,-12)
L_(ax,[(20,2.2),(31,1.8)],lw=3); L_(ax,[(20,2.2),sh],lw=3); L_(ax,[sh,hip,kn,an,(72,1.2)]); H_(ax,(18.8,21)); AR(ax,(41,15),(41,23))
label(fig,fig.add_subplot(gs[1,2]),3,'Planxa lateral',"Sobre un avantbraç, cos recte de peus a cap. Treballa el tronc que sosté la pelvis a la posició baixa.",'30 s per costat, 3 cops')
# 4 thoracic extension
ax=fig.add_subplot(gs[2,0]); setup(ax); ax.add_patch(Circle((30,4.2),4.2,fc='#d6dbe3',ec=FAINT,lw=1.6,zorder=2)); sh=(27,9.4); hip=(47,3.8); G_(ax,(28,10.5),11,7,20)
L_(ax,[sh,(22,17.5),(14.5,10.8)],lw=3); L_(ax,[sh,hip]); L_(ax,[hip,(54,16.5),(59,2.8),(65.5,1)]); H_(ax,(17.6,6.2)); AR(ax,(27,17),(20,13.5))
label(fig,fig.add_subplot(gs[3,0]),4,'Extensió toràcica sobre un rodet',"Rodet d'escuma sota els omòplats, mans darrere del cap. Deixa caure l'esquena enrere amb suavitat i respira. Ajuda a estirar els braços sense enfilar les espatlles.",'10 respiracions lentes')
# bike background
def bike(ax):
    for c in ((24,13),(73,13)): ax.add_patch(Circle(c,13,fill=False,ec='#d3d9e1',lw=2,zorder=1))
    bb=(45,9); sad=(38,32); ht=(66,33); hb=(69,21)
    for a_,b_ in [(bb,sad),(sad,ht),(bb,hb),(ht,hb),(hb,(73,13)),(bb,(24,13)),(sad,(24,13))]: ax.plot([a_[0],b_[0]],[a_[1],b_[1]],color='#b9c1cc',lw=2.6,solid_capstyle='round',zorder=2)
    ax.plot([33,43],[33,33],color=INKC,lw=4,solid_capstyle='round',zorder=3); ax.plot([ht[0]-1,ht[0]+5],[ht[1]+1.5,ht[1]-1],color=INKC,lw=3.6,solid_capstyle='round',zorder=3); ax.add_patch(Circle(bb,5.7,fill=False,ec=FAINT,lw=1.2,ls=(0,(2,2)),zorder=2))
hip=np.array([36,34]); sh=hip+20*np.array([math.cos(math.radians(42)),math.sin(math.radians(42))]); wr=sh+18.4*np.array([math.cos(math.radians(-52)),math.sin(math.radians(-52))])
el=ik(sh,wr,10,9,side=1); el2=ik(sh,wr,10,9,side=-1); el=el if el[1]<el2[1] else el2
kn=ik(hip,(49,16),15,14,side=1); kn2=ik(hip,(49,16),15,14,side=-1); kn=kn if kn[0]>kn2[0] else kn2
ax=fig.add_subplot(gs[2,1]); setup(ax); bike(ax); G_(ax,el,8,6,0); L_(ax,[sh,hip]); L_(ax,[hip,kn,(49,16),(55,14.6)]); L_(ax,[sh,el,wr],lw=3); H_(ax,sh+np.array([5.8,4.6])); ax.text(el[0]-9,el[1]-6,'≈ 150°',fontsize=8.8,fontweight='bold',color=ST['green'])
label(fig,fig.add_subplot(gs[3,1]),5,'Colzes suaus a la bici',"Mans a les manetes, espatlles lluny de les orelles, colzes lleugerament doblegats (uns 150°). Revisa la postura cada minut durant 5 minuts suaus.",'5 minuts, a ritme suau')
ax=fig.add_subplot(gs[2,2]); setup(ax); bike(ax); ax.add_patch(plt.Rectangle((15,12.5),13,5,fc='#d6dbe3',ec=FAINT,lw=1.2,zorder=2)); a2=np.array([22,20]); k2=ik(hip,a2,15,14,side=1); k2b=ik(hip,a2,15,14,side=-1); k2=k2 if k2[0]>k2b[0] else k2b
L_(ax,[hip,k2,a2,(28,19)],col='#9aa4b2',lw=3); L_(ax,[sh,hip]); L_(ax,[hip,kn,(49,16),(55,14.6)]); L_(ax,[sh,el,wr],lw=3); H_(ax,sh+np.array([5.8,4.6])); ax.plot([22,48],[hip[1],hip[1]],color=ST['green'],lw=2.2,ls=(0,(4,3)),zorder=6)
label(fig,fig.add_subplot(gs[3,2]),6,"Malucs quiets: pedalada d'una cama","Sobre rodet, marxa lleugera: 30 s amb una cama i 30 s amb l'altra, l'altre peu en un suport. La pelvis no ha de pujar i baixar (la línia verda ha de quedar plana).",'4 sèries de 30 s per cama')
finish(fig,'19','Exercicis i mobilitat per a les tres millores',"Sis exercicis amb figures de línia. Els números 1, 2 i 4 treballen la flexibilitat que et limita a la posició baixa; el 3 i el 6 treballen l'estabilitat de la pelvis; el 5 és de tècnica a la bici.","El canvi de manillar ajuda, però si el cos no t'acompanya el problema tornarà. Fes aquests exercicis 3 cops per setmana durant 4 setmanes i torna a gravar. Si algun exercici fa mal, para i consulta un professional.",'19_exercicis_i_mobilitat.png')
# ---------- 20 filming setup
fig=newfig(8.4); gs=fig.add_gridspec(2,2,width_ratios=[1.6,1],height_ratios=[.78,1.3],hspace=.14,wspace=.06)
ax=fig.add_subplot(gs[0,0]); ax.set_aspect('equal'); ax.axis('off'); ax.grid(False); ax.set_xlim(-1.3,4.6); ax.set_ylim(-1.2,1.2); ax.set_title('Vista des de dalt',loc='left',fontsize=11,fontweight='bold')
ax.add_patch(Polygon([[3.35,0],[.9,.62],[.9,-.62]],closed=True,fc=ACCENT,alpha=.09,ec='none')); ax.add_patch(plt.Rectangle((-.85,-.2),1.75,.4,fc=PANEL,ec=MUTED,lw=1.4)); ax.text(.02,0,'bici al rodet',ha='center',va='center',fontsize=9,color=MUTED)
ax.add_patch(plt.Rectangle((3.35,-.2),.3,.4,fc=ACCENT,ec='none')); ax.text(3.5,.42,'càmera en trípode',ha='center',fontsize=9,fontweight='bold',color=ACCENT)
ax.annotate('',xy=(.95,-.05),xytext=(3.3,-.05),arrowprops=dict(arrowstyle='<->',lw=1.5,color=ST['red'])); ax.text(2.1,-.2,'uns 3 m',ha='center',fontsize=10,fontweight='bold',color=ST['red'])
ax.text(0,-.38,'costat de la cadena (dret)\nde cara a la càmera',ha='center',va='top',fontsize=8.6,color=INK); ax.add_patch(plt.Rectangle((-1.28,-1.1),.07,2.2,fc='#e8ecf1',ec='none')); ax.text(-1.15,.95,'fons llis i clar',fontsize=8.6,color=MUTED)
ax.text(3.5,-.62,'llum a la cara,\nsense contrallum',fontsize=8.6,color='#9a6a00',fontweight='bold',va='top',ha='center')
ax2=fig.add_subplot(gs[1,0]); setup(ax2); ax2.set_xlim(-6,150); ax2.set_ylim(-2,64); ax2.set_title('Vista de costat',loc='left',fontsize=11,fontweight='bold')
bike(ax2); hip=np.array([36,34]); sh=hip+20*np.array([math.cos(math.radians(42)),math.sin(math.radians(42))]); wr=sh+18.4*np.array([math.cos(math.radians(-52)),math.sin(math.radians(-52))])
el=ik(sh,wr,10,9,side=1); el2=ik(sh,wr,10,9,side=-1); el=el if el[1]<el2[1] else el2; an=np.array([49,16]); kn=ik(hip,an,15,14,side=1); kn2=ik(hip,an,15,14,side=-1); kn=kn if kn[0]>kn2[0] else kn2
L_(ax2,[sh,hip],col='#a7b1bf'); L_(ax2,[hip,kn,an,(55,14.6)],col='#a7b1bf'); L_(ax2,[sh,el,wr],col='#a7b1bf',lw=3); ax2.add_patch(Circle(sh+np.array([5.8,4.6]),4.2,fc='white',ec='#a7b1bf',lw=2.4,zorder=5))
ax2.plot([128,128],[0,9],color=MUTED,lw=2.4); ax2.add_patch(plt.Rectangle((123.5,9),9,6,fc=ACCENT,ec='none')); ax2.plot([123.5,45],[9,9],color=ST['red'],lw=1.5,ls=(0,(4,3)),zorder=1)
ax2.text(86,5.2,'objectiu a l\'alçada de l\'eix del pedalier',fontsize=8.6,color=ST['red'],fontweight='bold',ha='center'); ax2.text(128,18,'càmera',fontsize=8.6,ha='center',color=ACCENT,fontweight='bold')
mk=[(sh,'espatlla',(2,60)),(hip,'maluc (punt ossi del costat)',(-4,48)),(el,'colze',(92,58)),(kn,'genoll (costat de fora)',(96,47)),(an,'turmell (os de fora)',(96,38)),((55,14.6),'bola del peu',(96,29))]
for pt,t,pos in mk:
    ax2.scatter(*pt,s=70,color=ST['red'],edgecolor='white',linewidth=1.4,zorder=8); ax2.annotate(t,xy=pt,xytext=pos,fontsize=8.6,va='center',color=INK,arrowprops=dict(arrowstyle='-',color=FAINT,lw=.9),zorder=9)
ax3=fig.add_subplot(gs[:,1]); ax3.axis('off'); ax3.set_xlim(0,100); ax3.set_ylim(0,100); ax3.grid(False)
ax3.text(0,99,'LLISTA DE GRAVACIÓ',fontsize=8.5,fontweight='bold',color=ACCENT,va='top')
items=["Càmera fixa en un trípode, sense moure la càmera ni fer zoom","Horitzontal, a l'alçada del pedalier i a uns 3 m","Costat de la cadena (dret) i, en un segon clip, l'esquerre","60 imatges per segon (o més) i 1080p","Bona llum i fons llis; roba ajustada","Adhesius al maluc, genoll, turmell, bola del peu, espatlla i colze","2 a 3 minuts a ritme normal per cada estil, sense escalfament","Un segon clip al final d'una sessió dura (per veure la fatiga)"]
wi=ax3.get_position().width*fig.get_figwidth()-.4; hi=ax3.get_position().height*fig.get_figheight(); u=hi/100; fs=9; lh=(fs*1.45/72)/u; cwid=int((wi*72*.88)/(fs*0.53)); y=93
for j,t in enumerate(items):
    w=textwrap.wrap(t,cwid); ax3.text(0,y,f"{j+1}",fontsize=11,fontweight='bold',color=ACCENT,va='top'); ax3.text(6,y,'\n'.join(w),fontsize=fs,va='top',linespacing=1.45); y-=len(w)*lh+lh*1.1
finish(fig,'20','Com gravar la propera prova',"Com col·locar la càmera i on posar els adhesius (cinta de color) per al proper vídeo, amb la llista de comprovacions. La vista de costat no és a escala: la càmera va a uns 3 m.","Una càmera fixa, a l'alçada del pedalier i ben horitzontal evita deformar els angles. Els adhesius ajuden el programa a trobar el maluc, el genoll i el turmell amb menys error, i el clip a l'esquerra permet mirar l'asimetria.",'20_muntatge_de_gravacio.png')
# ---------- 21 confidence
fig=plt.figure(figsize=(CW/200,8.4)); ax=fig.add_axes([0,0,1,1]); ax.axis('off'); ax.set_xlim(0,100); ax.set_ylim(0,84); ax.grid(False)
items=[('Vídeo més llarg','Ara: 9, 8, 4 i 2 pedalades per estil. Amb 2 a 3 minuts per estil serien 30 o més.','Gran'),
('Més imatges per segon i més resolució','Ara: 30 per segon i 464 x 832 píxels, amb moviment borrós. A 60 i 1080p baixa l\'error.','Gran'),
('Càmera fixa, horitzontal, a 3 m','Ara: càmera a la mà, que es mou. Un trípode evita errors de perspectiva i de gir.','Gran'),
('Adhesius i mides reals','Entrecuix, alçada del selló, biela, potència, espaiadors, angle del tub del selló.','Gran'),
('Segona eina de seguiment','Sports2D al teu ordinador (aquí el model no s\'ha pogut baixar). Comparar els dos programes.','Mitjà'),
('Gravar des del costat esquerre','Sense això no es pot dir res de l\'asimetria entre cames.','Mitjà'),
('Una prova de referència de camp','Foto amb plomada pel genoll a les 3 i goniòmetre del genoll a baix, per calibrar l\'error.','Mitjà'),
('Repetir la prova 2 o 3 cops','Per saber quin canvi és real i quin és soroll del dia.','Mitjà'),
('Les teves sensacions i objectius','On et fa mal, quant de temps vols estar a cada posició, carretera o gravel, i si els tres estils són els que he vist.','Mitjà')]
y=82
for j,(t,s,e) in enumerate(items):
    col=ST['green'] if e=='Gran' else ST['amber']; ax.plot([0,100],[y+1,y+1],color=RULE,lw=.9)
    ax.text(0,y-4,f"{j+1:02d}",fontsize=14,fontweight='bold',color=FAINT,va='center'); ax.text(6,y-2.6,t,fontsize=10.5,fontweight='bold',va='center'); ax.text(6,y-6.3,s,fontsize=8.7,color=MUTED,va='center')
    ax.add_patch(FancyBboxPatch((86,y-6.6),14,5.2,boxstyle='round,pad=0.0,rounding_size=1.2',fc=col,ec='none',alpha=.18)) if False else ax.add_patch(plt.Rectangle((86,y-6.6),14,5.2,fc=col,ec='none',alpha=.16)); ax.text(93,y-4,f"efecte {e.lower()}",fontsize=8.6,fontweight='bold',ha='center',va='center',color=col if e=='Gran' else '#9a6a00'); y-=9
finish(fig,'21','Què necessito per tenir més confiança',"Les coses concretes que farien pujar la fiabilitat de l'anàlisi, de més a menys efecte. Ara la confiança general és mitjana.","Ara mateix són fiables els angles grans i repetits (genoll, maluc, tors), però no les xifres petites ni res de la cama esquerra. Amb 3 o 4 d'aquests punts la confiança passaria de mitjana a alta.",'21_per_pujar_la_confianca.png')
print('pro4 ok')
