from common2 import *
g=np.arange(360)
# ---------- 01 tracking check
fr=[15,390,750]; lab=['Inici','Mig','Final']
fig=newfig(7.0); gs=fig.add_gridspec(2,3,height_ratios=[4.4,1.1],hspace=.28,wspace=.04)
for j,i in enumerate(fr):
    ax=fig.add_subplot(gs[0,j]); ax.imshow(crop(skel(getframe(i),i,2,labels=('knee','hip'),fs=24),2)); ax.axis('off'); ax.set_title(f"{lab[j]}  ·  t = {i/30:.1f} s",loc='left',fontsize=12,fontweight='bold')
ax=fig.add_subplot(gs[1,:]); vis=L[:,[12,14,16,24,26,28,30,32],2].min(1)
ax.plot(T,vis,color=STYLE['A'],lw=1.6); ax.set_ylim(.9,1.005); ax.set_xlim(0,T[-1]); ax.set_ylabel('Confiança\nmínima'); ax.set_xlabel('Temps del vídeo (s)')
for i in fr: ax.axvline(i/30,color=FAINT,lw=1,ls=':')
ax.set_title('Confiança del model a cada fotograma (8 punts del costat dret)',loc='left',fontsize=11,fontweight='bold')
finish(fig,'01','Comprovació del seguiment',"L'esquelet detectat sobre tres fotogrames (inici, mig i final): orella, espatlla, colze, canell, maluc, genoll, turmell, taló i punta del peu de la cama dreta, la que veu la càmera. A sota, la confiança mínima del model en tot el vídeo: sempre per sobre de 0,96.","L'esquelet cau damunt del cos real, així que les mesures de la cama dreta i del tronc són fiables. La cama esquerra queda darrere la bici i no es pot mesurar bé. Un vídeo a 30 imatges per segon i 464 x 832 píxels deixa certa borrositat quan el peu va ràpid.",'01_comprovacio_seguiment.png')
# ---------- 02 timeline
fig=newfig(8.0); gs=fig.add_gridspec(2,4,height_ratios=[1.35,2.0],hspace=.25,wspace=.06)
ax=fig.add_subplot(gs[0,:]); ax.plot(T,sig['torso'],color=INK,lw=1.3)
for k,(nm,a,b) in SEG.items(): ax.axvspan(a,b,color=STYLE[k],alpha=.22,lw=0); ax.text((a+b)/2,53,{'A':'Estil 1','B':'Estil 2','C':'Estil 3','D':'Estil 1'}[k],ha='center',va='top',fontsize=11,color=STYLE[k],fontweight='bold')
ax.set_ylabel("Angle del tors\nsobre l'horitzontal (°)"); ax.set_xlabel('Temps del vídeo (s)'); ax.set_ylim(0,56); ax.set_xlim(0,T[-1])
for j,k in enumerate('ABCD'):
    a=fig.add_subplot(gs[1,j]); mid=int((SEG[k][1]+SEG[k][2])/2*30); a.imshow(crop(skel(getframe(mid),mid,2,labels=('knee','hip'),fs=26),2)); a.axis('off')
    a.set_title(SHORT[k],loc='left',fontsize=11,color=STYLE[k],fontweight='bold',pad=4); a.text(0,-.015,'\n'.join(__import__('textwrap').wrap(SUB[k],30)),transform=a.transAxes,va='top',fontsize=8.5,color=MUTED)
finish(fig,'02','Tres estils de pedalar en un sol vídeo',"He dividit el vídeo segons l'angle del tors. La primera i l'última franja són el mateix estil (assegut dret, mans a les manetes), la del mig és la posició baixa, i la curta és dret sobre els pedals.","Cada estil carrega el cos de manera diferent. Barrejar-los embrutaria totes les xifres, així que cada estil s'analitza per separat. Les franges de color són els trams estables que he utilitzat.".replace('Barrejar-los','Si es barregen els estils,'),'02_estils_de_pedalada.png')
# ---------- 03 four positions
rows=[('A',0),('B',1),('C',2)]; heads=[0,90,180,270]; CLK={0:'les 12  ·  a dalt',90:'les 3  ·  davant',180:'les 6  ·  a baix',270:'les 9  ·  darrere'}
fig=newfig(12.6); gs=fig.add_gridspec(7,4,height_ratios=[.1,.1,1,.13,1,.13,1],hspace=.05,wspace=.03,left=0,right=1,top=.97,bottom=0)
for c,ph in enumerate(heads):
    h=fig.add_subplot(gs[0,c]); h.axis('off'); h.text(0,.2,CLK[ph],fontsize=11.5,fontweight='bold',va='center')
