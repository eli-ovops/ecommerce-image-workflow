"""Apply three reviewed candidates; retain all other client JPEGs byte-for-byte."""
from pathlib import Path
import hashlib
import html
from html.parser import HTMLParser
import json
import shutil
from urllib.parse import quote, unquote
import zipfile
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent.parent
R = B / 'video-geometry-repair'
BACK = R / 'before-selection'
CHANGES = {
    'D04': ('D04-fresh-video-v2.png', '9f0d07f3c9e53e82605460dc708652cff08717c8ac8741a5439b1695423cc4a6'),
    'D06': ('D06-video-v1.png', '9222db0321db291160281eebf831b659fb951601f17d6f84550fb759c244a1bb'),
    'D11': ('D11-fresh-video-v5.png', 'e1c835d445864a04cfe2efe3aa770a0a8f867bd35f0bcb5694e2aaf2063fe128'),
}
SUSPECTS = ['M03', 'D15', 'V01', 'V06']
STATUS = 'VIDEO_RECALIBRATED_CANDIDATE_USER_REVIEW_PENDING'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
def preserve(p):
    if p.is_file():
        target = BACK / p.relative_to(B)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(p, target)

assert not (R / 'selection-export-receipt.json').exists(), 'Already applied; inspect receipt before any repeat.'
q11 = read(R / 'independent-D11-final.json')
q46 = read(R / 'independent-D04-D06-final.json')
assert q11['needs_repair'] is False and q11['sha256'] == CHANGES['D11'][1]
assert all(x['selectable'] for x in q46['items'])
assert {x['sha256'] for x in q46['items']} == {CHANGES[k][1] for k in ['D04', 'D06']}
for name, fingerprint in CHANGES.values():
    assert sha(R / name) == fingerprint

ref = read(B / 'reference-map.json')
plan = ref['actual_execution_32']
assert len(plan) == 32
manifest = read(B / 'image-manifest.json')
qa = read(B / 'qa-review.json')
delivery = read(B / 'delivery-manifest.json')
receipt = read(B / 'delivery-check.json')
prompts = read(B / 'prompt-set.json')
root_review = read(B / 'root-delivery-review.json')
unchanged = {x['id']: sha(B / x['jpg']) for x in delivery['assets'] if x['id'] not in CHANGES}
for name in ['reference-map.json', 'image-manifest.json', 'qa-review.json', 'qa-review.md',
             'delivery-manifest.json', 'delivery-check.json', 'prompt-set.json',
             'root-delivery-review.json', 'README.md', '交付总览.html']:
    preserve(B / name)

