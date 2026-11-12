from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageChops
import json,zipfile,hashlib,html,io,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;R=P.parents[1];records=sorted(json.loads((P/'manifest.json').read_text()),key=lambda r:r['id'])
checks=[];cards=[];contact=Image.new('RGB',(1440,2240),'#e7e5e1');cd=ImageDraw.Draw(contact)
for i,r in enumerate(records):
 n=r['id'];f=P/f'JPG/{n}.jpg';im=Image.open(f);im.load();assert im.size==tuple(r['size']);assert im.format=='JPEG'
 # Independently reconstruct archived layers, not trusting merged preview.
 with zipfile.ZipFile(P/f'editable/{n}/layers.ora') as z:
  assert z.testzip() is None;tree=ET.fromstring(z.read('stack.xml'));out=Image.new('RGBA',im.size)
  for el in reversed(list(tree.find('stack'))):out=Image.alpha_composite(out,Image.open(io.BytesIO(z.read(el.attrib['src']))).convert('RGBA'))
  merged=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA');assert ImageChops.difference(out,merged).getbbox() is None
 ET.parse(P/f'editable/{n}/editable.svg')
 thumb=im.copy();thumb.thumbnail((350,495));x=i%4*360;y=i//4*560;contact.paste(thumb,(x,y+28));cd.text((x+5,y+5),str(n),fill='#111')
 mobile=im.copy();mobile.thumbnail((360,640));mobile.save(P/f'review/{n}-mobile.jpg',quality=94)
 ref=Image.open(R/f'references/2026-10-31_同款商户电商参考/微信图片_20261031133902_{n}_2.jpg');ref.thumbnail((500,890));ref.save(P/f'review/{n}-reference.jpg',quality=92)
 status='待审：静态近似，厚边/真实感未通过' if n in [387,392,395,399] else ('未完成：缺安装视角与水幕' if n in [388,389,390,391,394] else '替代题材：参考功能无依据')
 r['status']=status;r['actual_primary_source']='376' if n in [387,392,395,399] else '372' if n not in [396,398] else 'multiple photo details'
 checks.append(dict(id=n,size=im.size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),ora_crc=True,ora_recomposed_equal=True,svg_xml_valid=True,status=status))
 cards.append(f'<section id="r{n}"><h2>{n} · {status}</h2><div class="pair"><figure><img src="review/{n}-reference.jpg" alt="原参考{n}"><figcaption>原参考 · 仅供对照</figcaption></figure><figure><a href="JPG/{n}.jpg"><img src="JPG/{n}.jpg" alt="审阅候选{n}"></a><figcaption>本轮候选 · <a href="editable/{n}/editable.svg">可编辑文字SVG</a> · <a href="editable/{n}/layers.ora">分层ORA</a></figcaption></figure></div><p>{html.escape(r["note"])}</p></section>')