for r,(k,ri) in enumerate(rows):
    lab=fig.add_subplot(gs[2*r+1,:]); lab.axis('off'); lab.text(0,.2,f"{SHORT[k]}  ·  {SUB[k]}",fontsize=11.5,fontweight='bold',color=STYLE[k],va='center')
    for c,ph in enumerate(heads):
        i=frame_at_phase(k,ph); im=crop(skel(getframe(i),i,2,labels=('knee','hip','elbow'),fs=36,lw=4,jr=7),2)
        clock(im,70,86,48,ph); ax=fig.add_subplot(gs[2*r+2,c]); ax.imshow(im); ax.axis('off')
finish(fig,'03','Les quatre posicions del pedal',"El teu cos a les 12, 3, 6 i 9 del rellotge de la biela, per a cada estil, amb l'esquelet i els angles de maluc, genoll i colze mesurats en aquell instant. El rellotge petit indica on és la biela.","A les 12 el maluc està més tancat i a les 6 el genoll està més estès. Compara les files: a la posició baixa (fila del mig) el maluc es tanca i els colzes es doblen molt més que a les manetes.",'03_quatre_posicions.png')
# ---------- 06 curves
def stat(k,s): c=curves[k]['knee' if s=='knee' else s]; return c.mean(0),c.std(0)
def own_left(k,s): return np.roll(curvesL[k][s].mean(0),-180)
joints=[('knee','Genoll (°)'),('hip','Maluc (°)'),('ankle','Turmell (°)')]
fig=newfig(9.6); gs=fig.add_gridspec(3,3,hspace=.32,wspace=.2)
for r,(s,yl) in enumerate(joints):
    for c,main in enumerate('ABC'):
        ax=fig.add_subplot(gs[r,c]); m,sd=stat(main,s)
        ax.fill_between(g,m-ERR[s],m+ERR[s],color=STYLE[main],alpha=.12,lw=0); ax.fill_between(g,m-sd,m+sd,color=STYLE[main],alpha=.35,lw=0)
        ax.plot(g,own_left(main,s),color=FAINT,lw=1.3,ls=(0,(4,3)))
        if main=='A' and len(curves['D'][s])>0: ax.plot(g,curves['D'][s].mean(0),color=STYLE['D'],lw=1.6,ls=':')
        ax.plot(g,m,color=STYLE[main],lw=2.4)
        ax.set_xticks([0,90,180,270,360]); ax.set_xticklabels(['12','3','6','9','12'])
        if c==0: ax.set_ylabel(yl)
        if r==0: ax.set_title(f"{SHORT[main]}\n{SUB[main]}",loc='left',fontsize=9.5,color=STYLE[main],fontweight='bold',pad=6)
        if r==2: ax.set_xlabel('Biela (rellotge)')
from matplotlib.lines import Line2D; from matplotlib.patches import Patch
fig.legend(handles=[Line2D([0],[0],color=INK,lw=2.4,label='cama dreta (es veu bé)'),Patch(fc='#9bb5c9',label='dispersió entre pedalades'),Patch(fc='#dbe5ee',label='error del seguiment (±5° maluc i genoll, ±8° turmell)'),Line2D([0],[0],color=STYLE['D'],lw=1.6,ls=':',label='mateix estil al final del vídeo'),Line2D([0],[0],color=FAINT,lw=1.3,ls=(0,(4,3)),label='cama esquerra (amagada, poc fiable)')],loc='lower center',ncol=3,fontsize=9.5,bbox_to_anchor=(.5,-.01))
fig.subplots_adjust(bottom=.1)
finish(fig,'06','Angles del genoll, el maluc i el turmell al llarg de la pedalada',"Els angles al llarg del cercle del pedal: 12 és dalt de tot i 6 a baix de tot. El halo clar és l'error del seguiment i la banda més fosca és quant es diferencien les teves pedalades entre elles. L'estil 1 inclou, en puntejat, el mateix estil al final del vídeo.","Les corbes es repeteixen molt (banda estreta), així que les diferències entre estils més grans que el halo clar són reals. La cama esquerra (línia gris discontínua) queda darrere la bici i el model només l'endevina: la seva forma no és la d'una pedalada normal, per això no n'extrec conclusions.",'06_angles_vs_posicio_biela.png')
# ---------- 07 polar
fig=newfig(6.4); gs=fig.add_gridspec(1,2,width_ratios=[1.15,1],wspace=.05)
ax=fig.add_subplot(gs[0],projection='polar'); ax.set_theta_zero_location('N'); ax.set_theta_direction(-1); th=np.radians(np.r_[g,0])
ax.fill_between(np.linspace(0,2*np.pi,200),145,155,color=ST['green'],alpha=.16,lw=0)
for k in 'ABC':
    m=np.r_[curves[k]['knee'].mean(0),curves[k]['knee'].mean(0)[0]]; ax.plot(th,m,color=STYLE[k],lw=2.4); ax.fill_between(th,m-5,m+5,color=STYLE[k],alpha=.1,lw=0)
