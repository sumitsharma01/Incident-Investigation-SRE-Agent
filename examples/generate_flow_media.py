"""Render a deterministic animated architecture loop and a static cover."""
import asyncio
import io
from pathlib import Path
from PIL import Image
import imageio_ffmpeg
from playwright.async_api import async_playwright
from generate_architecture_graphics import logo, icon, text

OUT=Path(__file__).resolve().parents[1]/'docs/assets/architecture'

def graphic():
 s='''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-label="Production signals flow into the SRE Agent, through OpenSRE and Azure, and return findings for engineer review"><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#2b80ef" stroke-width="1.8"/></marker><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#eaf3ff"/></linearGradient><linearGradient id="agent" x2="1" y2="1"><stop stop-color="#267ced"/><stop offset="1" stop-color="#1453bd"/></linearGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="22"/></filter><filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="15" flood-color="#164d99" flood-opacity=".08"/></filter></defs><style>text{font-family:Arial,Helvetica,sans-serif}</style><rect width="1600" height="900" fill="url(#bg)"/>'''
 s+=text(80,91,'LIBRESRE',20,'#246bd0',700)
 s+=text(80,158,'Production signals. Clearer next steps.',48,'#153258',700)
 paths=['M825 285V345','M450 450H590','M800 555V657','M895 657V555','M1060 450H1200']
 for i,p in enumerate(paths):
  s+=f'<path id="rail{i}" d="{p}" fill="none" stroke="#2b80ef" stroke-opacity=".5" stroke-width="3" marker-end="url(#arrow)"/>'
 s+='<rect id="halo" x="574" y="329" width="502" height="242" rx="38" fill="#45a1ff" opacity="0" filter="url(#glow)"/>'
 def box(x,y,w,h,fill='#ffffff',stroke='#d9e7fb'):
  return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="{fill}" stroke="{stroke}" filter="url(#shadow)"/>'
 s+=box(590,215,470,70)+text(620,260,'Incident context',24,'#153258',700)+text(841,258,'Service · symptoms',18,'#59718e')
 s+=box(80,345,370,210)+text(112,390,'Observability',28,'#153258',700)
 s+=logo(112,415,'prometheus',54,54)+logo(193,415,'grafana',54,54)
 s+=text(112,511,'Peak traffic · rising latency',22,'#59718e')
 s+=box(590,345,470,210,'url(#agent)','#398bf2')
 s+=icon(622,372,'metrics','#ffffff')+text(684,405,'INCIDENT INVESTIGATION',16,'#d4e8ff',700)
 s+=text(622,463,'Our SRE Agent',38,'#ffffff',700)+text(622,513,'Investigate connected evidence',23,'#e1efff')
 s+=box(1200,345,320,210)+icon(1232,369,'report','#267ced')
 s+=text(1232,462,'Findings',32,'#153258',700)+text(1232,511,'Engineer review',23,'#59718e')
 s+=box(620,657,410,116)+text(646,698,'INVESTIGATION RUNTIME',14,'#59718e',700)
 # White upstream wordmark on a small blue pill keeps its original appearance.
 s+='<rect x="646" y="713" width="160" height="38" rx="9" fill="#174995"/>'
 s+=logo(657,721,'opensre',136,24)+logo(840,713,'azure',35,35)+text(889,741,'Azure',22,'#153258',700)
 s+=text(846,323,'Describe',16,'#246bd0',700)+text(474,430,'Evidence',16,'#246bd0',700)
 s+=text(680,608,'Investigate',16,'#246bd0',700)+text(911,608,'Results',16,'#246bd0',700)+text(1093,430,'Report',16,'#246bd0',700)
 for i in range(5):s+=f'<circle id="dot{i}" r="7" fill="#45a1ff" opacity="0"/>'
 return s+'</svg>'

JS='''window.setFrame=(t)=>{
 const phases=[[0,1.5],[.6,2],[2.4,3.6],[3.6,4.8],[5,6.5]];
 phases.forEach(([a,b],i)=>{const d=document.getElementById('dot'+i);const p=document.getElementById('rail'+i);const u=(t-a)/(b-a);d.setAttribute('opacity',u>=0&&u<=1?1:0);const pt=p.getPointAtLength(Math.max(0,Math.min(1,u))*p.getTotalLength());d.setAttribute('cx',pt.x);d.setAttribute('cy',pt.y)});
 const active=t>=1.3&&t<=5.4;document.getElementById('halo').setAttribute('opacity',active?.35+.15*Math.sin(t*5):0);
};'''

async def main():
 svg=graphic();(OUT/'agent-flow.svg').write_text(svg)
 html='<html><body style="margin:0;background:#f3f8ff">'+svg+'<script>'+JS+'</script></body></html>'
 (OUT/'agent-flow.html').write_text(html.replace('</script>', 'function tick(ms){setFrame((ms/1000)%7.2);requestAnimationFrame(tick)};requestAnimationFrame(tick);</script>'))
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
  page=await browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
  await page.set_content(html)
  await page.evaluate('setFrame(2.9)');await page.screenshot(path=str(OUT/'agent-flow.png'))
  frames=[]
  for n in range(144):
   await page.evaluate(f'setFrame({n/20})')
   im=Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
   frames.append(im)
  writer=imageio_ffmpeg.write_frames(str(OUT/'agent-flow.mp4'), (1600,900), fps=20, macro_block_size=1, codec='libx264', quality=9, pix_fmt_in='rgb24', pix_fmt_out='yuv420p')
  writer.send(None)
  for frame in frames: writer.send(frame.tobytes())
  writer.close()
  frames=[f.resize((1280,720),Image.Resampling.LANCZOS) for f in frames[::2]]
  palette_source=Image.new("RGB",(1280,1440))
  palette_source.paste(frames[29],(0,0))
  palette_source.paste(frames[29].crop((86,330,200,380)).resize((1280,720)),(0,720))
  palette=palette_source.quantize(colors=256)
  frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
  frames[0].save(OUT/'agent-flow.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
  await browser.close()
 print('Rendered SVG, HTML, PNG and 7.2-second looping GIF.')
if __name__=='__main__':asyncio.run(main())