contact.save(P/'review/13张审阅总览.jpg',quality=94)
(P/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(P/'verification.json').write_text(json.dumps(dict(stage='REVIEW_CANDIDATES_NOT_ACCEPTED',checks=checks,browser_preview='NOT_RUN',svg_visual_render='NOT_VERIFIED; live text metrics may differ from JPG; layout.json and build.py preserve exact Pillow rendering',visual_review='All13 final JPGs opened individually in tool; source372/376/374/382 and connector details inspected; full reference review reused and relevant refs re-opened. No visual PASS claimed.'),ensure_ascii=False,indent=2))
(P/'preview.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>顶喷13张 · 阶段审阅</title><style>body{margin:0;background:#16191c;color:#eee;font:16px/1.6 system-ui}main{max-width:1200px;margin:auto;padding:24px}a{color:#e6bd85}h1{font-size:30px}.notice{background:#3a2e20;padding:20px;border-left:4px solid #d7b07b}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;background:#25282b;padding:10px}img{display:block;width:100%;height:auto}figcaption{padding:10px}section{margin:50px 0;border-top:1px solid #555}p{color:#d1d1d1}nav{display:flex;flex-wrap:wrap;gap:18px;padding:20px 0}@media(max-width:600px){main{padding:14px}.pair{gap:8px}figure{padding:3px}figcaption{font-size:12px}h2{font-size:19px}}</style><main><h1>13张逐图对应 · 阶段审阅候选</h1><div class="notice">已保存7方6竖、可编辑中文和独立商品/背景层。尚未达到“仅换商品和模特，其他尽量贴参考”的整体验收要求：实拍角度不足、厚度与光线匹配仍弱，5张缺安装水幕，AIR/360°等改为外观题材。不能作为已验收客户成品。</div><nav>'''+''.join(f'<a href="#r{r["id"]}">{r["id"]}</a>' for r in records)+'</nav>'+''.join(cards)+'</main></html>')
readme='''# 顶喷13张逐图对应 · 阶段审阅

2026-11-02。唯一制作Owner当前会话；未新增代理/聊天。最新要求：风格、构图、光影尽量照原13参考，仅替换商品与原创模特；不支持的品牌、功能、参数不照搬。

**结论：13个编号都有候选，但任务验收未完成，不能当作完整合格广告套图。**

- 399已用376原实拍整件重排，双行金字、暖侧光/轻雾背景接近参考；原片仍近正视，明显侧壁/斜仰视缺失。没有用假厚边或拉伸掩盖。
- 387、392、395、399采用376原片；388—391、393—394、397采用372原片。所有整件等比缩放/旋转，不做透视扭曲或AI商品重绘。同一原片复用仅能作布局占位，不能宣称不同机位已恢复。
- 388、389、390、391、394：缺参考对应安装仰视与出水证据，目前静态场景占位，无水幕、支架；391/394为新原创成年短发模特，标场景示意。该5张的主视觉任务未完成。
- 392/395：372/376复位商品+382实际短红点圆窗，未展示完整提拉过程；382局部外缘SKU未确认，不改成银色整件。
- 393/397内部AIR爆炸图改为面板/侧边/接头外观；398旋转/人体覆盖比较改为接头特写；396六大功能改六处实拍细节。这些是内容替代，不代表原功能覆盖。
- 实际商品受原拍摄光线限制，冷色反射与部分暖场景不完全融合；边缘有薄片感。侧边/接头原照残留环境反射和局部清晰度限制。真实感未通过，不追加无依据的相同路线重试。

## 文件

`preview.html`逐张左参考右候选（本地浏览器未实测）；`JPG/`13张；`review/13张审阅总览.jpg`；`editable/编号/layers.ora`独立栅格层；`editable.svg`含可编辑中文字与本地base.png；`layout.json`位置/文字；`build.py`原生排版复现入口（需要原项目实拍路径）。ORA和SVG及base可独立编辑，不依赖外部服务；SVG字体显示与JPG精确字距尚未通过GUI核验，精确栅格排版用JSON+Pillow脚本。

尺寸：7张1200×1200；6张900×1600。所有原件及此前版本保留；本轮初稿JPG在review/v1-jpg.zip。无外发、发布、删除。

## 已查与待补

13张最终JPG均实际打开；396侧边卡首次被方形裁切成空反射，已回原374右端局部并用等比完整显示修正，393/397/398同步。13JPG解码和尺寸、13ORA CRC与独立逐层重组、13SVG XML检查通过；这些不等于视觉通过。逐项SHA见verification.json。

下一步需要真实商品的参考对应斜仰视安装角度、可辨侧壁的斜放近照和真实出水素材，才能保持真实孔纹同时接近水幕构图；AIR/360/水量比较无证据不恢复。当前可直接审阅399等静态构图改善和原创模特选择，整套接受仍UNKNOWN。
'''
(P/'README.md').write_text(readme)
# Bundle only current review assets; preserve initial draft archive separately.
for name,files in [('13张_JPG_审阅候选.zip',sorted((P/'JPG').glob('*.jpg'))),('13张_可编辑源包.zip',sorted((P/'editable').rglob('*'))+[P/'README.md',P/'manifest.json',P/'build.py',P/'verification.json']+sorted((P/'assets').glob('*')))]:
 files=[f for f in files if f.is_file()]
 with zipfile.ZipFile(P/name,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,str(f.relative_to(P)))
 with zipfile.ZipFile(P/name) as z:
  assert z.testzip() is None
  for f in files:assert hashlib.sha256(z.read(str(f.relative_to(P)))).digest()==hashlib.sha256(f.read_bytes()).digest()
 print(name,len(files),(P/name).stat().st_size)
print('Verified',len(checks),'JPG / ORA / SVG')
