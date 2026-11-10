import sys, pickle; sys.path.insert(0,'/mnt/user-data/working/scripts')
from common import *
import pandas as pd
T=np.arange(len(L))/FPS
SEG={'A':('Assegut dret, mans a les manetes',1.0,8.6),
     'B':('Assegut baix, a la part baixa del manillar',11.0,17.2),
     'C':('Dret sobre els pedals',18.9,21.4),
     'D':('Assegut dret un altre cop (final)',23.7,25.6)}
MM=3.06   # mm per pixel, calibrated from height 1.735 m with standard body proportions (+-8%)
def S(n,fc,side='R'): return lp(P(n,side),fc)
R={n:S(n,8 if n in('knee','ank','heel','toe','hip') else 5) for n in ['ear','sh','el','wr','hip','knee','ank','heel','toe']}
Lf={n:S(n,8 if n in('knee','ank','heel','toe','hip') else 5,'L') for n in ['sh','hip','knee','ank','heel','toe']}
ear,sh,el,wr,hip,knee,ank,heel,toe=[R[n] for n in ['ear','sh','el','wr','hip','knee','ank','heel','toe']]
ball=heel+0.72*(toe-heel)
def signals(sh,hip,knee,ank,heel,toe):
    return dict(knee=ang3(hip,knee,ank),hip=ang3(sh,hip,knee),ankle=ang3(knee,ank,toe),
      foot_pitch=np.degrees(np.arctan2((heel[:,1]-toe[:,1]),(toe[:,0]-heel[:,0]))))
sig=signals(sh,hip,knee,ank,heel,toe)
sig['elbow']=ang3(sh,el,wr); sig['shoulder']=ang3(hip,sh,el)
sig['torso']=np.degrees(np.arctan2(-(sh[:,1]-hip[:,1]), sh[:,0]-hip[:,0]))
sig['neck']=ang3(ear,sh,hip); sig['head_fwd_mm']=(ear[:,0]-sh[:,0])*MM
sigL=signals(Lf['sh'],Lf['hip'],Lf['knee'],Lf['ank'],Lf['heel'],Lf['toe'])
hipbounce=(hip[:,1]-lp(hip[:,1],0.5))*MM
sig['knee_fwd_of_ball_mm']=(knee[:,0]-ball[:,0])*MM
def circfit(xy):
    A=np.c_[2*xy[:,0],2*xy[:,1],np.ones(len(xy))]; b=(xy**2).sum(1)
    c=np.linalg.lstsq(A,b,rcond=None)[0]; return c[:2], np.sqrt(c[2]+c[0]**2+c[1]**2)
rel=ball-hip
phase=np.full(len(T),np.nan); bbpos={}
for k,(nm,t0,t1) in SEG.items():
    f=(T>=t0-0.8)&(T<=t1+0.8)
    c,r=circfit(rel[(T>=t0)&(T<=t1)]); bbpos[k]=c
    d=rel[f]-c
    phase[f]=np.degrees(np.arctan2(d[:,0],-d[:,1]))%360   # 0 top, 90 front(right), 180 bottom, 270 back
grid=np.arange(360)
curves={k:{} for k in SEG}; curvesL={k:{} for k in SEG}; rows=[]; strokeinfo=[]
for k,(nm,t0,t1) in SEG.items():
    f=np.where((T>=t0-0.8)&(T<=t1+0.8))[0]
    ph=phase[f]; wraps=f[1:][np.diff(ph)<-180]   # frames where phase wrapped 359->0
    for a,b in zip(wraps[:-1],wraps[1:]):
        if T[a]<t0-0.05 or T[b]>t1+0.05: continue
        n=b-a
        if n<int(0.4*FPS) or n>int(1.3*FPS): continue
        idx=np.arange(a,b); p=np.maximum.accumulate(phase[idx]); 
        if p[-1]-p[0]<300: continue
        def rs(x): return np.interp(grid,p,x[idx])
        cur={s:rs(v) for s,v in sig.items()}
        for s in ['knee','hip','ankle','foot_pitch']: curvesL[k].setdefault(s,[]).append(np.interp((grid+180)%360, p, sigL[s][idx]) if False else np.interp(grid,(p+180)%360 if False else p,sigL[s][idx]))
        for s,v in cur.items(): curves[k].setdefault(s,[]).append(v)
        d=dict(seg=k,start_s=round(T[a],2),dur_s=n/FPS,rpm=60*FPS/n)
        d['knee_bdc']=cur['knee'][180]; d['knee_tdc']=cur['knee'][0]; d['knee_max']=cur['knee'].max(); d['knee_min']=cur['knee'].min()
        d['hip_min_top']=cur['hip'].min(); d['hip_max']=cur['hip'].max(); d['hip_rom']=np.ptp(cur['hip'])
        d['ankle_min']=cur['ankle'].min(); d['ankle_max']=cur['ankle'].max(); d['ankle_rom']=np.ptp(cur['ankle'])
        d['foot_pitch_rom']=np.ptp(cur['foot_pitch']); d['heel_drop_deg_bdc']=-cur['foot_pitch'][180]
        d['torso_deg']=cur['torso'].mean(); d['elbow_deg']=cur['elbow'].mean(); d['shoulder_deg']=cur['shoulder'].mean()
        d['neck_deg']=cur['neck'].mean(); d['head_fwd_mm']=cur['head_fwd_mm'].mean()
        d['knee_fwd_of_ball_3oclock_mm']=cur['knee_fwd_of_ball_mm'][90]
        d['hip_bounce_mm']=np.ptp(hipbounce[idx])
        w=np.abs(np.gradient(np.unwrap(np.radians(phase[idx])))); w=lp(w,5)
        d['slowest_pct_of_mean']=100*w.min()/w.mean()
        d['slowest_at_deg']=float(phase[idx][np.argmin(w)])
        rows.append(d)
df=pd.DataFrame(rows)
for k in curves:
    for s in curves[k]: curves[k][s]=np.array(curves[k][s])
    for s in curvesL[k]: curvesL[k][s]=np.array(curvesL[k][s])
# torso drift per segment (deg per 10 s), cadence
drift={}
for k,(nm,t0,t1) in SEG.items():
    f=(T>=t0)&(T<=t1); drift[k]=np.polyfit(T[f],sig['torso'][f],1)[0]*10
df.to_csv('/mnt/user-data/working/strokes.csv',index=False)
pickle.dump(dict(T=T,sig=sig,sigL=sigL,pts=dict(R=R,L=Lf,ball=ball),phase=phase,SEG=SEG,curves=curves,curvesL=curvesL,df=df,drift=drift,MM=MM,bb=bbpos,hipbounce=hipbounce),open('/mnt/user-data/working/an.pkl','wb'))
pd.set_option('display.width',250)
print(df.groupby('seg').size().to_dict())
print(df.drop(columns=['start_s']).groupby('seg').agg(['mean','std']).round(1).T.to_string())
print('torso drift deg/10s',{k:round(v,1) for k,v in drift.items()})
