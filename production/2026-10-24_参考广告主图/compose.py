"""Reference-led ad lettering on native generated blank title bands."""
from pathlib import Path
import json,hashlib,importlib.util
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent; ROOT=B.parents[1]
S=importlib.util.spec_from_file_location('pg',ROOT/'tools/photo_guided_gate.py');G=importlib.util.module_from_spec(S);S.loader.exec_module(G)
def rec(p):
 p=Path(p);return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def text(d,xy,t,size,fill,stroke=0):
 f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',size)
 d.text(xy,t,font=f,fill=fill,anchor='lt',stroke_width=stroke,stroke_fill=fill)
def main():
 m=json.loads((B/'image-manifest.json').read_text());log=json.loads((B/'production-log.json').read_text())
 calls={c['id']:c for c in log['calls'] if c.get('native_path') and 'roi' not in c.get('version','').lower()}
 sources={str((ROOT/s['file']['path']).resolve()):s for s in m['appearance_sources']}
 for a in m['assets']:
  key=a['id']
  if key not in calls:continue
  c=calls[key];native=Path(c['native_path']);prompt=Path(c['prompt_file']);prompt=prompt if prompt.is_absolute() else ROOT/prompt
  a.update(generated_native=rec(native),prompt=rec(prompt))
  refs=c['actual_call']['referenced_image_paths'];a['appearance_source_ids']=[sources[str(Path(p).resolve())]['id'] for p in refs if str(Path(p).resolve()) in sources]
  current_styles=[rec(Path(p)) for p in refs if '/references/' in p]
  if current_styles:a['style_references']=current_styles
  hashes=sorted({sources[str(Path(p).resolve())]['file']['sha256'] for p in refs if str(Path(p).resolve()) in sources})
  selected=ROOT/a['local_repair']['file']['path'] if a.get('local_repair') else native
  with Image.open(selected) as im:can=G.typesetting_baseline(im,a)
  d=ImageDraw.Draw(can);a['text_edit_regions']=[];a['approved_copy']=[]
  if key=='AD01':
   a['text_edit_regions']=[[50,88,480,166],[20,1080,1215,1240]]
   a['approved_copy']=['三档出水','手持花洒','常规 · 喷雾 · 混合','下方按键切换']
   text(d,(77,98),'三档出水',70,'#fff8e9',1)
   text(d,(46,1122),'手持花洒',78,'#17100b',2)
   text(d,(522,1103),'常规 · 喷雾 · 混合',66,'#fff8ee',1)
   text(d,(526,1202),'下方按键切换',30,'#f6d9ae')
  elif key=='AD02':
   a['text_edit_regions']=[[865,35,1225,280],[880,320,1205,385],[880,425,1205,488],[60,1132,1194,1241],[890,995,1215,1045]]
   a['approved_copy']=['三档出水','下方按键切档','中央按压除垢','常规 · 喷雾 · 混合','正背展示 · 单花洒']
   text(d,(888,47),'三档',110,'#10212c',2)
   text(d,(888,167),'出水',110,'#10212c',2)
   text(d,(919,326),'下方按键切档',38,'#ffffff',1)
   text(d,(919,434),'中央按压除垢',38,'#ffffff',1)
   text(d,(914,1005),'正背展示 · 单花洒',28,'#184567')
   phrase='常规 · 喷雾 · 混合';f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',84)
   x=round((can.width-d.textlength(phrase,font=f))/2)
   text(d,(x,1142),phrase,84,'#ffffff',1)
  elif key=='AD03':
   a['text_edit_regions']=[[785,45,1210,205],[35,1080,1205,1210]]
   a['approved_copy']=['三档出水','下方按键切换','中央红钮','手动按压除垢']
   text(d,(816,65),'三档出水',76,'#fff9eb',1)
   text(d,(821,164),'下方按键切换',32,'#eecb91')
   text(d,(57,1113),'中央红钮',78,'#fff9eb',2)
   text(d,(570,1122),'手动按压除垢',78,'#241409',2)
  # Other native compositions are lettered only after visual review.
  output=B/f'working/{key}.png';jpg=B/f'final/{key}.jpg';can.save(output);can.save(jpg,quality=97,subsampling=0)
  a.update(candidate=rec(output),client_jpg=rec(jpg),actual_dimensions=list(can.size),qa_status='AWAITING_VISUAL_REVIEW')
  receipt={'tool':'builtin_image_gen','native_sha256':a['generated_native']['sha256'],'prompt_sha256':a['prompt']['sha256'],'appearance_source_sha256':hashes,'actual_call':c,'hard_shape_lock':False}
  if a.get('local_repair'):receipt['local_repair']=a['local_repair']
  rp=B/f'review/{key}-generation-receipt.json';rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2));a['generation_receipt']=rec(rp)
 (B/'image-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('Native candidates composed; visual and lettering review pending')
if __name__=='__main__':main()
