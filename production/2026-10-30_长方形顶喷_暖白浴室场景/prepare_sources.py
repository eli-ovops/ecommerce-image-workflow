from pathlib import Path
import shutil,json,hashlib
P=Path(__file__).resolve().parent
root=P.parent.parent
(P/'sources').mkdir(exist_ok=True)
files=[root/'products/长方形拉钮顶喷/原始实拍20261030'/('微信图片_20261030154107_'+str(n)+'_2.jpg') for n in [374,376]]+list((root/'products/长方形拉钮顶喷/接头补充实拍20261030').glob('*.jpg'))
for f in files:shutil.copy2(f,P/'sources'/f.name)
shutil.copy2(P.parent/'2026-10-30_长方形顶喷_背面接口与斜侧两图/商品基线_v3.blend',P/'商品基线_v3.blend')
(P/'source-manifest.json').write_text(json.dumps([{'source':str(f.resolve()),'archived':'sources/'+f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'actual_visual_read':'本会话已实看完整工具预览；376本轮重看，374与接口照沿用本会话此前实看记录'} for f in files],ensure_ascii=False,indent=2))
