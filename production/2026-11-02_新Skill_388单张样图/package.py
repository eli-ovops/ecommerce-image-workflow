# -*- coding: utf-8 -*-
from pathlib import Path
import json,zipfile,hashlib
from PIL import Image
P=Path(__file__).resolve().parent
checks=[('构图层次','有改善','上方大主体、中部粗斜白字红描边、左下产品、米色底带实现。'),('文字','可读','四条指定文字可读，360px主标题清晰。'),('品牌宣传','未见泄漏','未见竞品品牌、通用接口、旋转除垢、AIR或增压宣称。'),('红钮','未通过','左下红钮明显凹面，与376实拍较平的钮面不一致。'),('孔与盲点','未通过精确还原','部分盲点保留，但黑孔心更密且排列不稳定，未逐孔验证。'),('表面','待返修','叶纹有交叠和划痕样伪影，微纹理不如实拍自然。'),('水幕','待审','水量饱满，破碎水珠更丰富；上游仍有珠链感，起点未逐孔核实。'),('比例','有限近似','圆角长方形成立，未透视标定；安装接头仅场景示意。')]
r=dict(date='2026-11-02',skills=['qiyu-ecommerce-exact-replication','ecommerce-image-diagnosis'],optimizer='gpt-image-2-ecommerce-v1',authorization='User explicitly requested direct execution; no separate prompt approval claimed',tool='image_gen.imagegen built-in',calls=1,actual_model='UNKNOWN',size=[1254,1254],previous_ai_input=False,pixel_hard_protection=False,per_hole_verified=False,editable_layers=False,diagnosis_script_executed=False,checks=[dict(item=a,result=b,evidence=c) for a,b,c in checks],overall='STYLE_SAMPLE_ONLY_PRODUCT_REWORK_REQUIRED',customer_acceptance='UNKNOWN')
(P/'diagnosis.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
(P/'README.md').write_text('''# 新Skill 388单张样稿

已读取并应用qiyu-ecommerce-exact-replication及optimizer，分离参考布局与商品身份。一次内置imagegen调用，从原388参考和372/376实拍生成整图。Image1只提供布局/光影，Image2/3提供商品事实。用户明确要求直接执行，未另索提示词批准。真实输入角色和SHA见inputs.json，完整提示词见prompt.txt。

布局拆解：上部大横向喷头约92%宽、中央粗斜白字红描边、左下完整商品、底部暖米色带。删除竞品品牌、通用接口、官方旗舰、旋转除垢、不怕堵塞。尺寸只用已确认约30×20cm。

388-new-skills-review.jpg为1254×1254；native-generation.png为未返修的原生输出。仅做JPG导出、缩略图和放大对照，没有改动生成内容。没有商品像素硬锁，没有可编辑分层文字/商品源；不把扁平图包装为PSD或ORA。提示词可编辑，不代表可确定性重建。

已查看整图、360px、上下喷面200%、实拍细节对照及参考并排。布局和字效更贴近参考、水幕更饱满；左下红钮凹面错误，孔/盲点未精确还原，叶纹有伪影。只作为技能效果样稿，商品细节未通过，客户接受待定。

诊断技能缺少references/diagnosis_framework.md与scripts/generate_report.py；仅使用入口视觉检查思路，未运行作者脚本。当前HTML是本地自建结果页，未做点击率、转化率或平台认证预测。没有为信任分数添加任何证件或虚构背书。

原件与旧版保持，只做一张，未扩整套。当前模型工具未返回底层模型名，实际标识UNKNOWN。
''')
page='<meta charset="utf-8"><title>新Skill388样稿</title><style>body{background:#222;color:#eee;max-width:1254px;margin:auto;padding:24px;font:18px sans-serif}img{max-width:100%}td,th{border:1px solid #666;padding:12px}table{border-collapse:collapse}</style><h1>新Skill388样稿：商品细节待返修</h1><img src="388-new-skills-review.jpg"><h2>左原参考，右样稿</h2><img src="reference-left-candidate-right.jpg"><h2>左实拍，右生成细节</h2><img src="real-left-generated-right-details.jpg"><table><tr><th>检查</th><th>结果</th><th>证据</th></tr>'
for a,b,c in checks:page+=f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>'
(P/'preview-diagnosis.html').write_text(page+'</table><p>人工定性检查；原作者脚本缺失，未执行。</p>')
files=[f for f in P.rglob('*') if f.is_file() and f.suffix!='.zip' and f.name!='verification.json'];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
with zipfile.ZipFile(P/'new-skills-388-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(P))
with zipfile.ZipFile(P/'new-skills-388-source.zip') as z:
 assert z.testzip() is None;assert all(hashlib.sha256(z.read(i)).hexdigest()==sha(P/i.filename) for i in z.infolist())
r=dict(size=list(Image.open(P/'388-new-skills-review.jpg').size),archive_members=len(files),archive_bytes=(P/'new-skills-388-source.zip').stat().st_size,crc=True,member_sha_equal=True,files=[dict(file=str(f.relative_to(P)),sha256=sha(f)) for f in files]);(P/'verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if k!='files'})
