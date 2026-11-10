import numpy as np
from scipy.signal import butter, filtfilt
FPS=30.0
L=np.load('/mnt/user-data/working/mp/landmarks.npy')  # frames x 33 x (x,y,vis,pres)
IDX=dict(ear=8,sh=12,el=14,wr=16,hip=24,knee=26,ank=28,heel=30,toe=32,
         Lsh=11,Lel=13,Lwr=15,Lhip=23,Lknee=25,Lank=27,Lheel=29,Ltoe=31)
def P(name,side='R'):
    k=IDX[name] if side=='R' else IDX['L'+name]
    return L[:,k,:2].copy()
def lp(x,fc=6.0,order=2):
    b,a=butter(order,fc/(FPS/2)); 
    x=np.asarray(x,float)
    if x.ndim==1: return filtfilt(b,a,x)
    return np.stack([filtfilt(b,a,x[:,i]) for i in range(x.shape[1])],1)
def ang3(a,b,c):
    """interior angle at b between points a-b-c, degrees"""
    v1=a-b; v2=c-b
    cs=(v1*v2).sum(1)/(np.linalg.norm(v1,axis=1)*np.linalg.norm(v2,axis=1)+1e-9)
    return np.degrees(np.arccos(np.clip(cs,-1,1)))
