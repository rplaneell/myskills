from viz2 import *
L=np.load("/mnt/user-data/working/mp/landmarks.npy")
M=pickle.load(open('/mnt/user-data/working/metrics.pkl','rb')); Mt=M['M']; S=M['S']; df=M['df']; cons=M['cons']
curves=A['curves']; curvesL=A['curvesL']; hipb=A['hipbounce']
typ={}
for k in 'ABCD':
    d=df[df.seg==k].reset_index(drop=True); i=int(np.argmin(cons[k])); typ[k]=(d.start_s[i],d.dur_s[i])
def stroke_idx(k): s0,du=typ[k]; a=int(round(s0*30)); return np.arange(a,a+int(round(du*30))+1)
def frame_at_phase(k,ph):
    idx=stroke_idx(k); dd=np.abs(((phase[idx]-ph+180)%360)-180); return int(idx[np.argmin(dd)])
def mval(k,key): return float(Mt[(Mt.seg==k)&(Mt.key==key)].value.iloc[0])
def mgrade(k,key): return Mt[(Mt.seg==k)&(Mt.key==key)].grade.iloc[0]
def mconf(k,key): return Mt[(Mt.seg==k)&(Mt.key==key)].confidence.iloc[0]
CONF={'High':'Alta','Medium':'Mitjana','Low':'Baixa'}
def cat(v,d=1): return f"{v:.{d}f}".replace('.',',')
ERR=dict(knee=5,hip=5,ankle=8)
def tag_axes(ax,t,color=INK): ax.set_title(t,color=color,loc='left',fontsize=11.5,fontweight='bold',pad=7)
