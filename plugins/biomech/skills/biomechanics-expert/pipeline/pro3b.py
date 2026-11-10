from common2 import *
import textwrap, json
from matplotlib.patches import Circle
R=A['pts']['R']; NUM=json.load(open('/mnt/user-data/working/fitnums.json')); dpm=NUM['deg_per_mm_torso']; mpe=NUM['mm_per_deg_elbow']
def c1(v): return f"{v:.1f}".replace('.',',')
def rotv(v,deg): a=math.radians(deg); return np.array([v[0]*math.cos(a)-v[1]*math.sin(a), v[0]*math.sin(a)+v[1]*math.cos(a)])
def arc(img,v,p1,p2,r,col,w=8):
    d=ImageDraw.Draw(img); a1=math.degrees(math.atan2(p1[1]-v[1],p1[0]-v[0])); a2=math.degrees(math.atan2(p2[1]-v[1],p2[0]-v[0]))
    if (a2-a1)%360>180: a1,a2=a2,a1
    d.arc([v[0]-r,v[1]-r,v[0]+r,v[1]+r],a1,a2,fill=col,width=w)
def dashed(img,a,b,col,w=6,seg=14):
    d=ImageDraw.Draw(img); a=np.array(a); b=np.array(b); n=int(np.linalg.norm(b-a)/seg)
    for t in range(0,n,2): d.line([tuple(a+(b-a)*t/n),tuple(a+(b-a)*min(t+1,n)/n)],fill=col,width=w)
def pills(img,items):
    lay=Image.new('RGBA',img.size,(0,0,0,0))
    for xy,t,fs,fill in items: pill(lay,xy,t,fs,fill=fill)
    return Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB')
def para_block(fig,ax,items,fs=9.3,gap=1.0):
    wi=ax.get_position().width*fig.get_figwidth(); hi=ax.get_position().height*fig.get_figheight(); u=hi/100
    lh=(fs*1.52/72)/u; hh=(8.2*1.9/72)/u; cw=int(wi*72/(fs*0.53)); y=99
    for h,t,hc,bar in items:
        w=textwrap.wrap(t,cw); ax.text(0,y,h.upper(),fontsize=8,fontweight='bold',color=hc if hc!=INK else ACCENT,va='top')
        if bar: ax.add_patch(plt.Rectangle((-2.2,y-hh-len(w)*lh+lh*.15),.7,len(w)*lh+hh*.1,fc=hc,ec='none'))
        ax.text(0,y-hh,'\n'.join(w),fontsize=fs,va='top',linespacing=1.52); y-=hh+len(w)*lh+lh*gap
def card(name_png,num,title,col,img,sections,what,why,extra=None):
    fig=newfig(6.4); gs=fig.add_gridspec(1,2,width_ratios=[1,1.18],wspace=.06)
    ax=fig.add_subplot(gs[0]); ax.imshow(img); ax.axis('off'); ax.grid(False)
    ax2=fig.add_subplot(gs[1]); ax2.axis('off'); ax2.set_xlim(0,100); ax2.set_ylim(0,100); ax2.grid(False)
    para_block(fig,ax2,sections); finish(fig,num,title,what,why,name_png)
