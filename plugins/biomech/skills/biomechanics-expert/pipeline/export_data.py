import pandas as pd
from common2 import *
import csv
D='/home/user/ride_analysis/data/'
# per stroke
ren={'seg':'estil_codi','start_s':'inici_s','dur_s':'durada_s','rpm':'cadencia_rpm','knee_bdc':'genoll_a_les_6_graus','knee_tdc':'genoll_a_les_12_graus','knee_max':'genoll_extensio_maxima_graus','knee_min':'genoll_minim_graus','hip_min_top':'maluc_minim_a_dalt_graus','hip_max':'maluc_maxim_graus','hip_rom':'maluc_recorregut_graus','ankle_min':'turmell_minim_graus','ankle_max':'turmell_maxim_graus','ankle_rom':'turmell_recorregut_graus','foot_pitch_rom':'peu_inclinacio_recorregut_graus','heel_drop_deg_bdc':'peu_punta_avall_a_les_6_graus','torso_deg':'tors_graus','elbow_deg':'colze_graus','shoulder_deg':'espatlla_graus','neck_deg':'coll_graus','head_fwd_mm':'cap_davant_espatlla_mm','knee_fwd_of_ball_3oclock_mm':'genoll_respecte_bola_peu_a_les_3_mm','hip_bounce_mm':'rebot_pelvis_mm','slowest_pct_of_mean':'velocitat_minima_pct_de_la_mitjana','slowest_at_deg':'velocitat_minima_posicio_biela_graus','knee_curve_rms':'dispersio_corba_genoll_graus'}
d=df.rename(columns=ren); d.insert(1,'estil',d.estil_codi.map({'A':'Estil 1 assegut dret','B':'Estil 2 assegut baix','C':'Estil 3 dret','D':'Estil 1 final'})); d.round(2).to_csv(D+'pedalades.csv',index=False,encoding='utf-8-sig')
# per frame
fr=pd.DataFrame({'temps_s':T.round(3),'fotograma':np.arange(len(T)),'estil_codi':[next((k for k,(n,a,b) in SEG.items() if a<=t<=b),'') for t in T],'posicio_biela_graus':np.round(phase,1),
 'genoll_graus':sig['knee'].round(1),'maluc_graus':sig['hip'].round(1),'turmell_graus':sig['ankle'].round(1),'colze_graus':sig['elbow'].round(1),'espatlla_graus':sig['shoulder'].round(1),'tors_graus':sig['torso'].round(1),'coll_graus':sig['neck'].round(1),'rebot_pelvis_mm':hipb.round(1)})
for n,l in [('hip','maluc'),('knee','genoll'),('ank','turmell'),('sh','espatlla'),('el','colze'),('wr','canell'),('toe','punta_peu'),('heel','taló')]:
    fr[f'{l}_x_px']=np.array(R[n])[:,0].round(1); fr[f'{l}_y_px']=np.array(R[n])[:,1].round(1)
fr.to_csv(D+'fotogrames_angles_i_posicions.csv',index=False,encoding='utf-8-sig')
# metrics by style
m=Mt.rename(columns={'seg':'estil_codi','style':'estil','key':'clau','label':'mesura','unit':'unitat','value':'valor','err':'error_estimat','grade':'semafor','grade_best':'semafor_millor_cas','grade_worst':'semafor_pitjor_cas','confidence':'confianca','weight':'pes_a_la_puntuacio','source':'font_o_motiu','stroke_sd':'desviacio_entre_pedalades'})
m['semafor']=m.semafor.map({'green':'verd','amber':'ambre','red':'vermell'}); m['semafor_millor_cas']=m.semafor_millor_cas.map({'green':'verd','amber':'ambre','red':'vermell'}); m['semafor_pitjor_cas']=m.semafor_pitjor_cas.map({'green':'verd','amber':'ambre','red':'vermell'}); m['confianca']=m.confianca.map(CONF)
m.round(2).to_csv(D+'mesures_per_estil_amb_semafor.csv',index=False,encoding='utf-8-sig')
# summary
g=df.groupby('seg').agg(pedalades=('rpm','size'),cadencia_rpm=('rpm','mean'),cadencia_variacio=('rpm','std'),genoll_ext_max=('knee_max','mean'),maluc_min_dalt=('hip_min_top','mean'),tors=('torso_deg','mean'),colze=('elbow_deg','mean'),turmell_recorregut=('ankle_rom','mean'),rebot_pelvis_mm=('hip_bounce_mm','mean')).round(1)
g.index=['Estil 1 (A)','Estil 2 (B)','Estil 3 (C)','Estil 1 final (D)']; g.to_csv(D+'resum_per_estil.csv',encoding='utf-8-sig'); print(g)
import json; json.dump({'puntuacions':{k:{kk:round(vv,1) for kk,vv in v.items()} for k,v in S.items()}},open(D+'puntuacions.json','w'),indent=1,ensure_ascii=False)
open('/home/user/ride_analysis/.gitignore','w').write('# Secrets: never upload\n.env\n*.env\n')
open('/home/user/ride_analysis/.env.example','w').write('# This project needs no API keys. If one is ever needed, copy this file to .env and fill it in locally.\n# EXAMPLE_API_KEY=\n')
