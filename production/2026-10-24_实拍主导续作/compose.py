"""Deterministic Chinese typesetting only; generated product pixels stay protected."""
from pathlib import Path
import hashlib, importlib.util, json
from PIL import Image, ImageDraw, ImageFont
B=Path(__file__).resolve().parent
ROOT=B.parents[1]
SPEC=importlib.util.spec_from_file_location('photo_gate',ROOT/'tools/photo_guided_gate.py')
G=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(G)
def rec(path):
 p=Path(path);return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def label(draw,xy,value,size,fill,bold=False):
 f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc' if bold else '/System/Library/Fonts/Hiragino Sans GB.ttc',size)
 draw.text(xy,value,font=f,fill=fill,anchor='lt')
def main():
 m=json.loads((B/'image-manifest.json').read_text());log=json.loads((B/'production-log.json').read_text())
 calls={c['id']:c for c in log['calls'] if c.get('status')=='SUCCEEDED'}
 # Tool receipts historically use more than one status spelling; native file is verified below.
 for c in log['calls']:
  if c.get('native_path'): calls[c['id']]=c
 source_by_path={str((ROOT/s['file']['path']).resolve()):s for s in m['appearance_sources']}
 done=[]
 for a in m['assets']:
  key=a['id']
  if key not in calls:continue
  c=calls[key];native=Path(c['native_path']);a['generated_native']=rec(native)
  prompt=Path(c['prompt_file']);prompt=prompt if prompt.is_absolute() else ROOT/prompt
  a['prompt']=rec(prompt)
  refs=c['actual_call']['referenced_image_paths']
  ids=[source_by_path[str(Path(p).resolve())]['id'] for p in refs if str(Path(p).resolve()) in source_by_path]
  a['appearance_source_ids']=ids
  a['style_references']=[rec(Path(p)) for p in refs if '/references/' in p]
  a['text_edit_regions']=[]
  if key.startswith('K') or key=='R06':a['native_transform']={'uniform_scale':.82,'background_rgb':[255,255,255]}
  with Image.open(native) as im: canvas=G.typesetting_baseline(im,a)
  draw=ImageDraw.Draw(canvas);copy=[]
  if key.startswith('K'):
   copy=[a['sku'],'手持花洒','单花洒']
   a['text_edit_regions']=[[52,150,355,355],[54,1070,345,1130]]
   label(draw,(70,174),copy[0],64,'#172026',True)
   label(draw,(73,266),copy[1],32,'#515b64')
   label(draw,(73,1084),copy[2],28,'#515b64')
  elif key=='R04':
   a['text_edit_regions']=[[60,65,1150,184],[60,1010,595,1170],[655,1010,1210,1170]]
   copy=['两处按键 · 功能说明','中央红钮','手动按压除垢','下方按键','切换常规 / 喷雾 / 混合']
   label(draw,(76,96),copy[0],64,'#172026',True)
   label(draw,(76,1030),copy[1],44,'#bf202b',True)
   label(draw,(78,1104),copy[2],30,'#515b64')
   label(draw,(680,1030),copy[3],44,'#156fc4',True)
   label(draw,(680,1104),copy[4],28,'#515b64')
  elif key=='R05':
   a['text_edit_regions']=[[60,52,620,265]]
   copy=['面板细节','白色孔位 · 中央红钮','手动按压辅助除垢']
   label(draw,(76,76),copy[0],64,'#172a38',True)
   label(draw,(78,167),copy[1],32,'#255d81')
   label(draw,(78,225),copy[2],28,'#45677b')
  elif key=='R06':
   a['text_edit_regions']=[[60,52,1150,140],[240,1115,1020,1205]]
   copy=['正背外观','银色｜单花洒','正面','背面']
   label(draw,(76,72),copy[0],64,'#172026',True)
   label(draw,(932,98),copy[1],28,'#515b64')
   label(draw,(382,1144),copy[2],40,'#273c4b',True)
   label(draw,(810,1144),copy[3],40,'#273c4b',True)
  a['approved_copy']=copy
  working=B/f'working/{key}.png';jpg=B/f'final/{key}.jpg'
  canvas.save(working);canvas.save(jpg,quality=97,subsampling=0)
  a.update(candidate=rec(working),client_jpg=rec(jpg),actual_dimensions=list(canvas.size),qa_status='AWAITING_VISUAL_REVIEW')
  prior_review=a.get('review')
  if prior_review:
   r=json.loads((ROOT/prior_review['path']).read_text())
   if r.get('candidate_sha256')==a['candidate']['sha256'] and r.get('jpg_sha256')==a['client_jpg']['sha256']:a['qa_status']='REVIEW_READY'
  hashes=sorted({source_by_path[str(Path(p).resolve())]['file']['sha256'] for p in refs if str(Path(p).resolve()) in source_by_path})
  receipt={'tool':'builtin_image_gen','native_sha256':a['generated_native']['sha256'],'prompt_sha256':a['prompt']['sha256'],'appearance_source_sha256':hashes,'actual_call':c,'hard_shape_lock':False}
  rp=B/f'review/{key}-generation-receipt.json';rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2));a['generation_receipt']=rec(rp)
  done.append(key)
 (B/'image-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('Composed:',','.join(done))
if __name__=='__main__':main()