SC=lambda i:np.array(R['hip'][i])
# ---------- 15 hip closing
i=frame_at_phase('B',0); pil=skel(getframe(i),i,2,labels=(),lw=5,jr=8).convert('RGBA')
hip=np.array(R['hip'][i])*2; sh=np.array(R['sh'][i])*2; kn=np.array(R['knee'][i])*2; wr=np.array(R['wr'][i])*2
arc(pil,hip,sh,kn,120,hx(ST['red'])[:3],10)
tdir=sh-hip; kdir=kn-hip; tg=min([rotv(kdir/np.linalg.norm(kdir),s*38) for s in (1,-1)],key=lambda u:np.linalg.norm(u-tdir/np.linalg.norm(tdir)))*np.linalg.norm(tdir)
dashed(pil,hip,hip+tg,hx(ST['green'])[:3],7)
d=ImageDraw.Draw(pil); d.line([(wr[0]+36,wr[1]+10),(wr[0]+36,wr[1]-120)],fill=hx(ACCENT)[:3],width=8); d.polygon([(wr[0]+14,wr[1]-112),(wr[0]+58,wr[1]-112),(wr[0]+36,wr[1]-156)],fill=hx(ACCENT)[:3])
img=pills(pil,[((hip[0]-30,hip[1]+90),f"maluc {sig['hip'][i]:.0f}°  ·  objectiu 38° o més",30,hx(ST['red'],225)),((wr[0]-170,wr[1]-230),'manillar +10 mm',28,hx(ACCENT,225))])
card('15_millora1_maluc_tancat.png','15','Millora 1: el maluc es tanca massa a la posició baixa',ST['red'],np.array(crop(img,2)),[
 ('Què veig',f"A dalt de la pedalada (les 12) el maluc es tanca a {mval('B','hip_min_top'):.0f}° (±5°) a l'estil baix, i a {mval('A','hip_min_top'):.0f}° a les manetes. L'arc vermell és el teu angle; la línia verda és on tindria el tors amb 38°.",INK,False),
 ('Per què importa',"Comoditat: pessic o pressió al davant del maluc i càrrega lumbar. Risc de lesió: sobrecàrrega dels flexors del maluc i de l'esquena si hi passes molta estona. Potència: un maluc molt tancat limita la pujada del genoll i fa rebotar la pelvis.",INK,False),
 ('Causa probable',"Alçada del manillar (stack) i caiguda massa grans per a la teva flexibilitat actual; també flexibilitat dels flexors del maluc, i fatiga.",INK,False),
 ('Solució concreta',f"Puja el manillar 10 mm (un espaiador de 10 mm) i retesta: cada 10 mm obren el maluc uns {c1(10*dpm)}°. Si encara és per sota de 38°, afegeix 10 mm més; en total uns 50 mm resolen el cas. Alternativa sense eines: usa la part baixa només per a esforços curts. Complementa el canvi amb els estiraments de la figura 19.",ST['green'],True),
 ('Confiança',"Alta: fins i tot sumant l'error de 5°, el maluc queda per sota de 38°.",INK,False)],
 "El fotograma de les 12 en posició baixa, amb l'angle del maluc en vermell i el tors d'objectiu en verd discontinu.","És el canvi amb més efecte: és l'únic punt vermell amb confiança alta. Canvia una sola cosa (el manillar) i torna a gravar.")
# ---------- 16 elbows
panels=[]
for k in 'AB':
    i=frame_at_phase(k,180); pil=skel(getframe(i),i,2,labels=(),lw=5,jr=8).convert('RGBA'); sh=np.array(R['sh'][i])*2; el=np.array(R['el'][i])*2; wr=np.array(R['wr'][i])*2
    col=hx(ST['red'] if k=='B' else ST['amber'])[:3]; arc(pil,el,sh,wr,80,col,10)
    g1=(sh-el)/np.linalg.norm(sh-el); tgt=min([rotv(g1,s*160) for s in (1,-1)],key=lambda u:-u[0])*np.linalg.norm(wr-el); dashed(pil,el,el+tgt,hx(ST['green'])[:3],7)
    pil=pills(pil,[((el[0]+50,el[1]+40),f"colze {sig['elbow'][i]:.0f}°",32,hx(ST['red'] if k=='B' else ST['amber'],225)),((20,40),SHORT[k],30,hx(INK,215))])
    panels.append(np.array(crop(pil,2,box=(30,230,464,832))))
card('16_millora2_colzes_doblegats.png','16','Millora 2: els colzes van molt doblegats',ST['amber'],np.hstack(panels),[
 ('Què veig',f"A les manetes el colze és a {mval('A','elbow_deg'):.0f}° (atenció) i a la part baixa a {mval('B','elbow_deg'):.0f}° (problema), amb ±5° d'error. La referència és 150 a 170°. La línia verda és on estaria l'avantbraç amb 160°.",INK,False),
 ('Per què importa',"Comoditat: espatlles, coll i canells carreguen més pes. En gravel, uns braços doblegats i rígids transmeten els cops del terreny. Potència: gairebé no es nota; és sobretot comoditat i control.",INK,False),
 ('Causa probable',"Manillar massa baix o massa a prop per al teu tors (abast), tècnica (espatlles enfilades cap a les orelles) o poca mobilitat del tòrax.",INK,False),
 ('Solució concreta',f"1) Tècnica: espatlles baixes i colzes suaus, uns 150°. 2) Fes primer la millora 1. 3) Només si després els colzes segueixen per sota de 140° a les manetes, potència 10 mm més llarga: estira el colze uns {10/mpe:.0f}°. Un canvi cada cop.",ST['green'],True),
 ('Confiança','Mitjana a alta: el semàfor de les manetes no canvia amb ±5°.',INK,False)],
 "El colze a les manetes (esquerra) i a la part baixa (dreta), amb l'angle mesurat i la referència en verd discontinu.","Uns braços una mica més estirats i relaxats alleugereixen espatlles i coll i milloren el control, sobretot en gravel.")
