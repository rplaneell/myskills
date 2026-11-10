from common2 import *
from matplotlib.lines import Line2D; from matplotlib.patches import Patch
R=A['pts']['R']
def rel(k,i):
    bbp=np.array(R['hip'][i])+np.array(BB[k]); return {n:(np.array(R[n][i])-bbp)*MM*np.array([1,-1]) for n in ['ear','sh','el','wr','hip','knee','ank','heel','toe']}
# ---------- 04 body diagram
fig=newfig(7.4); gs=fig.add_gridspec(1,2,wspace=.04)
for j,k in enumerate('AB'):
    ax=fig.add_subplot(gs[j]); i=frame_at_phase(k,180); p=rel(k,i); ax.grid(False); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(plt.Circle((0,0),172.5,fill=False,ls=(0,(2,3)),color=FAINT,lw=1.2)); ax.plot(0,0,'+',color=MUTED,ms=9,mew=1.5); ax.plot([-250,330],[-215,-215],color=RULE,lw=2)
    for a,b in [('ear','sh'),('sh','el'),('el','wr'),('sh','hip'),('hip','knee'),('knee','ank'),('ank','toe'),('heel','toe')]:
        ax.plot([p[a][0],p[b][0]],[p[a][1],p[b][1]],color='#aeb7c4',lw=13,solid_capstyle='round',zorder=1); ax.plot([p[a][0],p[b][0]],[p[a][1],p[b][1]],color='#e4e8ee',lw=9,solid_capstyle='round',zorder=2)
    sad=p['hip']+np.array([-5,-62]); ax.plot([sad[0]-90,sad[0]+110],[sad[1]]*2,color=INK,lw=6,solid_capstyle='round',zorder=3)
    ax.plot([p['wr'][0]+28]*2,[p['wr'][1]-18,p['wr'][1]+34],color=INK,lw=6,solid_capstyle='round',zorder=3)
    tor=(p['hip']+p['sh'])/2
    spec=[('sh',p['sh'],'Espatlla','shoulder_deg','°'),('el',p['el'],'Colze','elbow_deg','°'),('tor',tor,'Tors','torso_deg','°'),('hip',p['hip'],'Maluc a dalt','hip_min_top','°'),('knee',p['knee'],'Genoll estès','knee_max','°'),('ank',p['ank'],'Turmell, recorregut','ankle_rom','°')]
    spec.sort(key=lambda t:-t[1][1]); xl=660; ys=np.linspace(max(t[1][1] for t in spec)+30,p['ank'][1]+10,len(spec))
    for (n,pt,lab,key,u),yl in zip(spec,ys):
        gr=mgrade(k,key); v=mval(k,key); ax.scatter(*pt,s=210,marker=MARK[gr],color=ST[gr],edgecolor='white',linewidth=1.6,zorder=6)
        ax.plot([pt[0]+14,xl-10],[pt[1],yl],color=FAINT,lw=.9,zorder=0)
        ax.text(xl,yl+16,lab,fontsize=9.3,color=MUTED,va='center'); ax.text(xl,yl-20,f"{v:.0f}°  {GRADE_TXT[gr]}",fontsize=11,fontweight='bold',color=ST[gr] if gr!='amber' else '#9a6a00',va='center')
    if k=='B':
        ax.annotate('',xy=(p['wr'][0]+28,p['wr'][1]+145),xytext=(p['wr'][0]+28,p['wr'][1]+48),arrowprops=dict(arrowstyle='-|>',lw=2.2,color=ACCENT)); ax.text(p['wr'][0]+28,p['wr'][1]+175,'manillar\n+10 mm',fontsize=9.5,color=ACCENT,fontweight='bold',ha='center',va='bottom')
    ax.set_xlim(-330,1050); ax.set_ylim(-260,1180); ax.set_title(f"{SHORT[k]}  ·  {SUB[k]}",loc='left',color=STYLE[k],fontsize=11,fontweight='bold')
