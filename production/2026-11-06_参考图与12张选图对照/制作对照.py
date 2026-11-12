# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import os, html, urllib.parse

root = Path('/Volumes/EXTERNAL/电商 作图工作流')
out = root / 'production/2026-11-06_参考图与12张选图对照'
out.mkdir(parents=True, exist_ok=True)
refdir = root / 'references/2026-11-04_方形三键花洒_电商参考/原图'
refs = {n: refdir / ('微信图片_20261104124257_%d_2.jpg' % n) for n in range(493, 513)}
selected = {
    '01 主图': 'production/2026-11-05_方形三键花洒_银色主图新稿/银色主图_按键修正_候选02.png',
    '02 雨淋出水': 'production/2026-11-04_方形三键花洒_普通出水图/雨淋图_水量加大_候选09.png',
    '03 浴室场景': 'production/2026-11-05_方形三键花洒_五图回源修订/03_场景_候选.png',
    '04 喷雾出水': 'production/2026-11-04_方形三键花洒_喷雾出水图/喷雾图_用户选定_20261105.png',
    '05 顶部喷枪': 'production/2026-11-04_方形三键花洒_顶部喷枪图/银色花洒_顶部喷枪_按红线截断_最终.jpg',
    '06 三档展示': 'production/2026-11-05_方形三键花洒_参考图脱敏版/银色三档_喷雾放大_候选03.png',
    '07 三键功能': 'production/2026-11-05_方形三键花洒_三键功能对应图/三键功能对应_候选02.png',
    '08 侧面与背面': 'production/2026-11-05_方形三键花洒_侧背外形图/侧背外形_新增侧拍重做_候选03.png',
    '09 三色展示': 'production/2026-11-05_方形三键花洒_三色展示图/三色展示_银色居中_候选02.png',
    '10 产品尺寸': 'production/2026-11-05_方形三键花洒_尺寸图/产品尺寸_候选01.png',
    '11 喷面近景': 'production/2026-11-05_方形三键花洒_喷面细节图/喷面细节_横向近景_候选03.png',
    '13 喷枪冲洗场景': 'production/2026-11-05_方形三键花洒_喷枪冲洗场景图/喷枪冲洗_用户通过版.png',
}
selected = {name: root / path for name, path in selected.items()}
for path in list(refs.values()) + list(selected.values()):
    if not path.is_file():
        raise SystemExit('素材不存在：' + str(path))

font = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
title_font = ImageFont.truetype(font, 36)
caption_font = ImageFont.truetype(font, 24)
sub_font = ImageFont.truetype(font, 20)

