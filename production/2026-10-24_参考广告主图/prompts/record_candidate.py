from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil,datetime
p=Path(__file__).parent.parent
id,src=sys.argv[1:3];src=Path(src)
req=json.loads((p/f'prompts/{id}-request.json').read_text())
f=p/f'generated/{id}-v001-native.png';shutil.copy2(src,f)
Image.open(f).convert('RGB').save(p/f'generated/{id}-v001-review.jpg',quality=95)
sha=lambda a:hashlib.sha256(Path(a).read_bytes()).hexdigest()
log=json.loads((p/'production-log.json').read_text())
record={'id':id,'version':'v001','status':'candidate_pending_independent_review','actual_call':req,'prompt_file':str(p/f'prompts/{id}-request.json'),'references':[{'path':a,'sha256':sha(a)} for a in req['referenced_image_paths']],'actual_tool_output_path':str(src),'native_path':str(f),'native_sha256':sha(f),'dimensions':list(Image.open(f).size),'output_actually_viewed':True,'saved_at':datetime.datetime.now().astimezone().isoformat()}
log['calls'].append(record);log['completed_generation_calls']=len(log['calls'])
(p/'production-log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print(json.dumps({'id':id,'native_path':str(f),'sha256':sha(f)},ensure_ascii=False))