fig.legend(handles=[Line2D([0],[0],marker=MARK[g_],color='w',markerfacecolor=ST[g_],markeredgecolor='white',ms=11,label=f"{GRADE_TXT[g_]}") for g_ in ('green','amber','red')]+[Line2D([0],[0],color=ACCENT,lw=2,label='cap on mou el canvi recomanat')],loc='lower center',ncol=4,fontsize=9.5,bbox_to_anchor=(.5,-.02))
finish(fig,'04','Mapa del cos: on són els punts forts i els febles',"El teu cos al punt més baix de la pedalada, de costat, amb cada articulació marcada amb el semàfor (color i forma: cercle bé, triangle atenció, quadrat problema). La fletxa blava mostra cap on mou el canvi recomanat.","L'estil baix concentra els problemes al maluc, al tors i al colze, mentre que el genoll i el turmell estan bé en tots dos. Les mides es calibren amb la teva alçada (1,735 m) i tenen un marge d'uns 8%.",'04_mapa_del_cos.png')
# ---------- 05 ghost
def rot(v,deg): a=math.radians(deg); return np.array([v[0]*math.cos(a)-v[1]*math.sin(a), v[0]*math.sin(a)+v[1]*math.cos(a)])
def ideal(sh,hip,kn,an,el,wr,torso,knee,elbow,shoulder):
    Lt=np.linalg.norm(sh-hip); Lua=np.linalg.norm(el-sh); Lfa=np.linalg.norm(wr-el); Lsh=np.linalg.norm(an-kn)
    th=math.radians(torso); ish=hip+Lt*np.array([math.cos(th),-math.sin(th)]); u=(hip-ish)/np.linalg.norm(hip-ish)
    iel=max([ish+Lua*rot(u,s*shoulder) for s in (1,-1)],key=lambda q:(q[0]-ish[0])+.5*(q[1]-ish[1]))
    u2=(ish-iel)/np.linalg.norm(ish-iel); iwr=max([iel+Lfa*rot(u2,s*elbow) for s in (1,-1)],key=lambda q:q[0]-iel[0])
    u3=(hip-kn)/np.linalg.norm(hip-kn); ian=max([kn+Lsh*rot(u3,s*knee) for s in (1,-1)],key=lambda q:q[1])
    return ish,iel,iwr,ian
def cmp(d): return f"{abs(d):.0f}° {'per sota' if d<0 else 'per sobre'}"
fig=newfig(6.4); gs=fig.add_gridspec(1,2,wspace=.03)
for j,k in enumerate('AB'):
    ax=fig.add_subplot(gs[j]); idx=stroke_idx(k); i=int(idx[np.argmax(sig['knee'][idx])]); g_=lambda n:np.array(R[n][i]); sh,hip,kn,an,el,wr=[g_(n) for n in ['sh','hip','knee','ank','el','wr']]
    ax.imshow((0.35*getframe(i)+0.65*255).astype(np.uint8)); ax.grid(False)
    mine=dict(torso=sig['torso'][i],knee=sig['knee'][i],elbow=sig['elbow'][i]); ref=dict(torso=38,knee=150,elbow=160)
    ish,iel,iwr,ian=ideal(sh,hip,kn,an,el,wr,ref['torso'],ref['knee'],ref['elbow'],90)
    ln=lambda pts,c,ls,lw,z: ax.plot([q[0] for q in pts],[q[1] for q in pts],color=c,ls=ls,lw=lw,zorder=z,solid_capstyle='round')
    ln([sh,hip,kn,an],'white','-',5.5,3); ln([sh,el,wr],'white','-',5.5,3); ln([sh,hip,kn,an],STYLE[k],'-',3,4); ln([sh,el,wr],STYLE[k],'-',3,4)
    ln([ish,hip,kn,ian],ST['green'],(0,(3,2)),2.6,5); ln([ish,iel,iwr],ST['green'],(0,(3,2)),2.6,5)
    for q in [sh,hip,kn,an,el,wr]: ax.plot(*q,'o',color=STYLE[k],mec='white',mew=1.5,ms=6,zorder=6)
    for q in [ish,iel,iwr,ian]: ax.plot(*q,'o',color='white',mec=ST['green'],mew=1.8,ms=6,zorder=6)
    rows=[(sh,'Tors',mine['torso'],ref['torso']),(el,'Colze',mine['elbow'],ref['elbow']),(kn,'Genoll',mine['knee'],ref['knee'])]; ys=[285,345,430]
    for (pt,lab,mv,rv),yl in zip(rows,ys):
        ax.plot([pt[0],440],[pt[1],yl],color=FAINT,lw=.9,zorder=1); ax.text(446,yl-10,lab,fontsize=9,color=MUTED,va='center',clip_on=False); ax.text(446,yl+14,f"{mv:.0f}°  ·  ref. {rv}°",fontsize=10,fontweight='bold',va='center',clip_on=False); ax.text(446,yl+36,cmp(mv-rv),fontsize=8.8,color=ST['red'] if abs(mv-rv)>8 else MUTED,va='center',clip_on=False)
    ax.set_xlim(0,640); ax.set_ylim(832,230); ax.axis('off'); ax.set_title(f"{SHORT[k]}  ·  {SUB[k]}   (t = {i/30:.1f} s)",loc='left',fontsize=10.5,color=STYLE[k],fontweight='bold')