def sheet(path, title, subtitle, entries, columns, tile):
    margin, gap, caption, header = 32, 20, 40, 112
    rows = (len(entries) + columns - 1) // columns
    width = margin * 2 + columns * tile + (columns - 1) * gap
    height = header + rows * (tile + caption + gap) + margin
    canvas = Image.new('RGB', (width, height), '#f5efe7')
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), title, font=title_font, fill='#38261a')
    draw.text((margin, 66), subtitle, font=sub_font, fill='#765d49')
    for idx, (name, image_path) in enumerate(entries):
        x = margin + (idx % columns) * (tile + gap)
        y = header + (idx // columns) * (tile + caption + gap)
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=8, fill='white')
        with Image.open(image_path) as im:
            im = ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((tile - 10, tile - 10), Image.Resampling.LANCZOS)
            canvas.paste(im, (x + (tile - im.width) // 2, y + (tile - im.height) // 2))
        draw.text((x + 4, y + tile + 5), name, font=caption_font, fill='#3c2719')
    canvas.save(path, quality=92, subsampling=0)

sheet(out / '参考图20张总览.jpg', '参考图：20 张', '编号对应原参考文件尾号；参考功能不自动适用于本产品。', [(str(n), path) for n, path in refs.items()], 5, 300)
sheet(out / '本批已选12张总览.jpg', '本批选定：12 张', '沿用此前验收编号；12 号手持三键图不纳入。', list(selected.items()), 4, 370)

def link(path):
    return urllib.parse.quote(os.path.relpath(path, out), safe='/')

def cards(items):
    if not items:
        return '<p class="empty">本批没有对应选图</p>'
    return ''.join('<a class="card" href="%s"><img loading="lazy" src="%s" alt="%s"><span>%s</span></a>' % (link(path), link(path), html.escape(name), html.escape(name)) for name, path in items)

groups = [
    ('主视觉与整体外观', '参考中有黑金主图、安装外观和正面商品图；本批已有银色主图、浴室场景及侧背外观。', [493,497,498,499,500,511], ['01 主图','03 浴室场景','08 侧面与背面']),
    ('雨淋出水', '参考中多张手持侧前视角展示雨淋；本批已有雨淋效果图。', [494,495,503,505], ['02 雨淋出水']),
    ('三档及顶部喷枪', '参考中的顶部冲洗机位可借鉴；本批已有喷雾、喷枪、三档总览及冲洗场景。', [501,512], ['04 喷雾出水','05 顶部喷枪','06 三档展示','13 喷枪冲洗场景']),
    ('喷面与按键细节', '参考包含横向喷面近景和手持按键特写；本批有喷面近景和三键功能说明，先前手持特写已排除。', [508,509], ['07 三键功能','11 喷面近景']),
    ('颜色与尺寸', '参考有三色展示；本批有三色与尺寸图。', [510], ['09 三色展示','10 产品尺寸']),
    ('参考里出现、但本款尚无依据的宣传', '增压测试、耐摔、止水、拆卸和接口规格等不能仅凭竞品图套用。', [496,502,504,506,507], []),
]
sections = []
for title, description, nums, names in groups:
    refitems = [('参考 %d' % n, refs[n]) for n in nums]
    ownitems = [(name, selected[name]) for name in names]
    sections.append('<section><h2>%s</h2><p>%s</p><div class="compare"><div><h3>参考图</h3><div class="grid">%s</div></div><div><h3>本批已选图</h3><div class="grid">%s</div></div></div></section>' % (html.escape(title), html.escape(description), cards(refitems), cards(ownitems)))

page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>参考图与本批12张对照</title><style>body{margin:0;background:#f5f0e9;color:#292018;font:16px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1500px;margin:auto;padding:30px}h1{margin:0 0 8px;font-size:32px}h2{margin:0;font-size:24px}p{margin:8px 0 18px;color:#5b4b3f}section{background:white;border-radius:16px;margin:20px 0;padding:24px;box-shadow:0 4px 20px #5d3c1712}.compare{display:grid;grid-template-columns:1fr 1fr;gap:28px}.compare>div{min-width:0}h3{font-size:18px;color:#754f30;border-bottom:1px solid #e6d8c8;padding-bottom:8px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.card{background:#faf7f2;border:1px solid #e4d8ca;border-radius:8px;overflow:hidden;color:#241b14;text-decoration:none}.card img{display:block;width:100%;aspect-ratio:1;object-fit:contain;background:#eee6dc}.card span{display:block;padding:8px}.empty{color:#8c7c6d}.callout{background:#efe4d5;padding:16px;border-radius:10px}@media(max-width:760px){main{padding:16px}.compare{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><main><h1>参考图与本批 12 张对照</h1><p>20 张参考按主题与选定图并排，点击缩略图可查看原图。保留此前验收编号；12 号手持三键特写已排除。</p><p class="callout">参考图用于比较构图与表达。商品结构、功能和宣传依据以本产品实拍与确认信息为准。下方是本批选图对照，不代表客户已验收整套。</p>''' + ''.join(sections) + '''<section><h2>可考虑补充的表达</h2><p>① 安装后的浴室使用场景或局部手持场景：参考 493、495、500，可区别于现有静态场景；需避免暗示额外配件随货。② 正背与顶部喷枪口组合细节：参考 509、512，可减少正面画面重复；现有侧背图和喷枪图已有一定覆盖。③ 如需详细页，可将已选图按主视觉、三档水型、操作、结构、尺寸、三色排序；长图是版式整理，不新增功能。</p><p>竞品图的增压倍数、耐摔、止水、可拆洗、接口规格、射程等未经本款确认，暂不作为待做卖点。</p></section></main></html>'''
(out / '对照总览.html').write_text(page, encoding='utf-8')
print('输出目录：', out)
print('参考：%d 张；选定：%d 张；缺失素材：0' % (len(refs), len(selected)))