ax.set_rlim(40,175); ax.set_rticks([60,90,120,150]); ax.set_rlabel_position(202); ax.set_xticks(np.radians([0,90,180,270])); ax.set_xticklabels(['les 12\ndalt','les 3','les 6\nbaix','les 9'],fontsize=10.5); ax.grid(color='#e3e8ee')
ax.set_title('Angle del genoll (°)',loc='left',pad=14)
ax2=fig.add_subplot(gs[1]); ax2.axis('off'); ax2.set_xlim(0,1); ax2.set_ylim(0,1); y=.92
ax2.text(0,y,'Extensió màxima del genoll',fontsize=11.5,fontweight='bold'); y-=.1
for k in 'ABC':
    v=curves[k]['knee'].mean(0).max(); ax2.add_patch(plt.Rectangle((0,y-.015),.025,.06,fc=STYLE[k],ec='none')); ax2.text(.05,y+.015,SHORT[k],fontsize=11,fontweight='bold',va='center'); ax2.text(.05,y-.045,SUB[k],fontsize=9,color=MUTED,va='center')
    ax2.text(.98,y,f"{v:.0f}°",fontsize=20,fontweight='bold',ha='right',va='center',color=STYLE[k]); y-=.17
ax2.text(0,y-.01,"Anell verd: 145 a 155°, interval\nhabitual d'extensió màxima.\nHalo: error del seguiment ±5°.",fontsize=10,color=MUTED,va='top',linespacing=1.5)
finish(fig,'07','El genoll al voltant del cercle del pedal',"La distància al centre és l'angle del genoll: com més lluny, més estesa la cama. L'anell verd és l'interval habitual per a l'extensió màxima. A la dreta, el valor màxim de cada estil.","El pic cap a les 6 hauria de tocar l'anell verd, i ho fa en els dos estils asseguts: l'alçada del selló és correcta. Dret sobre els pedals (marró) passa de llarg perquè el cos queda més amunt sobre el pedal; aquest estil no s'avalua amb aquesta regla.",'07_genoll_polar.png')
# ---------- 08 left right
items=[('Extensió màxima\ndel genoll','knee',np.max),('Genoll mínim\n(a dalt)','knee',np.min),('Maluc mínim\n(a dalt)','hip',np.min),('Recorregut\ndel turmell','ankle',np.ptp)]
fig=newfig(5.6); gs=fig.add_gridspec(1,2,wspace=.12)
for j,k in enumerate('AB'):
    ax=fig.add_subplot(gs[j]); x=np.arange(len(items)); w=.36
    rv=[f(curves[k][s].mean(0)) for _,s,f in items]; lv=[f(own_left(k,s)) for _,s,f in items]
    ax.bar(x-w/2,rv,w,color=STYLE[k],yerr=[ERR[s] for _,s,f in items],capsize=3,ecolor=INK,error_kw=dict(lw=1))
    ax.bar(x+w/2,lv,w,color='white',edgecolor=FAINT,hatch='////',lw=1,yerr=[ERR[s]*2 for _,s,f in items],capsize=3,ecolor=FAINT,error_kw=dict(lw=1))
    ax.set_xticks(x); ax.set_xticklabels([i[0] for i in items],fontsize=9); ax.set_ylim(0,205); ax.set_title(f"{SHORT[k]}  ·  {SUB[k]}",loc='left',color=STYLE[k],fontsize=10.5,fontweight='bold')
    for xi,(a,b) in enumerate(zip(rv,lv)): ax.text(xi,max(a,b)+17,f"dif. {abs(a-b):.0f}°",ha='center',fontsize=9,color=MUTED)
    if j==0: ax.set_ylabel('Graus')
