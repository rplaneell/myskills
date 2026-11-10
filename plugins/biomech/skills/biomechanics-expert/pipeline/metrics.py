import sys, pickle, json; sys.path.insert(0,'/mnt/user-data/working/scripts')
import numpy as np, pandas as pd
A=pickle.load(open('/mnt/user-data/working/an.pkl','rb'))
df=A['df']; curves=A['curves']; T=A['T']; sig=A['sig']; SEG=A['SEG']
# per style consistency: RMS of each stroke's knee curve around the style median curve
cons={}
for k in SEG:
    c=curves[k]['knee']; med=np.median(c,0); rms=np.sqrt(((c-med)**2).mean(1)); cons[k]=rms
    df.loc[df.seg==k,'knee_curve_rms']=rms
# metric rules: key,label,unit,green(lo,hi),amber(lo,hi),err,weight,source
RULES=[
 ('knee_max',"Extensió del genoll, part baixa de la pedalada",'°',(145,155),(140,160),5,3,"Holmes 1994 i Bini 2011 (revisions): uns 25 a 35° de flexió del genoll a l'extensió màxima, és a dir 145 a 155° d'angle interior"),
 ('hip_min_top',"Angle del maluc a dalt de la pedalada",'°',(45,180),(38,180),5,2,"Regla pràctica habitual de bike fit (ajust de la bici): mantenir per sobre de uns 45°. Depèn de la flexibilitat"),
 ('torso_deg',"Angle del tors respecte l'horitzontal",'°',(30,45),(20,55),3,1,"Regla pràctica: 30 a 45° en bici de carretera. Més baix és més aerodinàmic i demana més flexibilitat"),
 ('elbow_deg',"Angle del colze",'°',(150,170),(130,175),5,1.5,"Regla pràctica: un lleuger doblec d'uns 10 a 30°"),
 ('shoulder_deg',"Angle de l'espatlla (tors a braç)",'°',(80,100),(70,110),5,1,"Regla pràctica: uns 90°"),
 ('ankle_rom',"Recorregut del turmell",'°',(15,35),(10,45),8,1,"Els estudis de ciclisme solen donar uns 20 a 30°"),
 ('rpm',"Cadència",'rpm',(80,100),(70,110),2,1.5,"Interval d'entrenament habitual: 80 a 100 rpm (revolucions per minut)"),
 ('rpm_sd',"Regularitat de la cadència (variació)",'rpm',(0,3),(0,5),1,1,"Llindar orientatiu (idea de suavitat inspirada en VeloLens), no és un estàndard publicat"),
 ('torso_sd',"Estabilitat del tors (variació)",'°',(0,2),(0,4),1,1,"Llindar orientatiu: un tors quiet"),
 ('hip_bounce_mm',"Rebot de la pelvis (vertical)",'mm',(0,15),(0,30),8,1,"Llindar orientatiu, no és un estàndard publicat"),
 ('kops_mm',"Genoll respecte la bola del peu a les 3",'mm',(-30,30),(-60,60),35,0.5,"Regla KOPS (genoll sobre l'eix del pedal, sigles angleses). Evidència feble i error gran"),
 ('knee_curve_rms',"Regularitat entre pedalades",'°',(0,3),(0,5),1.5,1,"Llindar orientatiu sobre la dispersió de la corba del genoll"),
]
def val(k,key):
    d=df[df.seg==k]
    f=(T>=SEG[k][1])&(T<=SEG[k][2])
    if key=='rpm': return d.rpm.mean()
    if key=='rpm_sd': return d.rpm.std()
    if key=='torso_sd': return float(np.std(sig['torso'][f]-np.polyval(np.polyfit(T[f],sig['torso'][f],1),T[f])))
    if key=='kops_mm': return d.knee_fwd_of_ball_3oclock_mm.mean()
    return d[key].mean()
def grade(v,r):
    g,a=r[3],r[4]
    if g[0]<=v<=g[1]: return 'green'
    if a[0]<=v<=a[1]: return 'amber'
    return 'red'
PTS={'green':1,'amber':.5,'red':0}
def dist_to_green(v,g):  # signed distance to nearest green edge (0 inside)
    return 0 if g[0]<=v<=g[1] else (g[0]-v if v<g[0] else v-g[1])
rows=[]
for k in SEG:
    for r in RULES:
        key=r[0]; v=val(k,key); err=r[5]
        grd=grade(v,r)
        # error-aware range: move value up to +-err toward / away from green
        cl=lambda x: max(x,0) if r[3][0]==0 else x
        best=min((grade(cl(v+e),r) for e in (-err,0,err)),key=lambda s:-PTS[s]); worst=min((grade(cl(v+e),r) for e in (-err,0,err)),key=lambda s:PTS[s])
        conf='High' if best==worst else ('Medium' if abs(PTS[best]-PTS[worst])==.5 else 'Low')
        sd=df[df.seg==k][key].std() if key in df else np.nan
        rows.append(dict(seg=k,style=SEG[k][0],key=key,label=r[1],unit=r[2],value=v,err=err,grade=grd,grade_best=best,grade_worst=worst,confidence=conf,weight=r[6],source=r[7],stroke_sd=sd))
M=pd.DataFrame(rows)
def score(sub,col):
    return 100*sum(w*PTS[g] for w,g in zip(sub.weight,sub[col]))/sub.weight.sum()
S={}
rng=np.random.default_rng(1)
def mc(sub):
    out=[]
    for _ in range(3000):
        pts=0
        for _,rw in sub.iterrows():
            r=[x for x in RULES if x[0]==rw.key][0]
            v=rw.value+rng.normal(0,rw.err/2)   # err treated as a roughly 95% bound
            if r[3][0]==0: v=max(v,0)
            pts+=rw.weight*PTS[grade(v,r)]
        out.append(100*pts/sub.weight.sum())
    return np.percentile(out,5),np.percentile(out,95)
for k in ['A','B','D']:
    sub=M[M.seg==k]; lo,hi=mc(sub); S[k]=dict(score=score(sub,'grade'),lo=lo,hi=hi)
dur={k:SEG[k][2]-SEG[k][1] for k in S}
tot=sum(dur.values())
S['overall']={q:sum(S[k][q]*dur[k] for k in dur)/tot for q in ('score','lo','hi')}
M.to_csv('/home/user/ride_analysis/data/metrics_by_style.csv',index=False)
json.dump(S,open('/mnt/user-data/working/scores.json','w'),indent=1)
pickle.dump(dict(M=M,S=S,cons=cons,df=df),open('/mnt/user-data/working/metrics.pkl','wb'))
if __name__=='__main__':
    pd.set_option('display.width',250); pd.set_option('display.max_rows',100)
    print(M[['seg','key','value','err','grade','grade_best','grade_worst','confidence']].round(1).to_string())
    print(json.dumps(S,indent=1))
