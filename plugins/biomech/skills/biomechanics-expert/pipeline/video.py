from common2 import *
import subprocess, cv2
S_=1.5; VW,VH=int(464*S_)//2*2,int(832*S_)//2*2
knee=sig['knee']; hipa=sig['hip']
def seg_of(t):
    for k,(nm,a,b) in SEG.items():
        if a-0.5<=t<=b+0.3: return k
    return None
LAB={'A':'Estil 1 · assegut dret','B':'Estil 2 · assegut baix','C':'Estil 3 · dret sobre els pedals','D':'Estil 1 · assegut dret'}
def frame(i):
    im=getframe(i); pil=skel(im,i,2,labels=('knee','hip','elbow'),fs=26,lw=4,jr=6).resize((VW,VH),Image.LANCZOS).convert('RGBA')
    lay=Image.new('RGBA',pil.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    t=i/30; k=seg_of(t)
    txt=LAB.get(k,'transició entre estils'); col=STYLE.get(k,'#8a94a3')
    d.rounded_rectangle([14,14,14+d.textlength(txt,font=F(26,'SemiBold'))+52,66],radius=14,fill=(16,32,46,215)); d.ellipse([26,32,44,50],fill=hx(col)); d.text((54,24),txt,font=F(26,'SemiBold'),fill=(255,255,255,255))
    d.text((20,76),f"t = {t:4.1f} s",font=F(22,'Medium'),fill=(255,255,255,235))
    # live graph (bottom left), last 3 s
    gx,gy,gw,gh=14,VH-236,330,220; d.rounded_rectangle([gx,gy,gx+gw,gy+gh],radius=14,fill=(16,32,46,205))
    d.text((gx+14,gy+10),'Angles (últims 3 s)',font=F(20,'Medium'),fill=(255,255,255,235))
    a=max(0,i-90); xs=np.arange(a,i+1)
    def pts(arr,lo,hi): return [(gx+14+(x-(i-90))/90*(gw-28), gy+gh-22-(v-lo)/(hi-lo)*(gh-70)) for x,v in zip(xs,arr[a:i+1])]
    for v in (60,90,120,150): yy=gy+gh-22-(v-30)/(170-30)*(gh-70); d.line([(gx+14,yy),(gx+gw-14,yy)],fill=(255,255,255,40),width=1)
    if len(xs)>2:
        d.line(pts(knee,30,170),fill=hx('#56d4ff'),width=3); d.line(pts(hipa,30,170),fill=hx('#ffd166'),width=3)
        px,py=pts(knee,30,170)[-1]; d.ellipse([px-5,py-5,px+5,py+5],fill=hx('#56d4ff')); px,py=pts(hipa,30,170)[-1]; d.ellipse([px-5,py-5,px+5,py+5],fill=hx('#ffd166'))
    d.text((gx+14,gy+gh-24),'genoll',font=F(18,'Medium'),fill=hx('#56d4ff')); d.text((gx+92,gy+gh-24),'maluc',font=F(18,'Medium'),fill=hx('#ffd166'))
    d.text((gx+gw-150,gy+gh-24),f"{knee[i]:.0f}°  {hipa[i]:.0f}°",font=F(18,'SemiBold'),fill=(255,255,255,235))
    # crank clock bottom right
    ph=phase[i]
    if not np.isnan(ph):
        cx,cy,r=VW-64,VH-64,44; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(16,32,46,205),outline=(255,255,255,200),width=2)
        for aa in (0,90,180,270): tt=math.radians(aa); d.line([(cx+r*.8*math.sin(tt),cy-r*.8*math.cos(tt)),(cx+r*.95*math.sin(tt),cy-r*.95*math.cos(tt))],fill=(255,255,255,200),width=2)
        tt=math.radians(ph); d.line([(cx,cy),(cx+r*.75*math.sin(tt),cy-r*.75*math.cos(tt))],fill=hx(ST['amber']),width=5); d.ellipse([cx-5,cy-5,cx+5,cy+5],fill=(255,255,255,255))
    return Image.alpha_composite(pil,lay).convert('RGB')
vp='/home/user/ride_analysis/video/ride_annotated_raw.mp4'; out='/home/user/ride_analysis/video/pedalada_anotada.mp4'
vw=cv2.VideoWriter(vp,cv2.VideoWriter_fourcc(*'mp4v'),30,(VW,VH))
for i in range(len(T)): vw.write(cv2.cvtColor(np.array(frame(i)),cv2.COLOR_RGB2BGR))
vw.release()
subprocess.run(['ffmpeg','-y','-v','error','-i',vp,'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out],check=True)
import os; os.remove(vp); print('video',os.path.getsize(out)//1024,'KB')
# ---------- GIF: one clean stroke (typical stroke of style 1), slowed down 3x
idx=stroke_idx('A'); frames=[]
for i in idx:
    im=crop(skel(getframe(i),i,2,labels=('knee','hip','elbow','ankle'),fs=30,lw=5,jr=7),2); im=im.resize((int(im.width*.8),int(im.height*.8)),Image.LANCZOS)
    d=ImageDraw.Draw(im); clock(im,60,70,40,phase[i]); d.rounded_rectangle([110,30,110+330,86],radius=14,fill=(16,32,46)); d.text((126,40),'Estil 1 · una pedalada · càmera lenta',font=F(20,'Medium'),fill='white')
    frames.append(im)
frames[0].save('/home/user/ride_analysis/video/una_pedalada.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
print('gif',len(frames),'frames',os.path.getsize('/home/user/ride_analysis/video/una_pedalada.gif')//1024,'KB')