fig.legend(handles=[Patch(fc=INK,label='cama dreta (es veu bé)'),Patch(fc='white',ec=FAINT,hatch='////',label='cama esquerra (quasi amagada, error doble)')],loc='lower center',ncol=2,fontsize=9.5,bbox_to_anchor=(.5,-.04))
finish(fig,'08','Esquerra contra dreta: no es pot mesurar amb aquest angle',"La cama dreta mira cap a la càmera. L'esquerra queda darrere la bici i el model n'endevina la posició: barres ratllades i barres d'error el doble de grans.","Qualsevol diferència entre cames cau dins de l'error, així que no en trec cap conclusió d'asimetria. Per comprovar aquesta part, grava un altre cop des del costat esquerre.",'08_esquerra_vs_dreta.png',note='Conclusió: cap afirmació sobre asimetria. Cal una segona gravació des del costat esquerre.')
# ---------- 09 stroke timeline
fig=newfig(6.6); gs=fig.add_gridspec(3,1,hspace=.14)
cols=[('torso_deg','Tors (°)'),('knee_max','Extensió del genoll (°)'),('rpm','Cadència (rpm)')]
for r,(col,yl) in enumerate(cols):
    ax=fig.add_subplot(gs[r]); 
    for k in 'ABCD':
        d=df[df.seg==k]; ax.axvspan(SEG[k][1],SEG[k][2],color=STYLE[k],alpha=.1,lw=0); ax.plot(d.start_s,d[col],'-o',color=STYLE[k],lw=1.8,ms=4.5)
    ax.set_ylabel(yl); ax.set_xlim(0,T[-1])
    if r==1: ax.axhspan(145,155,color=ST['green'],alpha=.13,lw=0)
    if r<2: ax.set_xticklabels([])
    else: ax.set_xlabel('Temps del vídeo (s)')
finish(fig,'09','Pedalada a pedalada: revisió de deriva',"Un punt per pedalada; els colors són els estils. La banda verda és l'interval habitual d'extensió del genoll, i rpm vol dir revolucions per minut.","Dins de cada estil els punts es mantenen plans, sense deriva més enllà de l'error. Però amb només 26 segons no es pot veure fatiga de veritat: cal un clip de 2 a 3 minuts i un altre després d'una sessió dura.",'09_deriva_pedalada_a_pedalada.png',note='Limitació: el vídeo dura 26 s. Això és una revisió de deriva, no una prova de fatiga.')
# ---------- 10 heatmap
fig=newfig(4.6); gs=fig.add_gridspec(1,5,width_ratios=[9,8,4,2,.35],wspace=.35)
for j,k in enumerate('ABCD'):
    ax=fig.add_subplot(gs[j]); c=curves[k]['knee']; med=np.median(c,0); im=ax.imshow(c-med,aspect='auto',cmap='PuOr',vmin=-12,vmax=12,interpolation='nearest',extent=[0,360,len(c),0]); ax.grid(False)
    r=cons[k]; thr=max(2.5,1.4*np.median(r)) if len(r)>3 else 99
    for i,v in enumerate(r):
        if v>thr: ax.text(-16,i+.5,'★',color=ST['red'],fontsize=11,ha='center',va='center')
    ax.set_xticks([0,90,180,270,360]); ax.set_xticklabels(['12','3','6','9','12']); ax.set_yticks(np.arange(len(c))+.5); ax.set_yticklabels([str(i+1) for i in range(len(c))],fontsize=8.5)
    ax.set_title(SHORT[k],loc='left',color=STYLE[k],fontsize=10.5,fontweight='bold'); ax.set_xlabel('Biela')
    if j==0: ax.set_ylabel('Pedalada núm.')
cax=fig.add_subplot(gs[4]); cb=fig.colorbar(im,cax=cax); cb.set_label('Genoll respecte la pedalada típica (°)',fontsize=9); cb.outline.set_visible(False)
finish(fig,'10','Regularitat de cada pedalada',"Cada fila és una pedalada i cada columna una posició de la biela. El color és quant es diferencia l'angle del genoll respecte la teva pedalada típica d'aquell estil (taronja: més estès, lila: més doblegat). Una estrella marca una pedalada que se'n va del patró.","Files pàl·lides volen dir una pedalada repetible. Les diferències de menys de 5° cauen dins de l'error del seguiment, així que les pedalades que se'n surten (estrelles) són només orientatives.",'10_regularitat_pedalades_mapa.png')
print('pro1 ok')