fig.legend(handles=[Line2D([0],[0],color=INK,lw=3,label='Tu (mesurat)'),Line2D([0],[0],color=ST['green'],lw=2.6,ls=(0,(3,2)),label='Referència de bici de carretera típica (mateixos ossos, mateix maluc)')],loc='lower center',ncol=2,fontsize=9.5,bbox_to_anchor=(.5,-.02))
finish(fig,'05','El teu esquelet contra una referència',"El teu esquelet (línia contínua) sobre un esquelet de referència (verd discontinu) construït amb els teus propis ossos i amb el maluc fix. Les xifres donen la diferència en graus al punt baix de la pedalada; ref. vol dir referència.","El genoll és dins de l'interval habitual, així que l'alçada del selló sembla correcta. La posició baixa s'allunya molt d'un ajust típic al tors i als colzes: pot ser una opció teva per a esforços curts, però és on el maluc es tanca més. Diferències de menys de 5° cauen dins de l'error.",'05_superposicio_referencia.png')
# ---------- 11 scorecard
KEYS=list(Mt[Mt.seg=='A'].key); lab={r.key:r.label for r in Mt[Mt.seg=='A'].itertuples()}
fig=plt.figure(figsize=(CW/200,9.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,94); ax.axis('off'); ax.grid(False)
tiles=[('A','Estil 1',S['A'],'Mitjana'),('B','Estil 2',S['B'],'Mitjana'),('D','Estil 1 (final)',S['D'],'Baixa'),('T','Global',S['overall'],'Mitjana')]
for j,(k,t,s,cf) in enumerate(tiles):
    x0=j*25.2; col=STYLE.get(k,INK)
    ax.add_patch(plt.Rectangle((x0,80),23.4,13,fc=PANEL,ec='none')); ax.add_patch(plt.Rectangle((x0,92),23.4,1,fc=col,ec='none'))
    ax.text(x0+1.4,89.2,t,fontsize=10.5,fontweight='bold',color=col,va='center'); ax.text(x0+1.4,84.3,f"{s['score']:.0f}",fontsize=30,fontweight='bold',va='center'); ax.text(x0+7.4,83.7,'/ 100',fontsize=10,color=MUTED,va='center')
    ax.add_patch(plt.Rectangle((x0+13,85.5),9,.8,fc=RULE,ec='none')); ax.add_patch(plt.Rectangle((x0+13+9*s['lo']/100,85.2),9*(s['hi']-s['lo'])/100,1.4,fc=col,ec='none')); ax.plot(x0+13+9*s['score']/100,85.9,'o',color=INK,ms=5)
    ax.text(x0+13,88.5,f"interval {s['lo']:.0f} a {s['hi']:.0f}",fontsize=8,color=INK); ax.text(x0+13,82.5,f"conf. {cf.lower()}",fontsize=8,color=MUTED)
colx={'A':44,'B':62,'D':80}; xs=dict(C=94.5)
ax.text(0,76,'MESURA',fontsize=8.5,fontweight='bold',color=MUTED)
for k,t in (('A','ESTIL 1'),('B','ESTIL 2'),('D','ESTIL 1 FINAL')): ax.text(colx[k],76,t,fontsize=8.5,fontweight='bold',color=STYLE[k])
ax.text(xs['C'],76,'ESTIL 3',fontsize=8.5,fontweight='bold',color=STYLE['C'],ha='center')
y=71; step=5.35
for key in KEYS:
    ax.plot([0,100],[y+step/2,y+step/2],color=RULE,lw=.8); ax.text(0,y,lab[key],fontsize=10,va='center')
    for k in 'ABD':
        r=Mt[(Mt.seg==k)&(Mt.key==key)].iloc[0]; v=r.value; txt=(f"{abs(v):.0f} mm {'darrere' if v<0 else 'davant'}" if key=='kops_mm' else (f"{v:.0f} {r.unit}" if abs(v)>=10 else f"{v:.1f} {r.unit}".replace('.',',')))
        ax.scatter(colx[k]-1.8,y,s=80,marker=MARK[r.grade],color=ST[r.grade],zorder=5,edgecolor='white',linewidth=1); ax.text(colx[k],y+.9,txt,fontsize=9.6,fontweight='bold',va='center'); ax.text(colx[k],y-1.4,f"{GRADE_TXT[r.grade].lower()} · conf. {CONF[r.confidence].lower()}",fontsize=7.6,color=MUTED,va='center')
    r=Mt[(Mt.seg=='C')&(Mt.key==key)].iloc[0]; v=r.value; txt=(f"{abs(v):.0f} mm {'darrere' if v<0 else 'davant'}" if key=='kops_mm' else (f"{v:.0f} {r.unit}" if abs(v)>=10 else f"{v:.1f} {r.unit}".replace('.',',')))
    ax.text(xs['C'],y,txt,fontsize=9.2,color=FAINT,ha='center',va='center'); y-=step
ax.text(0,y-.6,"Només informatiu per a l'estil 3: els intervals d'ajust són per a ciclistes asseguts.  La puntuació és orientativa (idea inspirada en VeloLens), no un diagnòstic.",fontsize=8.3,color=MUTED)
finish(fig,'11','Fitxa de puntuació: la teva pedalada en una pàgina',"Cada mesura amb el seu semàfor per a cada estil, i una puntuació sobre 100 amb el seu interval probable (simulant l'error del seguiment) i la seva confiança. Confiança alta vol dir que el semàfor no canviaria encara que el valor variés dins de l'error.","L'estil 1 (assegut dret) és molt bo, l'estil 2 (baix) perd punts al maluc, al tors i als colzes, i el genoll i la cadència estan bé en tots. La recomprovació del final és curta (2 pedalades) i s'ha de llegir amb cura.",'11_fitxa_puntuacio.png')
# ---------- 12 template
fig=plt.figure(figsize=(CW/200,8.2)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,82); ax.axis('off'); ax.grid(False)
ax.text(0,79,'Data de la prova: ______________',fontsize=10.5); ax.text(36,79,'Què he canviat (només UNA cosa): ____________________________________',fontsize=10.5)
for x,t,c in ((38,'ABANS (aquest vídeo)',ACCENT),(62,'DESPRÉS (propera prova)',MUTED),(88,'CANVI',MUTED)): ax.text(x,73,t,fontsize=9,fontweight='bold',color=c,ha='center')
y=67
for key in ['knee_max','hip_min_top','torso_deg','elbow_deg','shoulder_deg','ankle_rom','rpm','hip_bounce_mm']:
    ax.plot([0,100],[y+3,y+3],color=RULE,lw=.8); ax.text(0,y,lab[key],fontsize=10,va='center')
    for k,x in (('A',31),('B',44)):
        r=Mt[(Mt.seg==k)&(Mt.key==key)].iloc[0]; ax.text(x,y,f"{r.value:.0f} {r.unit}",fontsize=10,fontweight='bold',color=STYLE[k],va='center'); 
    ax.text(31,y+1.9,'estil 1',fontsize=6.6,color=FAINT); ax.text(44,y+1.9,'estil 2',fontsize=6.6,color=FAINT)
    for x0 in (52,70): 
        for dx in (0,8.6): ax.add_patch(plt.Rectangle((x0+dx,y-2),7.8,4,fill=False,ec=FAINT,lw=1,ls=(0,(3,2))))
    ax.add_patch(plt.Rectangle((83,y-2),10,4,fill=False,ec=FAINT,lw=1,ls=(0,(3,2)))); y-=6
for x0,t in ((0,'Imatge «quatre posicions»: ABANS'),(51,'Imatge «quatre posicions»: DESPRÉS')):
    ax.add_patch(plt.Rectangle((x0,1),49,17,fill=False,ec=FAINT,lw=1.4,ls=(0,(4,3)))); ax.text(x0+24.5,9.5,t,ha='center',va='center',fontsize=10,color=FAINT)
ax.text(52,70.2,'estil 1',fontsize=6.6,color=FAINT); ax.text(60.6,70.2,'estil 2',fontsize=6.6,color=FAINT); ax.text(70,70.2,'estil 1',fontsize=6.6,color=FAINT); ax.text(78.6,70.2,'estil 2',fontsize=6.6,color=FAINT)
finish(fig,'12','Plantilla abans i després',"Els teus valors d'ara a l'esquerra i caselles buides a la dreta per omplir amb la propera prova, amb dues caselles grans per a la imatge de les quatre posicions.","Canvia una sola cosa cada cop (per exemple el manillar 10 mm més alt), grava igual i compara. Un canvi de menys de 5° cau dins de l'error del seguiment: no el donis per bo.",'12_plantilla_abans_despres.png')
print('pro2 ok')
