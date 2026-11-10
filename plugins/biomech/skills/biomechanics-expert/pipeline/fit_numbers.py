"""Step 4b: numbers behind the fit advice (saddle height, handlebar stack, reach).
Reads an.pkl made by analyse2.py and writes fitnums.json, which pro3.py and pro3b.py read."""
import sys, json, math, pickle; sys.path.insert(0,'/mnt/user-data/working/scripts')
import numpy as np
A=pickle.load(open('/mnt/user-data/working/an.pkl','rb')); R=A['pts']['R']; T=A['T']; MM=A['MM']; SEG=A['SEG']
n=lambda a,b:np.linalg.norm(R[a]-R[b],axis=1)
k0=list(SEG)[0]; f=(T>=SEG[k0][1])&(T<=SEG[k0][2])           # first seated segment
thigh=np.median(n('hip','knee')[f])*MM; shank=np.median(n('knee','ank')[f])*MM; torso=np.median(n('hip','sh')[f])*MM
ua=np.median(n('sh','el')[f])*MM; fo=np.median(n('el','wr')[f])*MM
knee_max=float(np.mean(A['curves'][k0]['knee'].max(1))) if 'curves' in A else 154.0
elbow=float(np.mean(A['curves'][k0]['elbow'].mean(1))) if 'curves' in A else 138.0
th=math.radians(knee_max); L=math.sqrt(thigh**2+shank**2-2*thigh*shank*math.cos(th)); mm_per_deg_knee=thigh*shank*math.sin(th)/L*math.pi/180
eb=math.radians(elbow); ch=math.sqrt(ua**2+fo**2-2*ua*fo*math.cos(eb)); mm_per_deg_elbow=ua*fo*math.sin(eb)/ch*math.pi/180
out=dict(thigh=thigh,shank=shank,torso=torso,ua=ua,fo=fo,mm_per_deg_knee=mm_per_deg_knee,mm_per_deg_elbow=mm_per_deg_elbow,deg_per_mm_torso=math.degrees(1/torso))
json.dump({k:float(v) for k,v in out.items()},open('/mnt/user-data/working/fitnums.json','w')); print(out)
