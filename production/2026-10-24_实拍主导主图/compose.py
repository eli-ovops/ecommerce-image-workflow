"""Native-size typesetting, with disclosed bounded local image_gen patch repairs."""
from pathlib import Path
import hashlib
import importlib.util
import json
from PIL import Image,ImageDraw,ImageFont

B=Path(__file__).resolve().parent
ROOT=B.parents[1]
SPEC=importlib.util.spec_from_file_location('photo_gate',ROOT/'tools/photo_guided_gate.py')
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def rec(path):
    p=Path(path)
    return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def text(draw,xy,value,size,fill,bold=False):
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc' if bold else '/System/Library/Fonts/Hiragino Sans GB.ttc',size)
    draw.text(xy,value,font=font,fill=fill,anchor='lt')


def main():
    m=json.loads((ROOT/'workflow/experiment.json').read_text())
    log=json.loads((B/'production-log.json').read_text())
    calls={c['id']:c for c in log['calls']}
    plan={
      'R01':{'native':'R01-v002-native.png','selected':'R01-v003-composite.png','call':'R01_fix','prompt':'R01-local-fix.txt','photo_ids':['SIL001','SIL003','SIL004'],'repair':'R01-roi-evidence.json','mask':'R01-roi-composite-mask.png','text':[],'native_transform':{'uniform_scale':.82,'background_rgb':[255,255,255]}},
      'R02':{'native':'R02-v001-native.png','selected':'R02-v002-composite.png','call':'R02','prompt':'R02.txt','photo_ids':['SIL001','SIL003','SIL004'],'repair':'R02-reuse-evidence.json','mask':'R02-reuse-mask.png','text':[[48,100,430,480]]},
      'R03':{'native':'R03-v001-native.png','selected':'R03-v001-native.png','call':'R03','prompt':'R03.txt','photo_ids':['SIL001','SIL005','SIL004'],'text':[[44,60,350,675]]},
    }
    source_map={s['id']:s['file']['sha256'] for s in m['appearance_sources']}
    for a in m['assets']:
        key=a['id'];p=plan[key];native=B/'generated'/p['native'];selected=B/'generated'/p['selected'];call=calls[p['call']]
        a.update(appearance_source_ids=p['photo_ids'],generated_native=rec(native),prompt=rec(B/'prompts'/p['prompt']),text_edit_regions=p['text'],qa_status='AWAITING_VISUAL_REVIEW')
        if p.get('native_transform'):a['native_transform']=p['native_transform']
        if p.get('repair'):
            a['local_repair']={'file':rec(selected),'mask':rec(B/'generated'/p['mask']),'tool_patch':rec(B/'generated/R01-roi-tool-native.png'),
                'evidence':rec(B/'generated'/p['repair']),'base_sha256':a['generated_native']['sha256'],'tool':'builtin_image_gen',
                'additional_photo_reference':'SIL005 actual nozzle closeup used to produce the ROI repair patch'}
        receipt={'tool':'builtin_image_gen','native_sha256':a['generated_native']['sha256'],'prompt_sha256':a['prompt']['sha256'],
            'appearance_source_sha256':sorted({source_map[s] for s in p['photo_ids']}),'actual_call':call,
            'local_repair':a.get('local_repair'),'batch_log':rec(B/'production-log.json'),
            'hard_shape_lock':False,'note':'Actual referenced real photographs are primary; 3D side secondary. Patch-composited full images are explicitly not native full-frame tool outputs.'}
        rp=B/f'review/{key}-generation-receipt.json';rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2));a['generation_receipt']=rec(rp)
        with Image.open(selected) as im:canvas=G.typesetting_baseline(im,a)
        draw=ImageDraw.Draw(canvas)
        if key=='R02':
            text(draw,(64,142),'三档出水',72,'#fff8e9',True)
            text(draw,(64,238),'手持花洒',72,'#fff8e9',True)
            text(draw,(67,350),'常规 · 喷雾 · 混合',26,'#f4dfbc')
            text(draw,(67,414),'银色｜单花洒',26,'#fff1d7')
            a['approved_copy']=['三档出水','手持花洒','常规 · 喷雾 · 混合','银色｜单花洒']
        elif key=='R03':
            text(draw,(64,96),'下方按键',62,'#102a3e',True)
            text(draw,(64,180),'切换三档',62,'#126bc4',True)
            for y,label in [(374,'常规出水'),(457,'喷雾出水'),(540,'混合出水')]:text(draw,(68,y),label,31,'#25485f')
            a['approved_copy']=['下方按键','切换三档','常规出水','喷雾出水','混合出水']
        else:a['approved_copy']=[]
        output=B/f'working/{key}.png';jpg=B/f'final/{key}.jpg';canvas.save(output);canvas.save(jpg,quality=97,subsampling=0)
        a['candidate']=rec(output);a['client_jpg']=rec(jpg);a['actual_dimensions']=list(canvas.size)
    (ROOT/'workflow/experiment.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(B/'image-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
    print('Composed three JPGs at actual native 1254-square canvas; visual review pending')


if __name__=='__main__':main()
