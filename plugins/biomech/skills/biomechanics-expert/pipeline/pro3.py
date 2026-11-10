from common2 import *
import textwrap, json
from matplotlib.lines import Line2D; from matplotlib.patches import Patch, Circle, FancyBboxPatch, Wedge, Polygon
R=A['pts']['R']
NUM=json.load(open('/mnt/user-data/working/fitnums.json'))
dpm=NUM['deg_per_mm_torso']; mpe=NUM['mm_per_deg_elbow']; mpk=NUM['mm_per_deg_knee']
hip_need=(38-mval('B','hip_min_top'))/dpm
def c1(v): return f"{v:.1f}".replace('.',',')
def rel(k,i):
    bbp=np.array(R['hip'][i])+np.array(BB[k]); return {n:(np.array(R[n][i])-bbp)*MM*np.array([1,-1]) for n in ['ear','sh','el','wr','hip','knee','ank','heel','toe']}
# ---------- 13 fit changes with a drawn bike (generic size 54 gravel/endurance geometry, for illustration)
fig=newfig(8.6); gs=fig.add_gridspec(1,2,width_ratios=[1.28,1],wspace=.02)
ax=fig.add_subplot(gs[0]); ax.set_aspect('equal'); ax.axis('off'); ax.grid(False)
rw=(-425,70); fw=(600,70); rr=355
for c in (rw,fw):
    ax.add_patch(Circle(c,rr,fill=False,ec='#c3cad4',lw=3)); ax.add_patch(Circle(c,rr-26,fill=False,ec='#e3e7ed',lw=1)); ax.plot(*c,'o',color='#9aa4b2',ms=4)
sta=math.radians(73); ht=(385,590); hta=math.radians(71); hb=(ht[0]+150*math.cos(hta),ht[1]-150*math.sin(hta)); st_top=(-540*math.cos(sta),540*math.sin(sta)); bbp=(0,0)
fr=dict(lw=3.4,color='#4a5565',solid_capstyle='round')
for a,b in [(bbp,st_top),(bbp,hb),(st_top,ht),(bbp,rw),(st_top,rw),(hb,fw),(ht,hb)]: ax.plot([a[0],b[0]],[a[1],b[1]],**fr)
sad=np.array([-700*math.cos(sta),700*math.sin(sta)]); ax.plot([sad[0],st_top[0]-0],[sad[1],st_top[1]],color='#4a5565',lw=2.6)
ax.plot([sad[0]-95,sad[0]+125],[sad[1]+6]*2,color=INK,lw=7,solid_capstyle='round')
stem_end=(ht[0]+100,ht[1]+45); ax.plot([ht[0],ht[0]],[ht[1],ht[1]+20],color='#4a5565',lw=3); ax.plot([ht[0],stem_end[0]],[ht[1]+20,stem_end[1]],color=INK,lw=5)
th=np.linspace(-.9,2.6,40); bx=stem_end[0]+45*np.cos(th)*0+70*np.cos(th)*0
ax.plot([stem_end[0],stem_end[0]+95,stem_end[0]+112,stem_end[0]+70,stem_end[0]+20],[stem_end[1],stem_end[1]+5,stem_end[1]-80,stem_end[1]-150,stem_end[1]-160],color=INK,lw=4.5,solid_capstyle='round')
ax.add_patch(Circle((0,0),172.5,fill=False,ec='#9aa4b2',lw=1.3,ls=(0,(2,3)))); ax.plot(0,0,'o',color=INK,ms=5)
i=frame_at_phase('A',180); p=rel('A',i)
for a_,b_ in [('ear','sh'),('sh','el'),('el','wr'),('sh','hip'),('hip','knee'),('knee','ank'),('ank','toe'),('heel','toe')]: ax.plot([p[a_][0],p[b_][0]],[p[a_][1],p[b_][1]],color=STYLE['A'],lw=3,alpha=.85,solid_capstyle='round',zorder=5)
for n in ['sh','el','wr','hip','knee','ank']: ax.plot(*p[n],'o',color='white',mec=STYLE['A'],mew=2,ms=6,zorder=6)
def num(x,y,t,col): ax.add_patch(Circle((x,y),30,color=col,zorder=9)); ax.text(x,y,t,color='white',ha='center',va='center',fontsize=11,fontweight='bold',zorder=10)
def arr(x0,y0,dx,dy,col,lw=2.2): ax.annotate('',xy=(x0+dx,y0+dy),xytext=(x0,y0),arrowprops=dict(arrowstyle='-|>',lw=lw,color=col,shrinkA=0,shrinkB=0),zorder=8)
num(sad[0]-150,sad[1]+95,'1',ST['green']); ax.plot([sad[0]-100,sad[0]-35],[sad[1]+6,sad[1]+6],color=ST['green'],lw=0)
arr(sad[0]+55,sad[1]+175,0,-120,ST['green'],1.6); ax.text(sad[0]+75,sad[1]+135,'sense\ncanvis',fontsize=8.5,color=ST['green'],fontweight='bold',va='center')
arr(sad[0]-20,sad[1]-95,75,0,ST['amber'],2.2); num(sad[0]-70,sad[1]-95,'2',ST['amber'])
bar=np.array([stem_end[0]+100,stem_end[1]-80]); arr(bar[0]+60,bar[1]-20,0,95,ST['red'],2.6); num(bar[0]+60,bar[1]+120,'3',ST['red'])
arr(bar[0]+70,bar[1]-110,85,0,ACCENT,2.2); num(bar[0]+185,bar[1]-110,'4',ACCENT)
ax.set_xlim(-860,1010); ax.set_ylim(-420,1120); ax.set_title('Bici genèrica de mida 54 (només per situar els canvis)',loc='left',fontsize=10,color=MUTED,fontweight='normal')
ax2=fig.add_subplot(gs[1]); ax2.axis('off'); ax2.set_xlim(0,100); ax2.set_ylim(0,100); ax2.grid(False)
rows=[('1','Alçada del selló',ST['green'],'MANTENIR',f"Extensió màxima del genoll {mval('A','knee_max'):.0f}° i {mval('B','knee_max'):.0f}°: dins de 145 a 155°. 1 mm de selló mou el genoll uns {c1(1/mpk)}°, o sigui l'error de ±5° equival a ±{5*mpk:.0f} mm: la càmera no pot justificar cap canvi. Alçada estimada, pedalier a dalt del selló: uns 700 mm (±30)."),
('2','Selló endavant o endarrere',ST['amber'],'COMPROVAR PRIMER',f"Genoll {abs(mval('B','kops_mm')):.0f} a {abs(mval('A','kops_mm')):.0f} mm darrere de la bola del peu a les 3 (±35 mm, regla de poca evidència). Comprova-ho amb una plomada. Si són més de 30 mm, avança el selló 5 mm: baixa l'alçada efectiva uns {c1(5*math.cos(math.radians(73)))} mm."),
('3','Alçada del manillar (stack)',ST['red'],'ESTIL BAIX: +10 MM',f"Maluc a {mval('B','hip_min_top'):.0f}° a dalt a l'estil baix. Cada 10 mm de manillar més alt obren el maluc uns {c1(10*dpm)}°. Per arribar a 38° calen uns {hip_need:.0f} mm: avança de 10 en 10 i mesura. L'estil 1 (maluc {mval('A','hip_min_top'):.0f}°) es queda igual."),
('4','Abast (potència)',ACCENT,"L'ÚLTIM, SI CAL",f"Colze a {mval('A','elbow_deg'):.0f}° a les manetes. 10 mm més d'abast estiren el colze uns {10/mpe:.0f}°. Primer relaxa espatlles i puja el manillar; només si després el colze segueix per sota de 140°, prova una potència 10 mm més llarga.")]
y=99
for n,t,col,v,txt in rows:
    ax2.add_patch(plt.Rectangle((0,y-23),.8,23,fc=col,ec='none')); ax2.add_patch(Circle((4.6,y-3.5),2.3,color=col)); ax2.text(4.6,y-3.6,n,color='white',ha='center',va='center',fontsize=10.5,fontweight='bold')
    ax2.text(9,y-3.5,t,fontsize=11.5,fontweight='bold',va='center'); ax2.text(100,y-3.5,v,fontsize=8.5,fontweight='bold',color=col if col!=ST['amber'] else '#9a6a00',ha='right',va='center')
    ax2.text(9,y-8.2,'\n'.join(textwrap.wrap(txt,64)),fontsize=8.6,va='top',color=INK,linespacing=1.45); y-=25
