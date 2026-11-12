"""Bounded read-only polling/download. Never creates or retries a generation task."""
from pathlib import Path
import json,time,re,sys
from datetime import datetime
from zoneinfo import ZoneInfo
P=Path(__file__).resolve().parent
ns={'__file__':str(P/'wuye_video.py')};exec((P/'wuye_video.py').read_text().split('p=argparse.ArgumentParser()')[0],ns)
api=ns['api'];task=sys.argv[1];assert re.fullmatch(r'[A-Za-z0-9_-]+',task)
end=time.monotonic()+900;last=None;out=P/'AI主视觉首帧-v1/AI试生成-主视觉-H3-803-原始.mp4'
def record(r,note=None):
 now=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
 l=P/'wuye-tasks.json';j=json.loads(l.read_text());row=next(t for t in j['tasks'] if t.get('taskId')==task);row.update(status=r.get('status','unknown'),progress=r.get('progress'),lastCheck=now)
 if note:row['watchNote']=note
 if r.get('error'):row['providerError']={k:v for k,v in r['error'].items() if k in ('code','message')} if isinstance(r['error'],dict) else str(r['error'])[:300]
 if out.exists():row['output']=str(out)
 l.write_text(json.dumps(j,ensure_ascii=False,indent=2))
 m=P/'manifest.json';j=json.loads(m.read_text());j['singleAiTrial'].update(status=r.get('status','unknown'),progress=r.get('progress'),lastCheck=now)
 if out.exists():j['singleAiTrial']['rawOutput']=str(out)
 if note:j['singleAiTrial']['watchNote']=note
 m.write_text(json.dumps(j,ensure_ascii=False,indent=2))
while time.monotonic()<end:
 try:r=json.loads(api('/v1/videos/'+task))
 except Exception as e:
  print(type(e).__name__+': status query failed; no new generation',flush=True);time.sleep(10);continue
 state=(r.get('status'),r.get('progress'))
 if state!=last:
  print(json.dumps({'id':task,'status':state[0],'progress':state[1]},ensure_ascii=False),flush=True);record(r);last=state
 if r.get('status')=='failed':
  record(r,'No retry after this failure; verify refund.');print('FAILED: no further POST',flush=True);sys.exit(2)
 if r.get('status')=='completed':
  if not out.exists():
   payload=api('/v1/videos/'+task+'/content')
   if not payload or b'ftyp' not in payload[:40]:raise RuntimeError('Download did not return MP4 signature')
   with out.open('xb') as f:f.write(payload)
  record(r,'Downloaded; product detail and motion review pending.');print('DOWNLOADED '+str(out),flush=True);sys.exit(0)
 time.sleep(10)
record(r,'Bounded15min watch ended; pending is not failure. Do not POST again.');print('PENDING: existing task retained, no resubmission',flush=True)
