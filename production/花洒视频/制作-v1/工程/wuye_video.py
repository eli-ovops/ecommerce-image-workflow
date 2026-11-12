"""Document-based client. No automatic POST retries. Secrets never logged."""
import argparse, json, mimetypes, os, re, uuid, subprocess, tempfile
from pathlib import Path
from urllib import request, error, parse
BASE='https://www.wuyeai.cn'
KEY=Path.home()/'.config/wuyeai/shower-video.key'
ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/'wuye-tasks.json'
class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise RuntimeError('Redirect refused: check provider documentation before continuing')
def api(path, data=None, ctype=None):
    key=KEY.read_text().strip()
    # Explicit alternate upload transport; no automatic fallback or POST retries.
    if data is not None and os.environ.get('WUYE_UPLOAD_TRANSPORT')=='curl':
        with tempfile.TemporaryDirectory(prefix='wuye-request-') as tmp:
            body_path=Path(tmp)/'multipart.bin';body_path.write_bytes(data)
            config=('header = "Authorization: Bearer '+key+'"\n').encode()
            c=subprocess.run(['curl','--silent','--show-error','--http1.1','--retry','0','--connect-timeout','20','--max-time','90','--config','-','-H','Content-Type: '+ctype,'--data-binary','@'+str(body_path),BASE+path],input=config,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if c.returncode:
                msg=c.stderr.decode('utf-8','replace').replace(key,'[REDACTED]')
                raise RuntimeError('curl upload failed; no POST retry: '+msg[:400])
            return c.stdout
    req=request.Request(BASE+path,data=data,headers={'Authorization':'Bearer '+key})
    if ctype: req.add_header('Content-Type',ctype)
    try:
        with request.build_opener(NoRedirect).open(req,timeout=120) as r:
            return r.read()
    except error.HTTPError as e:
        # Do not print server bodies that may reflect credentials or private URLs.
        raw=e.read().decode('utf-8','replace').replace(key,'[REDACTED]')
        raw=re.sub(r'https?://[^\s\"<>]+','[URL]',raw)
        raw=re.sub(r'sk-[A-Za-z0-9_-]+','[REDACTED]',raw)
        raise RuntimeError('HTTP '+str(e.code)+'; no POST retry performed; '+raw[:700]) from None
def save(d):
    t=LEDGER.with_suffix('.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2)); t.replace(LEDGER)
def multipart(fields, files):
    boundary='----wuye'+uuid.uuid4().hex; parts=[]
    for k,v in fields.items():
        parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+k+'"\r\n\r\n'+str(v)+'\r\n').encode())
    for f in files:
        f=Path(f).resolve(); mime=mimetypes.guess_type(f.name)[0]
        if mime not in ('image/jpeg','image/png','image/webp'): raise ValueError('Only JPG/PNG/WebP reference images')
        parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="referenceImages"; filename="'+uuid.uuid4().hex+f.suffix+'"\r\nContent-Type: '+mime+'\r\n\r\n').encode()+f.read_bytes()+b'\r\n')
    parts.append(('--'+boundary+'--\r\n').encode()); return b''.join(parts),'multipart/form-data; boundary='+boundary
p=argparse.ArgumentParser(); p.add_argument('command',choices=['models','submit','status','download']); p.add_argument('--spec'); p.add_argument('--task'); p.add_argument('--out'); p.add_argument('--execute',action='store_true'); a=p.parse_args()
if a.command=='models':
    r=json.loads(api('/v1/models')); print(json.dumps({'models':[m['id'] for m in r.get('data',[])]},ensure_ascii=False))
elif a.command=='submit':
    spec=json.loads(Path(a.spec).read_text()); images=spec.pop('localImages',[])
    costs={'Seedance 2.0-720p':1.6,'Minimax-H3-720p高配版':0.8}
    if spec.get('model') not in costs: raise ValueError('Unverified route')
    price=costs[spec['model']]
    max_duration=12 if price==0.8 else 15
    if not 4<=int(spec.get('duration',0))<=max_duration or spec.get('ratio')!='9:16' or spec.get('resolution')!='720p' or not 1<=len(images)<=9: raise ValueError('Invalid media specification')
    body,ctype=multipart(spec,images)
    if not a.execute:
        print(json.dumps({'dryRun':True,'model':spec['model'],'referenceImageCount':len(images),'maximumEstimatedChargeCNY':price},ensure_ascii=False)); raise SystemExit()
    # Exclusive lock prevents concurrent reservations. Ambiguous submissions stay reserved.
    lock=LEDGER.with_suffix('.lock'); fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        d=json.loads(LEDGER.read_text()) if LEDGER.exists() else {'budgetCNY':10,'tasks':[]}
        if sum(t['reservedCNY'] for t in d['tasks'])+price>d['budgetCNY']+1e-8: raise RuntimeError('Budget exhausted')
        row={'localId':uuid.uuid4().hex,'model':spec['model'],'reservedCNY':price,'status':'submission_unknown'}; d['tasks'].append(row); save(d)
        r=json.loads(api('/v1/videos',body,ctype)); tid=r.get('id')
        if not isinstance(tid,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',tid): raise RuntimeError('No valid task ID; check provider task logs before any new submission')
        row.update(taskId=tid,status=str(r.get('status','queued'))); save(d); print(json.dumps(row))
    finally:
        os.close(fd); lock.unlink()
else:
    if not a.task or not re.fullmatch(r'[A-Za-z0-9_-]+',a.task): raise ValueError('Invalid task ID')
    path='/v1/videos/'+a.task
    if a.command=='status':
        r=json.loads(api(path)); print(json.dumps({k:r[k] for k in ('id','status','progress') if k in r}))
    else:
        r=json.loads(api(path))
        if r.get('status')!='completed': raise RuntimeError('Not completed; do not download or resubmit')
        dest=Path(a.out).resolve()
        with dest.open('xb') as f: f.write(api(path+'/content'))
        print('Downloaded: '+str(dest))