finish(fig,'13','Canvis d\'ajust: selló, posició i manillar',"Els quatre canvis d'ajust que té sentit provar, situats a la bici, amb la xifra concreta i l'ordre. Els números surten de la teva geometria mesurada (alçada 1,735 m): ±8% en mil·límetres i ±5° en angles.","Canvia UNA cosa cada cop i grava igual. L'alçada del selló ja està bé; el que té més guany és el manillar a l'estil baix. Limitació: només veig el teu costat dret, així que no puc dir res de l'alineació de les falques ni de si el selló està recte.",'13_canvis_dajust.png')
# ---------- 14 frame size and gravel
fig=newfig(9.9); ax=fig.add_axes([0,0,1,1]); ax.axis('off'); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.grid(False)
ax.text(0,98,'MIDA DE QUADRE SEGONS L\'ALÇADA',fontsize=8.5,fontweight='bold',color=ACCENT)
sizes=[(160,168,'48 a 50','XS'),(168,173,'50 a 52','S'),(173,178,'52 a 54','S/M'),(178,183,'54 a 56','M/L'),(183,190,'56 a 58','L')]
x0,x1=160,190; X=lambda h:(h-x0)/(x1-x0)*100
for a,b,sz,ltr in sizes:
    hl=a<=173.5<b; ax.add_patch(plt.Rectangle((X(a)+.15,84),X(b)-X(a)-.3,8,fc=ACCENT if hl else PANEL,ec='none')); ax.text((X(a)+X(b))/2,89,sz,ha='center',va='center',fontsize=10,fontweight='bold',color='white' if hl else INK); ax.text((X(a)+X(b))/2,86,ltr,ha='center',va='center',fontsize=8.5,color='white' if hl else MUTED)
    ax.text(X(a),80.5,f"{a}",fontsize=8,color=MUTED,ha='center')
