import sys; sys.path.insert(0,'/mnt/user-data/working/scripts')
import base64, io, json, pickle, math, html
import pandas as pd, numpy as np
from PIL import Image
sys.path.insert(0,'/mnt/user-data/working/scripts')
import importlib; mt=importlib.import_module('metrics')
M=pickle.load(open('/mnt/user-data/working/metrics.pkl','rb')); Mt=M['M']; S=M['S']; df=M['df']
IM='/home/user/ride_analysis/images/'; WEB='/home/user/ride_analysis/images_web/'
import os; os.makedirs(WEB,exist_ok=True)
def b64(path,q=84,w=1800):
    im=Image.open(path).convert('RGB'); 
    if im.width>w: im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=q,optimize=True,progressive=True); open(WEB+os.path.basename(path).replace('.png','.jpg'),'wb').write(buf.getvalue()); return base64.b64encode(buf.getvalue()).decode()
figs={}
for f in sorted(os.listdir(IM)):
    if f.endswith('.png'): figs[f[:2]]=(f,b64(IM+f))
def fig(n,alt): return f'<figure id="fig{n}"><img src="data:image/jpeg;base64,{figs[n][1]}" alt="{html.escape(alt)}" loading="lazy"></figure>'
gif=base64.b64encode(open('/home/user/ride_analysis/video/una_pedalada.gif','rb').read()).decode()
c1=lambda v,d=0: f"{v:.{d}f}".replace('.',',')
g=df.groupby('seg').agg(n=('rpm','size'),rpm=('rpm','mean'),sd=('rpm','std'))
def chip(gr): return {'green':'<span class="chip g">● BÉ</span>','amber':'<span class="chip a">▲ ATENCIÓ</span>','red':'<span class="chip r">■ PROBLEMA</span>'}[gr]
rules=''
for r in mt.RULES:
    gr,am=r[3],r[4]
    def rng(x,u): 
        lo,hi=x; 
        if lo<=-1000 or lo==0 and hi<200 and hi!=180: pass
        if lo<0: return f"fins a {c1(abs(lo))} {u} darrere o {c1(hi)} {u} davant"
        if hi>=180: return f"més de {c1(lo)} {u}"
        if lo==0: return f"menys de {c1(hi)} {u}"
        return f"{c1(lo)} a {c1(hi)} {u}"
    rules+=f"<tr><td>{html.escape(r[1])}</td><td>{rng(gr,r[2])}</td><td>{rng(am,r[2])}</td><td>±{c1(r[5])} {r[2]}</td><td class='src'>{html.escape(r[7])}</td></tr>"
tile=lambda lab,val,sub,cls='': f'<div class="tile {cls}"><div class="tl">{lab}</div><div class="tv">{val}</div><div class="ts">{sub}</div></div>'
tiles=''.join([tile('Puntuació global',f"{S['overall']['score']:.0f}<small>/100</small>",f"interval probable {S['overall']['lo']:.0f} a {S['overall']['hi']:.0f} · confiança mitjana"),
 tile('Estil 1 · assegut dret',f"{S['A']['score']:.0f}<small>/100</small>",f"interval {S['A']['lo']:.0f} a {S['A']['hi']:.0f}",'s1'),tile('Estil 2 · assegut baix',f"{S['B']['score']:.0f}<small>/100</small>",f"interval {S['B']['lo']:.0f} a {S['B']['hi']:.0f}",'s2'),
 tile('Alçada del selló','Mantenir','genoll estès 154° i 153°, dins de 145 a 155°','ok')])
