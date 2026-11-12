"""Package the reviewed selection without regenerating or re-encoding JPEGs."""
from pathlib import Path
import copy, hashlib, html, importlib.util, json, shutil, zipfile
from datetime import datetime
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
NOW = datetime.now().astimezone().isoformat(timespec='seconds')

def record(path):
    path = Path(path)
    if not path.is_absolute(): path = ROOT / path
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

FINDINGS = {
 'M01':'白底完整单品，头颈连续、银色裸螺纹可见；保留A038单主体与留白。复用已审JPG，当前字节一致。',
 'M02':'暖金斜托盘、大幅斜向主体、局部小窗及底部双色标题带；保留R001明暗与层级，取消配件及促销承诺。复用已审JPG。',
 'M03':'冷蓝竖纹背景、正背双主体、红钮细节窗及底部模式条；背壳无多余喷枪/圆斑，银色螺纹。复用已审JPG。',
 'M04':'暖棕左右分栏、三档名称卡与一张真实出水照片；没有把照片绑定某一档，底带只写出水实拍。v005删除制作解释。',
 'M05':'蓝白面板大近景、粗标题与真实按压小窗；下方切档、中央手动除垢分工明确，没有把红钮写成档位开关。',
 'M06':'暖浴室占左侧主要面积，斜向大商品与右侧白底小单品形成主次；继承R008场景/单品并栏，人物已取消。',
 'M07':'黑金光带、大面板斜向商品、红金底标题与红钮细节窗；用可见外观替代原内部特效/证件。复用已审JPG。',
 'M08':'暖棕三竖卡与统一大标题，分别展示三档、下方按键、中央红钮；按压卡采用实拍，不推导清洁效果。',
 'K01':'蓝色SKU模板、大主体右置、左侧层级字卡；银色由本SKU来源层复用，裸螺纹银色，底端白色残影已清理。',
 'K02':'与K01保持相同模板与字级；使用黑色SKU来源层，非银色换色。黑色螺纹与尾部边界已核。',
 'K03':'与K01保持相同模板与字级；使用枪灰色SKU来源层，保留本色光泽。深色螺纹与尾部边界已核。',
 'D01':'冷蓝浴室首屏、大幅斜向商品、双细节底带；顶部标题留白，尾部落在台面，借鉴A006/7/9/10的场景与信息节奏，取消人物。',
 'D02':'三色错落相册，银色居中较高、两侧错位，白框与色签可读；没有粉色/滤芯，黑色标签未裁字。',
 'D03':'冷蓝五窗细节，出水大窗配红钮/白孔小窗及双底窗；大小窗关系清楚。水流直接使用SIL009原照片。',
 'D04':'两条黑框真实出水照片、蓝色01/02序号条、独立三档名称；照片只标实拍视角，底文改为下方按键切换三档。',
 'D05':'下方按键大近景配右侧三步操作和分工卡；不照搬六档、旋转拨片、安装支架或皮肤机制。',
 'D06':'冷蓝侧背展示，大背面加三局部小窗，实际侧照约束曲面；背壳没有额外圆斑或喷枪结构，没有过滤内部示意。',
 'D07':'三步横条与两张原生未按/按压照片；短红针状态来自SIL005/6。v005底文仅保留手动按压辅助清理出水孔。',
 'D08':'灰蓝岩石台面斜置大单品、上部大标题与两细节底窗；无撞击/耐摔/材质/尺寸承诺。',
 'D09':'六格外观图鉴与六项已知事实卡；v005上排为完整正面、背面及侧面实拍，下面保留孔位/按键/红钮。无未知参数。',
 'W01':'夕阳沙纹、大面板特写、暖色粗标题及真实按压操作小窗；借鉴R024/28暖景，未制造水垢前后或健康危害。',
 'W02':'棕金岩石舞台、斜向单品及深棕底部标题带；保留R033氛围与主体关系，不标未知尺寸、不含软管。',
 'L01':'D01至D09按首屏、选色、细节、出水、切档、侧背、除垢、静物、信息收尾排序；已打开全长总览及8处接缝，未见裁字/白缝。',
 'L02':'M02、M04、M08、W01、W02组成暖棕路线；裁掉M08重复上标题，商品/操作内容保留。已打开全长总览及4处接缝。',
}