reasons = {
 'D04': {
  'composition': '冷蓝窗光、左持品右M001、上黑两行标题和下手持水流短条保留；人物改为干燥全着装展示。',
  'subject_scale': '修正过长握柄；商品与手指比例可见相容，人物占比较A009增大，作为人物展示页适配。',
  'color_light': '浅冷蓝窗光、银色镜面和白衣，保留A009/A010路线。',
  'type_layout': '日常淋浴/手持呈现两行黑字清晰；无新增参数。',
  'information_density': '主场景加下部独立手持水流近景，保持上下阅读任务。'},
 'D06': {
  'composition': '保留标题、三模式索引、大出水近景和下横侧视；只校准下横产品。',
  'subject_scale': '上微距与下横短条比例保持；下横接口裁出，不能核全长。',
  'color_light': '冷蓝反光水面、银壳白水流，沿A012/A013/R007。',
  'type_layout': '近看出水的起点及三模式文字完整，字级及分隔保留。',
  'information_density': '大水流近景与侧面出水起点互补，保留适用视觉任务。'},
 'D11': {
  'composition': '上回眸下正面持品，两格独立M001场景保留；适配为干燥全着装、水流避开人物。',
  'subject_scale': '两格商品与手指相容；人物主导，不替代商品大特写。',
  'color_light': '浅冷蓝高调窗光、白衣和镜面银壳，承接R026/A021。',
  'type_layout': '无字双场景，以细白线分隔；不复制参考强功效和未知尺寸。',
  'information_density': '承接合并D09无字人物停顿：下格拨发持品与水流独立完整；湿身举臂改为干燥拨发演示。'},
}
for key, (name, fingerprint) in CHANGES.items():
    source = R / name
    task = next(x for x in plan if x['id'] == key)
    for p in [B / 'final' / f'{key}.png', B / 'exports/JPG' / f'{key}.jpg']:
        preserve(p)
    shutil.copy2(source, B / 'final' / f'{key}.png')
    with Image.open(source) as im:
        im.load()
        dimensions = list(im.size)
        im.convert('RGB').save(B / 'exports/JPG' / f'{key}.jpg', quality=95, subsampling=0, optimize=True)
    asset = next(x for x in manifest['assets'] if x['id'] == key)
    asset.update(output=str(B / 'final' / f'{key}.png'), generated_path=str(source), sha256=fingerprint,
                 actual_dimensions=dimensions, qa_status='PASS_WITH_LIMITATIONS', user_acceptance='PENDING')
    task.update(output=asset['output'], selected_sha256=fingerprint, actual_dimensions=dimensions,
                production_status='VIDEO_TARGETED_REPAIR_PASS_WITH_LIMITATIONS', user_acceptance='PENDING')
    task['execution_adaptation'] = reasons[key]['composition']
    record = {'id': key, 'revision': name.removesuffix('.png'), 'reviewer': 'root plus independent native-image reviewer',
              'image_path': str(source), 'sha256': fingerprint, 'actual_dimensions': dimensions,
              'overall_status': 'PASS_WITH_LIMITATIONS', 'candidate_only': True,
              'reference_ids': task['reference_ids'],
              'reference_fidelity': {k: {'status':'PASS_WITH_LIMITATIONS', 'reason':v} for k,v in reasons[key].items()},
              'geometry_fidelity': {'status':'PASS_WITH_LIMITATIONS', 'whole_3d_validated':False,
                                    'evidence':'真实视频侧帧0011/0042、银91/92；本图可见轮廓相容，无精确测量。'},
              'product_fidelity': {'status':'PASS_WITH_LIMITATIONS', 'reason':'对照真实面板、双键、可见水流起点；银裸螺纹按用户确认（D06尾端裁出）。'},
              'copy_fidelity': {'status':'PASS_WITH_LIMITATIONS', 'reason':'保留已批准文字，无新增品牌、未知尺寸材质或证件。'},
              'skin_review': {'status':'PASS_WITH_LIMITATIONS', 'reason':'D04/D11从M001原始母版重新生成，原生与脸颈放大未见明显连片闭合网纹；D06无完整人物。'},
              'full74_reading_inherited_from':'production/2026-10-22_参考重构/revision-20261023-user-feedback/generation-review.jsonl',
              'actual_model':'UNKNOWN', 'actual_effort':'UNKNOWN', 'user_acceptance':'PENDING',
              'limitations':['仅可见轮廓核验，不证明精确3D、逐一孔数/流量或真人使用效果。']}
    if task.get('merged_reading_tasks'):
        record['merged_tasks_coverage'] = {'status':'PASS_WITH_LIMITATIONS','tasks':[x['id'] for x in task['merged_reading_tasks']],
                                         'reason':reasons[key]['information_density']}
    qa['reviews'].append(record)
    row = next(x for x in delivery['assets'] if x['id'] == key)
    row.update(native_dimensions=dimensions, jpg_sha256=sha(B / row['jpg']), visual_qa='PASS_WITH_LIMITATIONS')
    ps = next(x for x in prompts['assets'] if x['id'] == key)
    prompt_file = R / name.replace('.png', '-prompt.json')
    ps.update(native_source=str(source), selected_sha256=fingerprint, prompt_record=str(prompt_file),
              prompt=read(prompt_file)['prompt'], reference_roles=read(prompt_file).get('refs',[]))