ax.text(100,80.5,'190 cm',fontsize=8,color=MUTED,ha='center'); ax.annotate('',xy=(X(173.5),83.6),xytext=(X(173.5),77),arrowprops=dict(arrowstyle='-|>',color=ST['red'],lw=2)); ax.text(X(173.5),75,'tu: 173,5 cm',fontsize=9.5,fontweight='bold',color=ST['red'],ha='center')
ax.text(0,70.5,"Estàs just a la frontera entre la 52 i la 54: la millor estimació és la 54 (M), però la teva entrecuixa i la geometria de la bici decideixen.",fontsize=9,color=INK)
ax.text(0,63,'QUÈ DIU EL VÍDEO (SENSE CINTA MÈTRICA)',fontsize=8.5,fontweight='bold',color=ACCENT)
facts=[('0,58','tors / cama','proporcions normals'),('0,67','braç / cama','proporcions normals'),('506 mm','mà davant del pedalier','±8%'),('624 mm','mà sobre el pedalier','±8%'),('≈ 700 mm','alçada del selló','±30 mm')]
for j,(v,l,e) in enumerate(facts):
    x=j*20; ax.add_patch(plt.Rectangle((x,48),19,12.5,fc=PANEL,ec='none')); ax.text(x+1.2,56,v,fontsize=15,fontweight='bold'); ax.text(x+1.2,51.8,l,fontsize=7.8,color=MUTED); ax.text(x+1.2,49.6,e,fontsize=7,color=FAINT)
ax.text(0,43.5,'BICIS DE GRAVEL AMB UN AJUST MÉS NATURAL PER A TU',fontsize=8.5,fontweight='bold',color=ACCENT)
ax.text(0,40.2,"Criteri: a les manetes estàs còmode amb tors 33° i maluc 47°, però a la part baixa el maluc es tanca a 32°. Una bici amb uns 30 a 50 mm més d'alçada de davantera que la teva actual et deixaria\nles manetes cap als 36 a 38° i la part baixa cap als 38° de maluc. Descripcions generals; confirma stack i abast a la taula oficial de la mida 54.",fontsize=8,color=MUTED,va='top',linespacing=1.5)
cols=[(0,'Model'),(24,'Geometria'),(48,'Per què et pot anar natural'),(76,'A vigilar')]
for x,t in cols: ax.text(x,29.5,t.upper(),fontsize=7.8,fontweight='bold',color=MUTED)
ax.plot([0,100],[28,28],color=INK,lw=1)
bikes=[('Specialized Diverge','Endurance gravel, davantera alta','Postura relaxada per a hores amb les mans a les manetes','Que no et quedi massa curta'),
('Trek Checkpoint','Endurance gravel, davantera alta','Molta alçada: el maluc no es tanca a la part baixa','Preu i pes segons versió'),
('Cannondale Topstone Carbon','Davantera alta, abast curt','Molt còmoda per a espatlles i colzes','Abast curt: potser potència més llarga'),
('Canyon Grizl','Equilibrada, venda directa','Punt mig entre còmoda i esportiva; guia de mida detallada','Es pot provar poc a botiga'),
('Giant Revolt Advanced','Una mica més esportiva','Postura una mica baixa però no extrema','Menys alçada: mira el maluc baix'),
('Cervélo Áspero, Scott Addict Gravel, Orbea Terra','Gravel de cursa, davantera baixa','Només si decideixes mantenir l\'estil baix','És l\'estil que ara et tanca el maluc')]
y=24.5
for m,g_,w,v in bikes:
    ax.text(0,y,'\n'.join(textwrap.wrap(m,24)),fontsize=8.8,fontweight='bold',va='center',linespacing=1.3)
    for x,wd,t in ((24,26,g_),(48,30,w),(76,26,v)): ax.text(x,y,'\n'.join(textwrap.wrap(t,wd)),fontsize=8.2,va='center',color=INK,linespacing=1.3)
    ax.plot([0,100],[y-3.7,y-3.7],color=RULE,lw=.8); y-=6.9
ax.text(0,y-1.2,"Per afinar de veritat necessito: entrecuixa (de terra al coll del peu a l'entrecuix, descalç), marca i mida de la bici actual, longitud de la potència i espaiadors.",fontsize=8.6,fontweight='bold',color=ST['red'])
finish(fig,'14','La teva mida de quadre i bicis de gravel',"La mida de quadre més probable per a la teva alçada, les xifres de postura que surten del vídeo i una llista curta de bicis de gravel amb el motiu pel qual encaixarien amb la teva manera de pedalar.","Només amb l'alçada, la 54 (M) és la millor estimació, però estàs a la frontera amb la 52. No puc afirmar la mida perfecta sense la teva entrecuixa i la geometria de la bici actual, i no he pogut verificar des d'aquí les taules de geometria de cada marca: contrasta aquestes taules abans de comprar.",'14_mida_quadre_i_gravel.png')
print('pro3a ok')