NAMES = {
 'M01':'银色白底单品','M02':'棕金托盘主图','M03':'冷蓝正背主图','M04':'真实出水主图',
 'M05':'中央红钮主图','M06':'暖浴室场景主图','M07':'黑金视觉主图','M08':'三项功能主图',
 'K01':'银色SKU','K02':'黑色SKU','K03':'枪灰色SKU',
 'D01':'冷蓝首屏','D02':'三色可选','D03':'五窗细节','D04':'真实出水','D05':'按键切档',
 'D06':'侧背外观','D07':'手动按压除垢','D08':'握柄与曲面','D09':'外观图鉴与商品信息',
 'W01':'暖色按压除垢','W02':'棕金岩石单品','L01':'冷蓝完整详情长图','L02':'暖棕详情长图',
}
GROUPS = {'M':'01_主图','K':'02_SKU','D':'03_冷蓝详情','W':'04_暖色补充','L':'05_详情长图'}

def main():
    design = json.loads((BASE/'design-output.json').read_text())
    assets = copy.deepcopy(design['assets'])
    by_id = {a['id']:a for a in assets}
    assert set(by_id) == set(FINDINGS) == set(NAMES)
    ref_map = {}
    w = json.loads((ROOT/'references/2026-10-22_首批参考/wechat_manifest.json').read_text())
    for r in w['files']: ref_map[r['id']] = dict(record(r['project_path']), id=r['id'])
    archive_base = ROOT/'references/2026-10-22_首批参考/02_鼎江压缩包'
    archive = json.loads((archive_base/'archive_manifest.json').read_text())
    for r in archive['members']:
        if r.get('reference_id'):
            rid=r['reference_id']; ref_map[rid]=dict(record(archive_base/'extracted'/r['relative_path']), id=rid)
    assert len(ref_map)==74
    reused = {'M01':'production/2026-10-24_实拍主导主图/final/R01.jpg',
              'M02':'production/2026-10-24_参考广告主图/final/AD01.jpg',
              'M03':'production/2026-10-24_参考广告主图/final/AD02.jpg',
              'M07':'production/2026-10-24_参考广告主图/final/AD03.jpg'}
    for aid, source in reused.items():
        assert record(source)['sha256'] == by_id[aid]['output']['sha256']
    for a in assets:
        selected=record(a['output']['path']); assert selected==a['output'], a['id']
        for layer in a.get('source_layers',[]):
            if a['id'].startswith('L'):
                assert layer['source']==by_id[layer['id']]['output']

    coverage_path=BASE/'reference-coverage.json'
    coverage=json.loads(coverage_path.read_text())
    for r in coverage['entries']:
        if r['disposition']!='EXCLUDED_PORTRAIT':
            r['coverage_status']='CHECKED_IN_CURRENT_SUITE'
            r['actual_output_observations']=[{'id':aid,'finding':FINDINGS[aid]} for aid in r['outputs']]
            r['scope_of_check']='适用视觉任务经去重和事实替换后的承接检查；不是逐张复刻或原参考功能/结构真实性认可。'
    coverage['reviewed_at']=NOW
    coverage['customer_acceptance']='UNKNOWN'
    save(coverage_path,coverage)
    (BASE/'reference-coverage.md').write_text('# 74张参考的本轮承接\n\n'
        '复用已实际全读记录；逐图借鉴图面，以本商品实拍替换原参考造型和功能。22张独立图＋2张长图；不表示逐张复刻。4张纯人物参考因用户取消模特不进入本轮，重复/集合参考合并。\n\n'
        '|参考|处理|本轮图片|保留与改编边界|\n|---|---|---|---|\n'+''.join(
        '|{reference_id}|{disposition}|{outputs}|{boundary}|\n'.format(**dict(r,outputs='、'.join(r['outputs']) or '取消人物',boundary=r['source_prohibitions'].replace('|','／'))) for r in coverage['entries']))

    water_by_id={}
    for a in assets:
        if a['id'].startswith('L'): continue
        water_by_id[a['id']]=[r for r in a['actual_inputs'] if '/银色/原图/' in r['path'] and any('_'+str(n)+'_2.jpg' in r['path'] for n in range(95,101))]
    for a in assets:
        aid=a['id']; dst=BASE/'delivery'/GROUPS[aid[0]]/(aid+'_'+NAMES[aid]+'.jpg')
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists(): assert record(dst)['sha256']==a['output']['sha256']
        else: shutil.copyfile(ROOT/a['output']['path'],dst)
        a['selected_candidate']=a['output']; a['output']=record(dst)
        a['refs_actual_viewed']=[ref_map[r if isinstance(r,str) else r['id']] for r in a['refs_actual_viewed']]
        water=water_by_id.get(aid,[])
        if aid.startswith('L'):
            water=list({r['path']:r for c in a['children'] for r in water_by_id.get(c,[])}.values())
        a['has_model']=False; a['has_water']=bool(water); a['water_mode_assignment']=None
        a['water_photo_sources']=water
        receipt=BASE/'review'/(aid+'.json')
        save(receipt,{'status':'PASS','reviewer':'root','reviewed_at':NOW,
            'jpg_sha256':a['output']['sha256'],'finding':FINDINGS[aid],
            'checks':{k:'PASS' for k in ['product','reference_style','copy','layout','export']},
            'visual_method':'本轮实际查看成品及对应参考；未改变的已审图复用哈希，最新改字/侧窗/尾端遮罩作定向复核，长图另查总览与接缝。',
            'limits':'内部人工视觉检查；不等同客户接受、精密3D测量或自动逐孔水流识别。水流/按压照片为原实拍；广告商品图层部分为实拍引导生成层。'})
        a['review']=record(receipt); a['status']='INTERNAL_REVIEW_PASS_CUSTOMER_UNKNOWN'

    manifest={'schema_version':4,'date':'2026-10-24','experiment_id':'FULL-SUITE-NO-MODEL-024',
        'production_state':'EXPERIMENT_ENABLED','source_priority':'OWN_SKU_PHOTOS_PRIMARY_3D_SECONDARY',
        'hard_shape_lock':False,'water_policy':'REAL_PHOTOS_UNASSIGNED_MODES',
        'sku_photo_catalogs':[record('products/主推花洒/'+c+'/manifest.json') for c in ['银色','黑色','枪灰色']],
        'secondary_geometry_reference':record('production/2026-10-24_实物建模/blender/v010a/renders/strict_side.jpg'),
        'reference_coverage':record(coverage_path),'reference_read_record':coverage['reference_read_receipt'],
        'design_record':record(BASE/'design-output.json'),'source_verification':record(BASE/'generated/source-verification.json'),
        'generation_count':design['generation_count'],'generation_scope':'4 empty environments; product images reused as documented layers',
        'assets':assets,'client_acceptance':None,'customer_acceptance':'UNKNOWN'}
    save(BASE/'image-manifest.json',manifest)
    current=ROOT/'workflow/experiment.json'
    history=ROOT/'workflow/history/experiment-before-full-suite-20261024.json'
    if current.exists() and not history.exists(): history.parent.mkdir(exist_ok=True); shutil.copyfile(current,history)
    save(current,manifest)

    spec=importlib.util.spec_from_file_location('gate',ROOT/'tools/suite_release_gate.py')
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    review=gate.evaluate(manifest,ROOT,'review');save(BASE/'review/gate-review.json',review)
    customer=gate.evaluate(manifest,ROOT,'delivery');save(BASE/'review/gate-delivery.json',customer)
    assert review['status']=='PASS', review

    order={'M':0,'K':1,'D':2,'W':3,'L':4};assets.sort(key=lambda a:(order[a['id'][0]],a['id']))
    zip_path=BASE/'花洒完整电商套图_JPG_24张.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for a in assets:
            p=ROOT/a['output']['path']; z.write(p,str(p.relative_to(BASE/'delivery')))
    with zipfile.ZipFile(zip_path) as z:
        assert len(z.namelist())==24 and all(n.lower().endswith('.jpg') for n in z.namelist())
        assert z.testzip() is None
        hashes={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        assert hashes=={a['output']['sha256'] for a in assets}
    save(BASE/'review/package-verification.json',{'reviewed_at':NOW,'zip':record(zip_path),'jpg_count':24,
        'jpg_only':True,'decoded_jpg_count':review['checked_jpg_count'],'archive_readback_hash_match':True,
        'independent_images':22,'long_compositions':2,'customer_acceptance':'UNKNOWN'})
    cards=[]
    for a in assets:
        rel=str((ROOT/a['output']['path']).relative_to(BASE));title=html.escape(a['id']+' · '+NAMES[a['id']])
        cards.append('<article><a href="'+html.escape(rel)+'"><img loading="lazy" src="'+html.escape(rel)+'" alt="'+title+'"></a><h2>'+title+'</h2><p>'+str(a['dims'][0])+' × '+str(a['dims'][1])+' · <a download href="'+html.escape(rel)+'">下载JPG</a></p></article>')
    (BASE/'交付总览.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>花洒电商套图 · 24张JPG</title><style>body{margin:0;padding:28px;background:#eaf0f5;color:#122f43;font:16px system-ui}header{max-width:1200px;margin:auto auto 30px}a{color:#075cc1}main{max-width:1400px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px}article{background:white;padding:16px;border-radius:12px}img{display:block;width:100%;height:350px;object-fit:contain;background:white}h2{font-size:18px}p{line-height:1.6}</style><header><h1>花洒电商套图 · 24张JPG</h1><p>8张主图／广告素材、3张SKU、9张冷蓝详情、2张暖色补充、2张长详情。无模特。点击图片打开原尺寸。</p><p><a download href="'+html.escape(zip_path.name)+'">下载完整JPG压缩包</a></p><p>出水及按压使用本商品实拍；水流照片不逐图对应具体档位。</p></header><main>'+''.join(cards)+'</main></html>')
    (BASE/'README.md').write_text('# 本轮完整电商套图\n\n已完成24张JPG：22张独立图面＋2张组合长详情。8主图/素材、3三色SKU、9冷蓝详情模块、2暖色补充、2长详情。\n\n'
        '入口：[交付总览](交付总览.html)、[24张JPG包](花洒完整电商套图_JPG_24张.zip)、[当前清单](image-manifest.json)、[74参考承接](reference-coverage.md)。\n\n'
        '全部24项已作内部人工图面核查，文件/尺寸/来源哈希/导出数量/压缩包回读通过。客户是否接受仍UNKNOWN；review通过不代表客户接受或电商平台审核。delivery阶段因缺客户接受回执保留拒绝，不阻止提供本地审阅包。\n\n'
        '用户授权：那你继续吧；水型照片对应不确定，保留三档名称、照片不标档；无模特，仅JPG。实物照片决定商品外观，v010a只辅助空间关系，不宣称几何锁死。新增4次生图均为空环境；广告商品图层复用实拍引导生成层，水流/按压状态采用原实拍裁切。4张已审JPG字节复用，其他为本轮排版合成。三色使用各自来源层，不直接换色。\n\n'
        '唯一视觉Owner /root/blender_product_model；root验图/覆盖/打包。目标Astra/high；实际model/effort UNKNOWN。源文件、原实拍与全部旧版本保留。\n\n'
        '当前24图是74参考全部分析后按重复/不适用事实与取消人物重建的套图，不是74张成品或74张原样复刻。没有证件、未知尺寸材质、接口规格或增压过滤健康性能承诺。\n')
    print(json.dumps({'status':review['status'],'jpg_count':24,'zip':record(zip_path),'zip_mib':round(zip_path.stat().st_size/1024**2,2),'customer_acceptance':'UNKNOWN'},ensure_ascii=False))

if __name__=='__main__': main()