reassessed = read(B / 'video-geometry-review/independent-main-reassessment.json')['items']
reassessed += read(B / 'video-geometry-review/independent-detail-reassessment.json')['items']
geo = {x['id']: x for x in reassessed}
for row in plan:
    key = row['id']
    status = '本轮修正后可见轮廓相容' if key in CHANGES else geo[key]['status']
    row['current_geometry_status'] = status
    if key not in CHANGES:
        row['production_status'] = 'VIDEO_RECHECK_VISIBLE_COMPATIBLE' if status == '本图可见轮廓相容' else 'CANDIDATE_' + ('SUSPECT' if key in SUSPECTS else 'LIMITED_VIEW')
    next(x for x in delivery['assets'] if x['id'] == key)['geometry_status'] = status
ref.update(execution_status=STATUS, current_user_acceptance='PENDING_VIDEO_REVIEW', user_acceptance='PENDING')
ref['video_revision'] = {'modified_ids':list(CHANGES),'suspect_ids':SUSPECTS,'source':'sources/product-rotation-20261023.mp4',
                         'review':'video-geometry-review/', 'limits':'可见轮廓与实物相容不等于精确3D或客户验收。'}
qa['batch_status'] = STATUS
qa['user_acceptance'] = 'PENDING'
qa['latest_increment'] = {'ids':list(CHANGES), 'source':'actual video', 'suspect_ids':SUSPECTS, 'status':STATUS}
qa['latest_status_by_id'] = {x['id']: x['overall_status'] for x in qa['reviews']}

# Rebuild only the affected cold-route scroll; keep warm scroll unchanged.
cold = next(x for x in delivery['scrolls'] if x['source_ids'][0].startswith('D'))
preserve(B / cold['path'])
pieces, ranges, y = [], {}, 0
for row in delivery['assets']:
    if not row['id'].startswith('D'):
        continue
    with Image.open(B / 'final' / (row['id'] + '.png')) as im:
        h = round(im.height * 790 / im.width)
        piece = im.convert('RGB').resize((790,h), Image.Resampling.LANCZOS)
    ranges[row['id']] = [y,y+h]
    y += h
    pieces.append(piece)
scroll = Image.new('RGB',(790,y),'white')
y = 0
for im in pieces:
    scroll.paste(im,(0,y)); y += im.height; im.close()
scroll.save(B / cold['path'], quality=95, subsampling=0, optimize=True)
cold.update(dimensions=list(scroll.size),sha256=sha(B / cold['path']))
assembly = []
for key in CHANGES:
    lo,hi = ranges[key]
    bounds = [max(0,lo-100),min(scroll.height,hi+100)]
    p = R / f'assembly-QC-{key}.jpg'
    scroll.crop((0,bounds[0],790,bounds[1])).save(p,quality=94,subsampling=0,optimize=True)
    assembly.append({'id':key,'path':str(p.relative_to(B)),'bounds':bounds})
scroll.close()