# ---------- 17 pelvis bounce
idx=stroke_idx('B'); i=frame_at_phase('B',180); pil=skel(getframe(i),i,2,labels=(),lw=4,jr=6).convert('RGBA'); d=ImageDraw.Draw(pil); hp=np.array(R['hip'])[idx]*2
for p_ in hp: d.ellipse([p_[0]-9,p_[1]-9,p_[0]+9,p_[1]+9],fill=hx(ST['red'])[:3],outline=(255,255,255),width=3)
top=hp[:,1].min(); bot=hp[:,1].max(); x0=hp[:,0].min()-70
d.line([(x0,top),(x0,bot)],fill=hx(ACCENT)[:3],width=7); d.line([(x0-16,top),(x0+16,top)],fill=hx(ACCENT)[:3],width=7); d.line([(x0-16,bot),(x0+16,bot)],fill=hx(ACCENT)[:3],width=7)
img=pills(pil,[((x0-40,top-85),f"pelvis {mval('B','hip_bounce_mm'):.0f} mm",30,hx(ACCENT,225))])
fig=newfig(6.9); gs=fig.add_gridspec(2,2,width_ratios=[1,1.18],height_ratios=[1.2,1],wspace=.04,hspace=.28)
ax=fig.add_subplot(gs[:,0]); ax.imshow(np.array(crop(img,2))); ax.axis('off'); ax.grid(False)
ax2=fig.add_subplot(gs[0,1]); ax2.axis('off'); ax2.set_xlim(0,100); ax2.set_ylim(0,100); ax2.grid(False)
txt=[('Què veig',f"La pelvis puja i baixa uns {mval('B','hip_bounce_mm'):.0f} mm a l'estil baix, contra {c1(mval('A','hip_bounce_mm'))} mm a les manetes (±8 mm).",INK,False),('Causa probable',f"Sobretot el maluc tancat (millora 1). Secundari: selló una mica alt (extensió {mval('B','knee_max'):.0f}°, al límit de 145 a 155°) i estabilitat del tronc.",INK,False),('Solució',"Fes primer la millora 1. Només si el rebot passa de 15 mm amb el maluc ja per sobre de 38°, baixa el selló 3 mm (uns 1,8° menys d'extensió) i retesta. Reforç: planxa lateral i malucs quiets (figura 19). Confiança mitjana.",ST['green'],True)]
para_block(fig,ax2,txt,fs=9)
axc=fig.add_subplot(gs[1,1]); gr=np.arange(360)
for k in 'AB':
    cc=[]
    for r in df[df.seg==k].itertuples():
        a=int(round(r.start_s*30)); b=a+int(round(r.dur_s*30)); p=np.maximum.accumulate(phase[a:b]); y_=hipb[a:b]
        if len(p)>5: cc.append(np.interp(gr,p,y_))
    cc=np.array(cc); axc.plot(gr,cc.mean(0),color=STYLE[k],lw=2.2,label=SHORT[k]+' · '+('manetes' if k=='A' else 'part baixa')); axc.fill_between(gr,cc.mean(0)-cc.std(0),cc.mean(0)+cc.std(0),color=STYLE[k],alpha=.22,lw=0)
