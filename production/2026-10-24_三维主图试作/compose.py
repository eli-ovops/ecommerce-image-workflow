"""Deterministic layouts. Product RGBA is composited last and never AI-redrawn."""
from pathlib import Path
import hashlib
import importlib.util
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
SPEC = importlib.util.spec_from_file_location('render_gate', ROOT/'tools/render_release_gate.py')
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
SIZE = (1600, 1600)
DARK = '#132b3e'
BLUE = '#1766c6'
GREY = '#526a7b'


def rec(path):
    p = Path(path)
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def text(draw, xy, value, size, fill=DARK, bold=False):
    font = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc' if bold else
                              '/System/Library/Fonts/Hiragino Sans GB.ttc', size)
    draw.text(xy, value, font=font, fill=fill, anchor='lt', stroke_width=0)


def layer(name, height, xy):
    p = B/'renders'/name
    with Image.open(p) as im:
        box = im.getchannel('A').getbbox()
        w = round((box[2]-box[0]) * height / (box[3]-box[1]))
    return {'file': rec(p), 'size': [w, height], 'xy': list(xy)}


def shadow(canvas, box):
    im = Image.new('RGBA', SIZE)
    ImageDraw.Draw(im).ellipse(box, fill=(15, 47, 73, 38))
    canvas.alpha_composite(im.filter(ImageFilter.GaussianBlur(18)))


def make_p01():
    with Image.open(B/'backgrounds/blue-studio-native.png') as im:
        canvas = im.convert('RGBA').resize((1600, 1740), Image.Resampling.LANCZOS).crop((0,0,1600,1600))
    d = ImageDraw.Draw(canvas)
    text(d, (112,106), '银色 · 单花洒', 32, GREY)
    d.rectangle((112,176,192,184), fill=BLUE)
    text(d, (108,236), '三档切换', 112, bold=True)
    text(d, (108,374), '手持花洒', 112, bold=True)
    text(d, (112,548), '常规 · 喷雾 · 混合', 38, GREY)
    d.rectangle((0,1450,1600,1600), fill=(249,252,255,255))
    text(d, (112,1504), '下方按键切档', 38, DARK)
    text(d, (1055,1510), '银色手持花洒', 30, GREY)
    shadow(canvas, (1195,1278,1385,1314))
    return canvas, [layer('front3q-v004.png', 1180, (832,126))]


def make_p02():
    canvas = Image.new('RGBA', SIZE, '#f8fbfd')
    d = ImageDraw.Draw(canvas)
    text(d, (110,94), '正面与背面', 96, bold=True)
    text(d, (114,222), '银色手持花洒', 36, GREY)
    d.line((800,350,800,1385), fill='#dbe7ef', width=2)
    text(d, (352,1450), '正面', 38, DARK)
    text(d, (1110,1450), '背面', 38, DARK)
    return canvas, [layer('front3q-v004.png',1050,(160,338)), layer('back3q-v003.png',1050,(928,338))]


def make_p03():
    canvas = Image.new('RGBA', SIZE, '#eef7ff')
    d = ImageDraw.Draw(canvas)
    for y in range(1600):
        v = y / 1599
        d.line((0,y,1600,y), fill=(round(247-18*v),round(251-10*v),255,255))
    text(d, (110,106), '下方按键', 105, bold=True)
    text(d, (110,243), '切换三档', 105, BLUE, True)
    for y, number, name in [(646,'01','常规出水'),(790,'02','喷雾出水'),(934,'03','混合出水')]:
        text(d,(114,y+8),number,32,BLUE)
        text(d,(190,y),name,46,DARK)
    text(d,(114,1437),'银色 · 单花洒',30,GREY)
    return canvas, [layer('buttonclose-v004.png',1080,(675,440))]


def main():
    manifest = json.loads((ROOT/'workflow/experiment.json').read_text())
    functions = {'P01':make_p01,'P02':make_p02,'P03':make_p03}
    for asset in manifest['assets']:
        key = asset['id']
        # An incomplete render is not substituted with an older or generated product.
        try:
            canvas, layers = functions[key]()
        except FileNotFoundError:
            continue
        product = G.place_layers(SIZE, layers, lambda record,_:ROOT/record['path'])
        canvas.alpha_composite(product)
        native = B/'working'/f'{key}.png'
        mask = B/'working'/f'{key}-product-mask.png'
        jpg = B/'final'/f'{key}.jpg'
        canvas.save(native)
        product.getchannel('A').point(lambda a:255 if a==255 else 0).save(mask)
        canvas.convert('RGB').save(jpg, quality=97, subsampling=0)
        asset.update(product_layers=layers,candidate=rec(native),protected_mask=rec(mask),client_jpg=rec(jpg),qa_status='AWAITING_VISUAL_REVIEW')
    (ROOT/'workflow/experiment.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    (B/'image-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    complete = [a['id'] for a in manifest['assets'] if a['candidate']]
    print(json.dumps({'composed':complete,'status':'not yet visually reviewed'}))


if __name__ == '__main__':
    main()
