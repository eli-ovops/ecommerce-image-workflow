from pathlib import Path
import getpass, os
p = Path.home()/'.config/wuyeai/shower-video.key'
print('无夜AI：仅配置花洒视频专用密钥，不提交生成、不扣费。')
print('从 API 密钥页面复制完整密钥，在此粘贴后按回车；输入不会显示。')
k = getpass.getpass('API 密钥：').strip()
if not k.startswith('sk-') or '*' in k or len(k)<16 or any(c.isspace() for c in k):
    raise SystemExit('格式不正确；没有保存。请复制完整密钥。')
p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
if p.exists():
    raise SystemExit('已存在配置；未覆盖。请告知助手检查。')
fd = os.open(p, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
with os.fdopen(fd,'w') as f: f.write(k+'\n')
del k
print('配置已保存。请回复助手“配置好了”。未产生费用。')