axc.invert_yaxis(); axc.set_xticks([0,90,180,270,360]); axc.set_xticklabels(['12','3','6','9','12']); axc.set_xlabel('Biela (rellotge)'); axc.set_ylabel('Pelvis amunt / avall (mm)'); axc.legend(fontsize=8.5,loc='lower left')
finish(fig,'17','Millora 3: la pelvis rebota a la posició baixa',"A l'esquerra, la trajectòria de la pelvis (punts vermells) durant una pedalada en posició baixa. A la dreta, el moviment vertical de la pelvis al llarg del cercle del pedal per als dos estils.","És un símptoma més que una causa. Si arregles el maluc, el rebot pot baixar sol; per això va tercer.",'17_millora3_rebot_pelvis.png')
# ---------- 18 ladder
fig=plt.figure(figsize=(CW/200,7.2)); ax=fig.add_axes([0,0,1,1]); ax.axis('off'); ax.set_xlim(0,100); ax.set_ylim(0,72); ax.grid(False)
steps=[('1','Manillar +10 mm','Obrir el maluc a la posició baixa: 32° ara, objectiu 38° o més.','Mida: 10 mm (fins a 50 mm en total)  ·  Causa: stack i flexibilitat',ST['red']),
('2','Colzes suaus, potència +10 mm si cal','Colze a 138° a les manetes, objectiu 150°.','Mida: 0 a 10 mm  ·  Causa: abast i tècnica',ST['amber']),
('3','Selló 3 mm més baix, només si el rebot continua','Pelvis a 23 mm a la posició baixa, objectiu menys de 15 mm.','Mida: 3 mm  ·  Causa: selló al límit alt i estabilitat',ACCENT)]
for j,(n,t,s,m,c) in enumerate(steps):
    y=62-j*19.5; x=j*3
    ax.add_patch(plt.Rectangle((x,y-14),58,15.5,fc=PANEL,ec='none')); ax.add_patch(plt.Rectangle((x,y-14),.8,15.5,fc=c,ec='none')); ax.text(x+3.2,y-6.8,n,fontsize=30,fontweight='bold',color=c,va='center')
    ax.text(x+9,y-2.4,t,fontsize=12.5,fontweight='bold',va='center'); ax.text(x+9,y-7,s,fontsize=9.6,va='center'); ax.text(x+9,y-11,m,fontsize=8.6,color=MUTED,va='center')
ax.text(0,71,'ORDRE DE CANVIS (UN CADA COP, GRAVANT ENTRE MIG)',fontsize=8.5,fontweight='bold',color=ACCENT,va='center')
ax.add_patch(plt.Rectangle((66,43),34,25,fc='white',ec=RULE,lw=1.2)); ax.text(68,66,'LLISTA DE VIGILÀNCIA',fontsize=8.5,fontweight='bold',color=ACCENT,va='center')
ax.text(68,62.5,"• Genoll 31 a 56 mm darrere la bola del peu:\n  revisa amb una plomada\n• Cadència de 79 rpm a les manetes\n  (rpm = revolucions per minut)\n• Selló en alçada: mantenir\n• Esquerra contra dreta: no es pot veure".replace('comprova-ho amb','revisa amb'),fontsize=8.6,va='top',linespacing=1.65)
ax.add_patch(plt.Rectangle((66,2),34,38,fc='white',ec=ST['red'],lw=1.4)); ax.text(68,37.5,'QUAN ANAR A UN FISIO O A UN EXPERT EN BIKE FIT',fontsize=7.6,fontweight='bold',color=ST['red'],va='center')
ax.text(68,34,"• Dolor al davant del maluc o lumbar\n  a l'estil baix\n• Formigueig o adormiment a les mans\n• Dolor de genoll que no marxa\n• Sensació que una cama treballa menys\n  (cal gravar des de l'esquerra)\n• Dolor persistent d'espatlla o coll\n\nUn vídeo no diagnostica res: si hi ha dolor,\nconsulta un professional.",fontsize=8.6,va='top',linespacing=1.6)
finish(fig,'18','Escala de prioritats',"L'ordre en què et recomano fer els canvis, la mida de cada un, la llista de coses a vigilar i els senyals que indiquen que és moment d'anar a un professional.","Canviar una sola cosa cada cop i gravar després és l'única manera de saber què ha funcionat. Mai facis els tres alhora. Si hi ha dolor, un fisio o un expert en bike fit (ajust de la bici) val més que qualsevol vídeo.",'18_escala_prioritats.png')
print('pro3b ok')