# Only overview pages 2 and 3 include modified images.
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
for start in [8,16]:
    p = B / 'previews' / f'overview_{start//8+1:02d}.jpg'; preserve(p)
    canvas=Image.new('RGB',(1600,1240),'#eeeef0'); draw=ImageDraw.Draw(canvas)
    for j,row in enumerate(delivery['assets'][start:start+8]):
        x,y=(j%4)*400,(j//4)*620
        with Image.open(B / row['jpg']) as im:
            thumb=im.convert('RGB');thumb.thumbnail((372,558),Image.Resampling.LANCZOS)
            canvas.paste(thumb,(x+(400-thumb.width)//2,y+10+(558-thumb.height)//2))
        draw.text((x+15,y+578),row['id'],fill='#222222',font=font)
    canvas.save(p,quality=94,subsampling=0,optimize=True)

archive_name = '花洒_视频校准修订_JPG.zip'
q = lambda s: quote(str(s),safe='/')
e = html.escape
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>花洒·视频校准修订候选</title><style>body{margin:0;background:#f2f3f5;color:#20232a;font-family:-apple-system,"PingFang SC",sans-serif}header,main{max-width:1480px;margin:auto;padding:28px}p{line-height:1.7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}article{background:#fff;padding:16px;border-radius:10px}article img{width:100%;height:430px;object-fit:contain}a{color:#225d9c}.meta{font-size:13px;color:#606875}.note{background:#fff2d7;padding:16px}section{margin:32px 0}h3{font-size:18px}</style>',
 '<header><h1>花洒·视频校准修订候选</h1><p>32张独立图片 + 2条组合长图。仅交付JPG，无品牌，单花洒。</p>',
 '<p class="note">本轮修正 D04、D06、D11；D04/D11从原始模特素材重新生成。M03、D15、V01、V06保留低置信造型疑点，待客户核对。当前为审阅候选，不表示精确3D或客户已验收。</p>',
 f'<p><a href="{q(archive_name)}">下载32张JPG及两条长图</a> · <a href="{q("video-geometry-repair/本轮修正3张_JPG.zip")}">仅下载本轮修正3张</a></p></header><main>']
for title,prefix in [('主图与场景','M'),('三色SKU','K'),('冷蓝白详情','D'),('暖金补充','V')]:
    parts.append(f'<section><h2>{title}</h2><div class="grid">')
    for row in delivery['assets']:
        if not row['id'].startswith(prefix):continue
        key=row['id'];w,h=row['native_dimensions']
        badge=' · 本轮已修' if key in CHANGES else (' · 造型待核对' if key in SUSPECTS else '')
        parts.append(f'<article><a href="{q(row["jpg"])}"><img loading="lazy" src="{q(row["jpg"])}" alt="{key}"></a><h3>{key} · {e(row["title"])}{badge}</h3><p class="meta">{w}×{h} · 参考 {e(" / ".join(row["reference_ids"]))}</p><a href="{q(row["jpg"])}">JPG</a></article>')
    parts.append('</div></section>')
parts.append('<section><h2>组合长图</h2>')
for row in delivery['scrolls']:
    parts.append(f'<p><a href="{q(row["path"])}">{e(row["title"])}</a></p>')
parts.append('</section></main></html>')
(B / '交付总览.html').write_text('\n'.join(parts)+'\n')

paths=[B / x['jpg'] for x in delivery['assets']]+[B / x['path'] for x in delivery['scrolls']]
archive=B / archive_name
assert not archive.exists(), 'Preserve any existing archive; do not overwrite.'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in paths:z.write(p,str(p.relative_to(B)))
mini=R / '本轮修正3张_JPG.zip'
with zipfile.ZipFile(mini,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for key in CHANGES:z.write(B / 'exports/JPG' / f'{key}.jpg',f'{key}.jpg')
for p,count in [(archive,34),(mini,3)]:
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        assert len(z.namelist())==count and all(x.endswith('.jpg') for x in z.namelist())
for key,fingerprint in unchanged.items():
    assert sha(B / 'exports/JPG' / f'{key}.jpg')==fingerprint, 'Unchanged JPEG was modified: '+key
for row in delivery['assets']:
    with Image.open(B / row['jpg']) as im:
        im.load(); assert im.format=='JPEG' and list(im.size)==row['native_dimensions']
    assert sha(B / row['jpg'])==row['jpg_sha256']
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src'):
                assert (B / unquote(value)).is_file(),value
                assert not value.lower().endswith('.png'),value
Links().feed((B / '交付总览.html').read_text())

delivery.update(user_acceptance='PENDING_VIDEO_REVIEW',status=STATUS,modified_ids=list(CHANGES),
                geometry_suspect_ids=SUSPECTS,client_archive=archive_name)
receipt.update(status=STATUS,user_acceptance='PENDING_VIDEO_REVIEW',modified_ids=list(CHANGES),
               geometry_suspect_ids=SUSPECTS,client_image_format='JPG_ONLY',native_sources_retained=True,
               archive={'path':archive_name,'file_count':34,'bytes':archive.stat().st_size,'sha256':sha(archive)},
               incremental_checks={'unchanged_29_jpegs_same_hash':True,'three_same_hash_native_reviews':True,
                                   'jpg_dimensions_decode':True,'archive_crc_jpg_only_34':True,'gallery_links':True})
root_review.update(status=STATUS,user_acceptance='PENDING_VIDEO_REVIEW',client_archive=archive_name,
                   archive_sha256=sha(archive),modified_ids=list(CHANGES),geometry_suspect_ids=SUSPECTS)
root_review['video_increment']={'native_images_actually_viewed':[str(R / x[0]) for x in CHANGES.values()],
                              'assembly_review':'PENDING','assembly_context_pages':assembly,'overview_pages':['previews/overview_02.jpg','previews/overview_03.jpg'],
                              'limitations':'M03/D15/V01/V06 remain low confidence suspects; no precise 3D or user acceptance claimed.'}
source_manifest=read(B / 'source-manifest.json')
v=read(B / 'video-geometry-review/source-receipt.json')
if not any(x['sha256']==v['sha256'] for x in source_manifest['files']):
    source_manifest['files'].append({'source':v['original'],'project_copy':v['archived'],'sha256':v['sha256'],'bytes':v['bytes'],'kind':'actual rotation video'})
for name,obj in [('reference-map.json',ref),('image-manifest.json',manifest),('qa-review.json',qa),
                 ('delivery-manifest.json',delivery),('delivery-check.json',receipt),('prompt-set.json',prompts),
                 ('root-delivery-review.json',root_review),('source-manifest.json',source_manifest)]:write(B / name,obj)
note='''# 花洒·视频校准修订候选

本轮修正 **D04、D06、D11**，其余29张JPG保持原文件。32张独立JPG，另附两条长图。

- D04：修正握柄过长与裸螺纹，人物从M001原始素材重新生成。
- D06：修正下横侧视的头根台阶，保留原排版与水流近景。
- D11：人物从M001原始素材重新生成，校准连续弧度与银螺纹；采用干燥全着装持品展示。
- M03、D15、V01、V06：仍有低置信造型疑点，待客户核对，不宣称已经解决。

[打开图片总览](交付总览.html)

[下载32张JPG及两条长图](花洒_视频校准修订_JPG.zip)

[仅下载本轮修正3张](video-geometry-repair/本轮修正3张_JPG.zip)

当前为视频校准后的审阅候选，用户验收待定。仅检查可见轮廓与真实照片/视频相容，不证明精确3D或真人性能测试。旧版本、原视频、实拍、原生生成源与失败候选均保留，不交付PNG。
'''
(B / 'README.md').write_text(note)
with (B / 'qa-review.md').open('a') as f:
    f.write('\n\n## 2026-10-23 视频校准增量\n\nD04、D06、D11按新视频及本SKU实拍修订，原生同SHA独立核验通过且保留限制。D04/D11为原M001新生成，未复用损坏人物场景。其余29张JPG未改；M03/D15/V01/V06仍待客户核对。当前不是客户最终验收。详见video-geometry-review及video-geometry-repair独立记录。\n')
selection={'status':STATUS,'modified_ids':list(CHANGES),'unchanged_jpg_count':len(unchanged),
           'unchanged_jpg_sha256':unchanged,'source_sha256':{k:v[1] for k,v in CHANGES.items()},
           'jpg_sha256':{k:sha(B / 'exports/JPG' / f'{k}.jpg') for k in CHANGES},
           'archive':receipt['archive'],'mini_archive':{'path':str(mini.relative_to(B)),'bytes':mini.stat().st_size,'sha256':sha(mini)},
           'source_video':v,'assembly_context_pages':assembly,'final_visual_assembly_check':'PENDING',
           'created_or_updated_files':'Changed exports/selected natives/metadata and archive are enumerated above; source, QC and prompts retained under video-geometry-review and video-geometry-repair; previous changed assets/metadata copied under before-selection.',
           'deleted_files':[]}
write(R / 'selection-export-receipt.json',selection)
print(json.dumps({'status':STATUS,'changed':list(CHANGES),'unchanged':len(unchanged),'archive':str(archive),
                  'mini_archive':str(mini),'assembly':assembly},ensure_ascii=False,indent=2))