cad=''.join(f"<tr><td>{n}</td><td>{int(g.loc[k,'n'])}</td><td>{c1(g.loc[k,'rpm'],0)} rpm</td><td>±{c1(g.loc[k,'sd'],1)} rpm</td></tr>" for k,n in [('A','Estil 1 · assegut dret'),('B','Estil 2 · assegut baix'),('C','Estil 3 · dret sobre els pedals'),('D','Estil 1 final · assegut dret')])
H=f'''<!doctype html><html lang="ca"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anàlisi de pedalada i posició</title>
<style>
:root{{--ink:#16202e;--muted:#5b6675;--faint:#98a2b0;--rule:#d9dee5;--panel:#f4f6f9;--accent:#0a4d8c;--g:#009E73;--a:#E69F00;--r:#D55E00;--bg:#fff}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--ink:#e8edf3;--muted:#a3adba;--faint:#6f7a88;--rule:#2a3441;--panel:#18212c;--accent:#6db3f2;--bg:#0f151d}}}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 20px}}
nav{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule)}}
nav .wrap{{display:flex;gap:18px;overflow-x:auto;padding:12px 20px;font-size:13px;white-space:nowrap}}nav a{{color:var(--muted);text-decoration:none;font-weight:500}}nav a:hover{{color:var(--accent)}}
header.cover{{padding:64px 0 36px;border-bottom:1px solid var(--rule)}}.eyebrow{{letter-spacing:.16em;text-transform:uppercase;font-size:12px;font-weight:600;color:var(--accent)}}
h1{{font-size:clamp(32px,5vw,52px);line-height:1.1;margin:10px 0 12px;font-weight:650;letter-spacing:-.02em}}.lead{{font-size:19px;color:var(--muted);max-width:760px;margin:0}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:30px 0 8px}}.tile{{background:var(--panel);border-top:4px solid var(--ink);padding:16px 18px 14px}}.tile.s1{{border-color:#0072B2}}.tile.s2{{border-color:#CC79A7}}.tile.ok{{border-color:var(--g)}}
.tl{{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}}.tv{{font-size:38px;font-weight:650;line-height:1.15;margin:4px 0}}.tv small{{font-size:15px;color:var(--muted);font-weight:500;margin-left:4px}}.ts{{font-size:13px;color:var(--muted)}}
section{{padding:44px 0 6px;border-bottom:1px solid var(--rule)}}section:last-of-type{{border:0}}h2{{font-size:28px;margin:0 0 6px;letter-spacing:-.01em}}h2 .n{{color:var(--accent);font-weight:600;font-size:14px;letter-spacing:.14em;display:block;margin-bottom:6px}}
p{{max-width:780px}}.k{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin:18px 0 8px}}.k div{{background:var(--panel);padding:14px 16px;border-left:3px solid var(--accent);font-size:15px}}.k b{{display:block;margin-bottom:2px}}
figure{{margin:26px 0;padding:0}}figure img{{width:100%;height:auto;display:block;border:1px solid var(--rule);background:#fff}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:16px 0}}th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--rule);vertical-align:top}}th{{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}td.src{{color:var(--muted);font-size:13px}}
.chip{{font-weight:650;font-size:12px;white-space:nowrap}}.chip.g{{color:var(--g)}}.chip.a{{color:#9a6a00}}.chip.r{{color:var(--r)}}
.note{{background:var(--panel);border-left:3px solid var(--a);padding:12px 16px;margin:18px 0;font-size:15px;max-width:820px}}.note.bad{{border-color:var(--r)}}
pre{{background:#0f1720;color:#e6edf3;padding:16px;overflow:auto;font-size:13px;line-height:1.55;border-radius:6px}}code{{font-family:"JetBrains Mono",ui-monospace,monospace}}
video,.gifwrap img{{max-width:100%;border:1px solid var(--rule)}}.media{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;align-items:start;margin:20px 0}}.media figcaption{{font-size:14px;color:var(--muted);margin-top:8px}}
dl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;font-size:15px;max-width:860px}}dt{{font-weight:650}}dd{{margin:0;color:var(--muted)}}
footer{{padding:30px 0 60px;color:var(--faint);font-size:13px}}
@media print{{video{{display:none}}nav{{display:none}}section{{break-inside:auto}}figure{{break-inside:avoid}}header.cover{{padding-top:10px}}.tile,.k div{{break-inside:avoid}}}}
@media (max-width:600px){{section{{padding-top:30px}}}}
</style></head><body>
<nav><div class="wrap"><a href="#resum">Resum</a><a href="#video">El vídeo</a><a href="#dades">Dades</a><a href="#semafor">Semàfor</a><a href="#incertesa">Incertesa</a><a href="#millores">Millores</a><a href="#ajust">Ajust i mida</a><a href="#reprova">Repetir la prova</a><a href="#eines">Eines</a><a href="#glossari">Glossari</a></div></nav>
<header class="cover"><div class="wrap"><div class="eyebrow">Biomecànica de la pedalada · ajust de la bici</div><h1>La teva pedalada i la teva posició</h1><p class="lead">Anàlisi d'un vídeo lateral de 26 segons, rodet interior, amb tres estils de pedalar. Alçada de referència: 1,735 m. Vídeo del 28 d'octubre de 2026.</p>
<div class="tiles">{tiles}</div></div></header>
<main class="wrap">
<section id="resum"><h2><span class="n">01 · RESUM</span>El que cal saber en un minut</h2>
<div class="k"><div><b>El genoll i el selló estan bé</b>Extensió màxima de 154° i 153° (zona recomanada, 145 a 155°). La càmera no justifica cap canvi d'alçada de selló.</div>
<div><b>L'estil 1 és molt bo</b>Assegut dret, mans a les manetes: maluc a 47°, tors a 33°, pedalada molt regular. Només els colzes van doblegats (138°) i la cadència és de 79 rpm.</div>
<div><b>L'estil 2 és on cal millorar</b>A la part baixa, el maluc es tanca a 32° (problema, confiança alta), el tors és a 17° i els colzes a 104°. La pelvis rebota 23 mm.</div>
<div><b>Tres canvis, un cada cop</b>1) manillar +10 mm; 2) colzes suaus i, si cal, potència +10 mm; 3) selló 3 mm més baix només si el rebot continua.</div>
<div><b>Mida de quadre</b>Millor estimació 54 (M), però ets a la frontera amb la 52. Cal la teva entrecuixa per afinar.</div>
<div><b>Confiança mitjana</b>Vídeo curt (26 s), 30 imatges per segon i càmera a la mà. La cama esquerra no es pot mesurar. A l'apartat 'Repetir la prova' hi ha el que la pujaria.</div></div>
{fig('18','Escala de prioritats')}{fig('11','Fitxa de puntuació')}</section>
<section id="video"><h2><span class="n">02 · EL VÍDEO</span>Què he vist i què es pot mesurar</h2>
<table><tr><th>Dada</th><th>Valor</th></tr><tr><td>Format</td><td>464 x 832 píxels, vertical · 30 imatges per segon · 25,8 s (775 fotogrames)</td></tr><tr><td>Càmera</td><td>Lateral, costat dret (costat de la cadena), a la mà i amb petits moviments</td></tr><tr><td>Seguiment</td><td>MediaPipe Pose Landmarker (model heavy): 775 de 775 fotogrames detectats, confiança mínima superior a 0,96 a la cama dreta</td></tr><tr><td>Tres estils</td><td>Assegut dret a les manetes (1,0 a 8,6 s), assegut baix (11,0 a 17,2 s), dret sobre els pedals (18,9 a 21,4 s) i un breu retorn a l'estil 1 (23,7 a 25,6 s)</td></tr></table>
<div class="note"><b>Es pot mesurar bé:</b> genoll, maluc, tors, colze, espatlla i cadència de la cama dreta. <b>No es pot mesurar bé:</b> cama esquerra, asimetria, alineació de les falques, fatiga real (el vídeo és massa curt) i qualsevol canvi de menys de 5°.</div>
{fig('01','Comprovació del seguiment')}{fig('02','Tres estils de pedalar')}</section>
<section id="dades"><h2><span class="n">03 · DADES</span>Cadència i angles al llarg de la pedalada</h2>
<table><tr><th>Estil</th><th>Pedalades</th><th>Cadència</th><th>Variació</th></tr>{cad}</table>
<p>La posició de la biela s'expressa com un rellotge: les 12 són dalt de tot i les 6 a baix de tot. La cadència es mesura en rpm (revolucions per minut).</p>
{fig('03','Quatre posicions')}{fig('06','Angles contra posició de la biela')}{fig('07','Genoll polar')}
<div class="media"><figure style="margin:0"><video controls preload="metadata" src="../video/pedalada_anotada.mp4" poster=""></video><figcaption>Vídeo anotat amb esquelet, angles i un petit gràfic en directe (fitxer: video/pedalada_anotada.mp4).</figcaption></figure>
<figure class="gifwrap" style="margin:0"><img src="data:image/gif;base64,{gif}" alt="Una pedalada en càmera lenta"><figcaption>Una pedalada neta de l'estil 1 en càmera lenta (fitxer: video/una_pedalada.gif).</figcaption></figure></div></section>
<section id="semafor"><h2><span class="n">04 · SEMÀFOR</span>Comparació amb els intervals habituals</h2>
<p>Cap xifra és una llei: el teu cos, el teu estil i el teu objectiu compten. Els intervals són regles pràctiques de bike fit (ajust de la bici), amb font o motiu a la darrera columna. Cada valor té un marge d'error estimat; si la diferència és més petita que l'error, no en trec conclusions.</p>
<table><tr><th>Mesura</th><th>Verd</th><th>Ambre</th><th>Error</th><th>Font o motiu</th></tr>{rules}</table>
{fig('04','Mapa del cos')}{fig('05','Superposició amb la referència')}</section>
<section id="incertesa"><h2><span class="n">05 · INCERTESA</span>Què és fiable i què no</h2>
<p>Els estudis publicats donen errors d'uns 3 a 10° al maluc i al genoll en cicling, i pitjors al turmell. He fet servir ±5° (maluc i genoll), ±8° (turmell) i ±3° (tors), ±8% en mil·límetres. La puntuació surt de simular aquests errors, per això té un interval.</p>
{fig('08','Esquerra contra dreta')}{fig('09','Deriva')}{fig('10','Regularitat')}</section>
<section id="millores"><h2><span class="n">06 · MILLORES</span>Tres canvis, ordenats</h2>
{fig('15','Millora 1')}{fig('16','Millora 2')}{fig('17','Millora 3')}{fig('19','Exercicis')}
<div class="note bad"><b>Quan anar a un professional:</b> dolor al davant del maluc o lumbar a l'estil baix, formigueig a les mans, dolor de genoll que no marxa o sensació que una cama treballa menys. Un vídeo no diagnostica res.</div></section>
<section id="ajust"><h2><span class="n">07 · AJUST I MIDA</span>Selló, manillar i quadre</h2>
{fig('13','Canvis dajust')}{fig('14','Mida de quadre i gravel')}
<div class="note">Les taules de geometria de cada marca no s'han pogut verificar des d'aquí. La llista de bicis és una guia general: contrasta stack (alçada de la davantera) i reach (abast) a la web oficial de la mida 54 abans de decidir.</div></section>
<section id="reprova"><h2><span class="n">08 · REPETIR LA PROVA</span>Com pujar la confiança</h2>
{fig('20','Muntatge de gravació')}{fig('12','Plantilla abans i després')}{fig('21','Per pujar la confiança')}</section>
<section id="eines"><h2><span class="n">09 · EINES</span>Què s'ha fet servir i què no</h2>
<table><tr><th>Eina</th><th>Estat</th></tr>
<tr><td>Sports2D (model RTMPose)</td><td><b>Instal·lat, però no s'ha pogut executar aquí.</b> El model es baixa de download.openmmlab.com i huggingface.co, i la xarxa d'aquest entorn els bloqueja (error 403). No s'han inventat resultats: no hi ha fitxers TRC (posicions) ni MOT (angles) d'aquesta eina.</td></tr>
<tr><td>MediaPipe (Google)</td><td>Ha fet tota la mesura. Per tant, la comparació de 5° entre dues eines encara no es pot fer.</td></tr>
<tr><td>Pose2Sim</td><td>No cal: només hi ha una càmera.</td></tr>
<tr><td>VeloLens</td><td>Només com a idea (suavitat, cadència, extensió del genoll, estabilitat). No s'ha executat.</td></tr>
<tr><td>Claus d'API</td><td>No n'ha calgut cap. Com a prevenció, la carpeta té un .gitignore que exclou .env i un .env.example buit.</td></tr></table>
<p><b>Per executar Sports2D al teu ordinador</b> (en una carpeta amb ride.mp4), una vegada per tram:</p>
<pre><code>pip install sports2d -U
sports2d --video_input ride.mp4 --nb_persons_to_detect 1 --visible_side right --first_person_height 1.735 \\
  --joint_angles "right knee" "right hip" "right ankle" "right elbow" --time_range 1 8.6
# altres trams: 11 17.2 (assegut baix), 18.9 21.4 (dret), 23.7 25.6 (final)
# versions antigues: --multiperson false en lloc de --nb_persons_to_detect 1</code></pre>
<p>Si em passes els fitxers .mot que et surtin, els comparo amb MediaPipe i et dic on discrepen més de 5°. Per a la cinemàtica inversa (ajustar un esquelet al moviment) caldria instal·lar OpenSim primer; només ho faig si ho demanes.</p>
<p>Dades: carpeta <b>data</b> (pedalades.csv, fotogrames_angles_i_posicions.csv, mesures_per_estil_amb_semafor.csv, resum_per_estil.csv). Imatges: carpeta <b>images</b>. Vídeo i GIF: carpeta <b>video</b>.</p></section>
<section id="glossari"><h2><span class="n">10 · GLOSSARI</span>Abreviatures i termes</h2>
<dl><dt>rpm</dt><dd>revolucions per minut: quantes voltes dóna la biela cada minut.</dd><dt>fps</dt><dd>imatges per segon del vídeo.</dd><dt>Biela</dt><dd>el braç on es fixa el pedal.</dd><dt>Eix del pedalier</dt><dd>l'eix al qual s'enganxen les bieles (BB, bottom bracket en anglès).</dd><dt>Stack i reach</dt><dd>alçada i abast de la davantera del quadre respecte a l'eix del pedalier.</dd><dt>Bike fit</dt><dd>ajust de la bici al cos del ciclista.</dd><dt>KOPS</dt><dd>sigla anglesa per a la regla «genoll sobre l'eix del pedal».</dd><dt>TRC i MOT</dt><dd>fitxers de Sports2D amb les posicions de les articulacions (TRC) i els angles (MOT).</dd><dt>RTMPose, MediaPipe</dt><dd>models d'intel·ligència artificial que detecten les articulacions en un vídeo.</dd><dt>Cinemàtica inversa</dt><dd>ajustar un esquelet de l'OpenSim al moviment mesurat.</dd></dl></section>
</main><footer><div class="wrap">Informe generat a partir d'un sol vídeo. Les xifres són estimacions amb error; no substitueixen un ajust professional presencial.</div></footer></body></html>'''
H=H.replace(' poster=""','')
open('/home/user/ride_analysis/report/informe_pedalada.html','w',encoding='utf-8').write(H); print(len(H)//1024,'KB')
