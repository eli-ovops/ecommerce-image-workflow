from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json

OUT = Path(__file__).resolve().parent
manifest = json.loads((OUT / 'trial-manifest.json').read_text())
sources = {x['view']: Path(x['source']) for x in manifest['selected_images']}
sheet = Image.open(manifest['blender_reference']['existing_review']).convert('RGB')
font_path = next(p for p in [
    Path('/System/Library/Fonts/PingFang.ttc'),
    Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),
] if p.exists())
font = ImageFont.truetype(str(font_path), 32)
small = ImageFont.truetype(str(font_path), 25)
title = ImageFont.truetype(str(font_path), 46)
canvas = Image.new('RGB', (2700, 2040), '#f5f5f2')
draw = ImageDraw.Draw(canvas)
draw.text((36, 18), '圆形花洒｜实拍、Tripo 免费试样、现有 Blender 对照', font=title, fill='#111827')
draw.text((36, 85), 'H2.5 单图生成；多视图需付费未执行。统一朝向便于观察，未做像素或尺寸配准。', font=small, fill='#4b5563')
for i, heading in enumerate(['实拍（判断实物的依据）', 'Tripo 单图试样（未经修补）', '现有 Blender（待用户确认）']):
    draw.text((36 + 900*i, 140), heading, font=font, fill='#111827')

def existing_view(col):
    # Presentation-only crop/rotation of the existing review sheet.
    return sheet.crop((col*500 + 14, 40, col*500 + 484, 625)).rotate(90, expand=True)

rows = [
    ('正面：喷嘴、红钮、银色切换件', Image.open(sources['front']), Image.open(OUT/'front-texture.png'), existing_view(0)),
    ('背面：检查凭空增加的结构', Image.open(sources['back']), ImageOps.mirror(Image.open(OUT/'back-texture.png')), existing_view(1)),
    ('侧面：检查厚度、弯曲与凸出件', Image.open(sources['side_a']), ImageOps.mirror(Image.open(OUT/'side-geometry.png')), existing_view(2)),
]
for row, (label, *images) in enumerate(rows):
    y = 206 + row*580
    draw.text((36, y), label, font=small, fill='#4b5563')
    for col, im in enumerate(images):
        tile = ImageOps.contain(im.convert('RGB'), (864, 510))
        x = col*900 + 18 + (864-tile.width)//2
        py = y + 43 + (510-tile.height)//2
        canvas.paste(tile, (x, py))
draw.text((36, 1965), '本图仅用于结构审阅。实拍有透视；渲染为正交视图。未验证毫米精度、螺纹标准或商业授权。', font=small, fill='#4b5563')
canvas.save(OUT/'comparison-sheet.jpg', quality=92, subsampling=0)
print(OUT/'comparison-sheet.jpg')
