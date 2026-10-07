"""Generate editable SVG diagrams and browser-rendered PNG exports."""
import argparse
import base64
import html
import textwrap
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets/architecture'
CYAN='#55c9ff'; ORANGE='#ffa94b'; PURPLE='#ac92ff'; GREEN='#60d6aa'; MUTED='#a4b7ce'


def text(x,y,value,size=22,color='#edf3fc',weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">{html.escape(value)}</text>'


def icon(x,y,kind,color=CYAN):
    paths={
      'person':'<circle cx="20" cy="10" r="7"/><path d="M5 36c0-13 30-13 30 0"/>',
      'server':'<rect x="2" y="3" width="36" height="14" rx="3"/><rect x="2" y="23" width="36" height="14" rx="3"/><path d="M8 10h3m-3 20h3m9-20h13m-13 20h13"/>',
      'shield':'<path d="M20 2L36 8v12c0 10-16 18-16 18S4 30 4 20V8z"/><path d="M12 20l6 6 12-13"/>',
      'report':'<rect x="6" y="2" width="28" height="36" rx="3"/><path d="M12 11h16m-16 8h16m-16 8h10"/>',
      'route':'<path d="M3 20h34M22 5l15 15-15 15"/>',
      'metrics':'<path d="M3 35V5m0 30h34M7 29l8-8 6 4 12-18"/>',
    }
    return f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{paths[kind]}</g>'


def logo(x,y,brand,w=40,h=40):
    file=OUT/'brands'/({'grafana':'grafana.webp','azure':'azure.png','opensre':'opensre.svg','prometheus':'prometheus.svg','fastapi':'fastapi.svg','libresre':'libresre-symbol.png'}[brand])
    if brand == 'libresre': file=OUT.parent/'brand/libresre-symbol.png'
    data=file.read_bytes();mime={'svg':'image/svg+xml','png':'image/png','webp':'image/webp'}[file.suffix[1:]]
    if brand in ['prometheus','fastapi']:
        data=data.decode().replace('<svg ',f'<svg fill="{"#e6522c" if brand=="prometheus" else "#38d5bf"}" ',1).encode()
    uri='data:'+mime+';base64,'+base64.b64encode(data).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{uri}"/>'


def card(x,y,w,h,title,lines=(),brand=None,glyph=None,color=CYAN,highlight=False,title_size=24):
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{"#153047" if highlight else "#142236"}" stroke="{color if highlight else "#35465e"}" stroke-width="{2 if highlight else 1}"/>'
    if brand=='opensre':
        s+=logo(x+22,y+20,brand,145,29);s+=text(x+22,y+80,title,24,weight=650);start=y+113
    else:
        if brand:s+=logo(x+22,y+22,brand)
        elif glyph:s+=icon(x+22,y+22,glyph,color)
        s+=text(x+(80 if brand or glyph else 22),y+49,title,title_size,weight=650);start=y+87
    for i,line in enumerate(lines):s+=text(x+22,start+29*i,line,19,MUTED)
    return s


def arrow(path,color=CYAN,dashed=False):
    dash = 'stroke-dasharray="8 7"' if dashed else ''
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" {dash} marker-end="url(#arrow-{color[1:]})"/>'


def zone(x,y,w,h,label,subtitle,color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="{color}" fill-opacity=".045" stroke="{color}" stroke-opacity=".5"/>'+text(x+22,y+37,label,21,color,650)+text(x+22,y+68,subtitle,17,MUTED)


def frame(title,subtitle,height,tag):
    markers=''.join(f'<marker id="arrow-{c[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="{c}" stroke-width="1.8"/></marker>' for c in [CYAN,ORANGE,PURPLE,GREEN,'#70849c'])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" viewBox="0 0 1800 {height}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc><defs>{markers}<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101d31"/><stop offset="1" stop-color="#07111f"/></linearGradient><linearGradient id="accent"><stop stop-color="{CYAN}"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient></defs><style>text {{font-family:Arial,Helvetica,sans-serif;}}</style><rect width="1800" height="{height}" rx="26" fill="url(#bg)"/><rect x="44" y="40" width="68" height="5" rx="2" fill="url(#accent)"/>'''+text(130,49,tag,16,CYAN,650)+text(44,105,title,42,weight=700)+text(44,145,subtitle,22,MUTED)


def production():
    s=frame('Where the agent sits in production','The serving path stays separate. Investigation reads observability evidence; engineers decide what changes.',1120,'SRE AGENT / V0.3.0 / PRODUCTION PLACEMENT REFERENCE')
    s+=zone(44,188,490,788,'PRODUCTION WORKLOADS','Illustrative environment • not a deployed claim','#70849c')
    s+=zone(564,188,450,788,'OBSERVABILITY','Metrics path verified in the local lab',ORANGE)
    s+=zone(1044,188,712,788,'INVESTIGATION PLANE','Agent host + external Azure model endpoint',CYAN)
    s+=card(76,294,426,122,'Customers',['Normal application requests'],glyph='person',color='#70849c')
    s+=card(76,462,426,128,'Ingress / routing',['Existing serving infrastructure'],glyph='route',color='#70849c')
    s+=card(76,638,426,132,'Application services',['Expose metrics to your collectors'],glyph='server',color='#70849c')
    s+=card(76,818,426,116,'Dependencies',['Database / cache / downstream APIs'],glyph='server',color='#70849c')
    s+=arrow('M289 416V455','#70849c')+arrow('M289 590V631','#70849c')+arrow('M289 770V811','#70849c')
    s+=card(596,350,386,145,'Prometheus',['Collects and stores service metrics','Queries evaluate at a time/window'],brand='prometheus',color=ORANGE)
    s+=card(596,575,386,145,'Grafana',['Dashboards + datasource proxy','Viewer token for metrics access'],brand='grafana',color=ORANGE)
    s+=arrow('M502 685H548V423H588',ORANGE)+text(555,546,'metrics',17,ORANGE)
    s+=arrow('M789 495V567',ORANGE)+text(806,538,'datasource',17,ORANGE)
    s+=text(602,812,'Logs, traces, releases and history',20,MUTED)+text(602,846,'Need their own configured connectors.',18,MUTED)+text(602,875,'Current live proof covers metrics.',18,MUTED)
    s+=card(1076,282,648,116,'On-call engineer',['Describe incident • review findings • approve changes'],glyph='person',color=GREEN)
    s+=card(1076,446,648,132,'LibreSRE',['FastAPI • input checks • backend-aware plan','Orchestration and request-local review notes'],brand='libresre',highlight=True)
    s+=arrow('M1400 398V438',GREEN)+text(1420,425,'POST /investigate',17,GREEN)
    s+=card(1076,648,320,156,'Investigation runtime',['Headless CLI • read-only tools'],brand='opensre',color=CYAN)
    s+=card(1434,648,290,156,'Azure model',['External Azure endpoint','Configured gpt-5.4'],brand='azure',color=PURPLE)
    s+=arrow('M1236 578V640',CYAN)+text(1253,617,'invoke',17,CYAN)
    s+=arrow('M1076 674H990',ORANGE)+text(992,657,'read query',14,ORANGE)
    s+=arrow('M982 718H1068',ORANGE)+text(993,702,'results',14,ORANGE)
    s+=arrow('M1396 705H1426',PURPLE)+arrow('M1434 751H1404',PURPLE)
    s+=card(1076,858,648,86,'Findings → human review',[],glyph='report',color=GREEN)
    s+=arrow('M1236 804V850',GREEN)
    s+=text(44,1021,'PRODUCTION PREREQUISITES',17,ORANGE,650)+text(44,1055,'Add authentication, rate limits, bounded concurrency and isolated read-only credentials before production use.',22)
    s+=text(44,1090,'Grey: serving context    Orange: observability    Cyan: this project + OpenSRE    Purple: external model    No automatic write path shown.',17,MUTED)
    return s+'</svg>'


def investigation():
    s=frame('From incident description to evidence-backed findings','The HTTP API is the entry point. OpenSRE queries configured tools and reasons with the selected model.',1030,'SRE AGENT / VERIFIED LOCAL INVESTIGATION PATH')
    steps=[(44,'1 · Describe the incident',['Service, symptoms and time window','Engineer sends an HTTP request'],'person',None),
      (393,'2 · Plan and validate',['FastAPI → controller → orchestrator','Input checks and investigation plan'],None,'fastapi'),
      (742,'3 · Query evidence',['One ephemeral OpenSRE turn','No extra tool grants or write bypass'],None,'opensre'),
      (1091,'4 · Fetch metric signals',['Grafana datasource → Prometheus','Traffic, P95, errors and saturation'],None,'grafana'),
      (1440,'5 · Review the findings',['Summary, uncertainties and checks','Engineer owns the next action'],'report',None)]
    for x,title,lines,glyph,brand in steps:
        s+=f'<rect x="{x}" y="260" width="316" height="235" rx="18" fill="{"#153047" if x==393 else "#142236"}" stroke="{CYAN if x==393 else "#35465e"}" stroke-width="2"/>'
        if brand: s+=logo(x+22,282,brand,145 if brand=='opensre' else 40,29 if brand=='opensre' else 40)
        else: s+=icon(x+22,282,glyph,CYAN)
        s+=text(x+22,350,title,21,weight=650)
        wrapped=[part for line in lines for part in textwrap.wrap(line,30)]
        for i,line in enumerate(wrapped):s+=text(x+22,386+i*24,line,17,MUTED)
    for x in [360,709,1058,1407]:s+=arrow(f'M{x} 374H{x+25}',CYAN)
    s+=card(742,543,665,148,'Azure reasoning',['Model/tool loop uses the configured Azure deployment.','Selected evidence is sent to the model provider.'],brand='azure',color=PURPLE)
    s+=arrow('M900 495V535',PURPLE)+arrow('M1110 543V517H1020V503',PURPLE)
    s+=text(44,546,'WHAT THIS PROJECT ADDS',18,CYAN,650)
    for i,line in enumerate(['A consistent investigation API','Backend selection: demo or OpenSRE','Plans and request-local review notes','Recorded dashboards and replay scripts']):s+=text(44,587+38*i,'• '+line,23)
    s+=text(1470,548,'RETURNED STATUS',18,GREEN,650)
    for i,line in enumerate(['success','needs_input','approval_required','error']):s+=text(1470,589+34*i,line,23,GREEN if i==0 else MUTED)
    s+=zone(44,766,1712,172,'SEPARATE DEMO PATH','Credential-free sample collectors; their fixed hypotheses are not live incident evidence.', '#70849c')
    s+=text(70,882,'Logs → metrics → traces → deployments → history → sample aggregation → illustrative reasoning',24)
    s+=text(44,990,'Verified in the local Grafana/Prometheus lab. Additional connectors and production access require their own setup and validation.',20,MUTED)
    return s+'</svg>'


def proof():
    s=frame('The overload proof: rising traffic and P95','Actual API calls, model responses and metric queries. Workload values and recovery are generated by the local exporter.',1040,'SRE AGENT / RECORDED CASE / 7 OCTOBER 2026')
    phases=[(44,'01  BASELINE',GREEN,[('200 req/s','Incoming traffic'),('420 ms','P95 latency'),('0.5%','Failed requests'),('8','Queued requests')]),
            (636,'02  OVERLOAD',ORANGE,[('1,991 req/s','Incoming traffic · ~10×'),('2.4 seconds','P95 latency · ~5.7×'),('19.6%','Failed requests'),('850','Queued requests')]),
            (1228,'03  MODELED RECOVERY',CYAN,[('2,000 req/s','Incoming traffic stays high'),('450 ms','P95 latency'),('0.5%','Failed requests'),('12','Queued requests')])]
    for x,label,color,stats in phases:
        s+=f'<rect x="{x}" y="210" width="528" height="465" rx="22" fill="#142236" stroke="{color}" stroke-width="2"/>'+text(x+25,251,label,21,color,650)
        for i,(value,label2) in enumerate(stats):s+=text(x+25,312+i*88,value,38,color,700)+text(x+25,342+i*88,label2,19,MUTED)
    s+=arrow('M572 438H625',ORANGE)+arrow('M1164 438H1217',CYAN)
    s+=card(44,732,828,175,'What the agent concluded',['Read-only OpenSRE query verified traffic, P95 and queue depth.','Saturation/backlog was plausible; the exact cause stayed unproven.'],brand='opensre',color=CYAN)
    s+=card(916,732,840,175,'What this proof establishes',['The local evidence → API → OpenSRE → Azure integration works.','Recovery was scripted; no automatic remediation was performed.'],glyph='shield',color=GREEN)
    s+=logo(44,928,'prometheus',32,32)+logo(92,928,'grafana',32,32)+logo(140,928,'fastapi',32,32)+logo(188,928,'azure',32,32)
    s+=text(246,952,'Prometheus + Grafana + FastAPI + OpenSRE + Azure',21,MUTED)
    s+=text(44,984,'Source: committed baseline, incident and recovery snapshots. Values rounded; full evidence and failed/successful attempts are in the case report.',17,MUTED)
    return s+'</svg>'


def main(executable):
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True,exist_ok=True)
    diagrams={'production-placement':production(),'investigation-flow':investigation(),'overload-proof':proof()}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable)
        try:
            for name,svg in diagrams.items():
                (OUT/(name+'.svg')).write_text(svg+'\n')
                page=browser.new_page(viewport={'width':1800,'height':1200},device_scale_factor=2)
                page.set_content('<html><body style="margin:0">'+svg+'</body></html>',wait_until='load')
                page.locator('svg').screenshot(path=str(OUT/(name+'.png')))
                page.close()
        finally:browser.close()
    print('Generated three SVG sources and high-resolution PNG exports.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--executable-path')
    main(parser.parse_args().executable_path)
