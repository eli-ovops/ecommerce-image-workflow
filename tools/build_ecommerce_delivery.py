"""Package existing final images; this script never generates product imagery."""

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import zipfile

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument("batch_dir", type=Path)
args = parser.parse_args()
batch = args.batch_dir.resolve()
ids = ([f"SIL-P{i:02d}" for i in range(1, 9)]
       + [f"SIL-D{i:02d}" for i in range(1, 7)] + ["BLK-P01", "GMT-P01"])
final = batch / "final"
missing = [key for key in ids if not (final / f"{key}.png").is_file()]
if missing:
    raise SystemExit("Required final images missing: " + ", ".join(missing))

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
qa_path = batch / "qa-review.json"
if not qa_path.is_file():
    raise SystemExit("Independent visual QA record is missing")
qa = json.loads(qa_path.read_text(encoding="utf-8"))
latest_reviews = {record["id"]: record for record in qa.get("reviews", [])}
final_hashes = {}
for key in ids:
    review = latest_reviews.get(key)
    if not review or review.get("overall_status") not in ("PASS", "PASS_WITH_LIMITATIONS"):
        raise SystemExit("Final asset has not passed independent visual QA: " + key)
    final_hashes[key] = sha(final / f"{key}.png")
    if final_hashes[key] != review.get("sha256"):
        raise SystemExit("Final asset changed after its recorded visual QA: " + key)

export = batch / "exports"
jpg_dir = export / "JPG"
preview_dir = batch / "previews"
jpg_dir.mkdir(parents=True, exist_ok=True)
preview_dir.mkdir(exist_ok=True)
copy = json.loads((batch / "copy.json").read_text(encoding="utf-8"))
captions = {row["id"]: row for row in copy["assets"]}
records = []
for key in ids:
    source = final / f"{key}.png"
    target = jpg_dir / f"{key}.jpg"
    with Image.open(source) as image:
        image.load()
        rgb = image.convert("RGB")
        rgb.save(target, quality=95, subsampling=0, optimize=True)
        size = list(image.size)
    records.append({"id": key, "title": captions[key]["headline"] or "无字白底单品图",
                    "png": str(source.relative_to(batch)), "jpg": str(target.relative_to(batch)),
                    "dimensions": size, "png_sha256": final_hashes[key], "jpg_sha256": sha(target),
                    "independent_visual_qa": latest_reviews[key]["overall_status"]})

detail_sources = [final / f"SIL-D{i:02d}.png" for i in range(1, 7)]
detail_images = []
try:
    for source in detail_sources:
        with Image.open(source) as image:
            image.load()
            detail_images.append(image.convert("RGB"))
    widths = {image.width for image in detail_images}
    if len(widths) != 1:
        raise SystemExit("Detail widths differ: no automatic image scaling was applied")
    long_image = Image.new("RGB", (detail_images[0].width, sum(im.height for im in detail_images)), "white")
    y = 0
    for image in detail_images:
        long_image.paste(image, (0, y))
        y += image.height
    long_path = export / "银色详情长图.jpg"
    long_image.save(long_path, quality=95, subsampling=0, optimize=True)
    long_size = list(long_image.size)
finally:
    for image in detail_images:
        image.close()

font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
preview_paths = []
for start in range(0, len(records), 8):
    group = records[start:start + 8]
    canvas = Image.new("RGB", (1600, 1240), "#eeeeec")
    draw = ImageDraw.Draw(canvas)
    for j, record in enumerate(group):
        x, y = (j % 4) * 400, (j // 4) * 620
        with Image.open(batch / record["png"]) as image:
            image = image.convert("RGB")
            image.thumbnail((372, 558), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (400 - image.width) // 2, y + (558 - image.height) // 2 + 10))
        draw.text((x + 15, y + 578), record["id"], font=font, fill="#222222")
    path = preview_dir / f"delivery_overview_{len(preview_paths) + 1:02d}.jpg"
    canvas.save(path, quality=94, subsampling=0, optimize=True)
    preview_paths.append(str(path.relative_to(batch)))

e = html.escape
q = lambda value: quote(str(value), safe="/")
css = """body{margin:0;background:#f3f2ee;color:#222;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}
header,main{max-width:1440px;margin:auto;padding:28px}p{line-height:1.7}a{color:#28579d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}
article{padding:16px;background:white;border-radius:12px}article img{width:100%;height:410px;object-fit:contain}h3{font-size:18px}.meta{color:#666;font-size:13px}
section{margin:36px 0}.long{width:min(100%,780px);display:block;margin:auto}summary{cursor:pointer;padding:12px;background:white}footer{padding:32px;text-align:center;color:#666}"""
parts = [f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>花洒套图交付总览</title><style>{css}</style></head><body>',
         '<header><h1>花洒套图交付总览</h1><p>银色8张独立图＋6屏详情；黑色、枪灰色各1张SKU图。无品牌，单花洒，不含软管和支架。</p>',
         '<p>点击图片打开PNG原图，也可下载同尺寸JPG。下方另附6屏拼接详情长图。</p></header><main>']
for label, group in (("银色独立图片", records[:8]), ("银色详情页", records[8:14]), ("黑色与枪灰色SKU", records[14:])):
    parts.append(f"<section><h2>{label}</h2><div class=\"grid\">")
    for record in group:
        parts.append(f'<article><a href="{q(record["png"])}"><img loading="lazy" src="{q(record["jpg"])}" alt="{e(record["id"])}"></a><h3>{e(record["id"])} · {e(record["title"])}</h3><p class="meta">{record["dimensions"][0]} × {record["dimensions"][1]}</p><p><a href="{q(record["png"])}">PNG原图</a> · <a href="{q(record["jpg"])}">JPG版本</a></p></article>')
    parts.append("</div></section>")
long_rel = str(long_path.relative_to(batch))
parts.append(f'<section><h2>银色6屏详情长图</h2><p><a href="{q(long_rel)}">打开完整长图 · {long_size[0]} × {long_size[1]}</a></p><details><summary>展开长图预览</summary><img class="long" loading="lazy" src="{q(long_rel)}" alt="银色详情长图"></details></section>')
parts.append('</main><footer>文件尺寸及校验值见同目录 delivery-manifest.json。</footer></body></html>')
(batch / "交付总览.html").write_text("\n".join(parts) + "\n", encoding="utf-8")

delivery = {"date": "2026-10-22", "timezone": "Asia/Shanghai", "image_count": 16,
            "png_count": 16, "jpg_count": 16, "source_images_untouched": True,
            "assets": records, "overview_pages": preview_paths,
            "detail_long_image": {"path": long_rel, "dimensions": long_size, "sha256": sha(long_path),
                                  "method": "Six original detail screens pasted vertically in D01-D06 order, without resizing or cropping"},
            "user_acceptance": "PENDING", "platform_specific_compliance": "NOT_REQUESTED"}
(batch / "delivery-manifest.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
readme = ["# 花洒套图交付", "", "2026-10-22。16张独立成品：银色8张独立图、6屏详情，黑色/枪灰色各1张SKU图。另附同尺寸JPG和6屏拼接长图。", "",
          "- [打开可视总览](交付总览.html)", "- [文件及尺寸清单](delivery-manifest.json)", "",
          "PNG与JPG是同一套16张图片的不同格式，另附6屏详情拼接长图。制作来源、候选、提示词及核验记录单独保留在项目中，不混入客户用图压缩包。", "",
          "| 编号 | PNG | JPG | 实际尺寸 |", "| --- | --- | --- | --- |"]
for record in records:
    readme.append(f'| {record["id"]} | [打开]({q(record["png"])}) | [打开]({q(record["jpg"])}) | {record["dimensions"][0]}×{record["dimensions"][1]} |')
readme.extend(["", f"[银色详情长图]({q(long_rel)})（{long_size[0]}×{long_size[1]}）。", ""])
(batch / "README.md").write_text("\n".join(readme), encoding="utf-8")
archive_path = batch / "花洒套图_交付.zip"
zip_paths = ([batch / record[k] for record in records for k in ("png", "jpg")]
             + [long_path, batch / "交付总览.html", batch / "README.md", batch / "delivery-manifest.json"])
for folder in (batch / "previews",):
    if folder.is_dir():
        zip_paths.extend(sorted(p for p in folder.rglob("*") if p.is_file()))
with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in zip_paths:
        archive.write(path, path.relative_to(batch))
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert len(names) == len(set(names)) == len(zip_paths)
    assert set(names) == {str(path.relative_to(batch)) for path in zip_paths}

class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attributes):
        for key, value in attributes:
            if key in ("href", "src") and value:
                self.targets.append(value)

links = LocalLinks()
links.feed((batch / "交付总览.html").read_text(encoding="utf-8"))
for target in links.targets:
    url = urlsplit(target)
    assert not url.scheme and not url.netloc, "Unexpected external URL: " + target
    relative = unquote(url.path)
    assert (batch / relative).is_file(), "Missing gallery target: " + relative
    assert relative in names, "Gallery target missing from ZIP: " + relative
for record in records:
    with Image.open(batch / record["jpg"]) as image:
        image.load()
        assert list(image.size) == record["dimensions"]
with Image.open(long_path) as image:
    image.load()
    assert list(image.size) == long_size
assert len(records) == len({record["id"] for record in records}) == 16

check_path = batch / "delivery-check.json"
check = json.loads(check_path.read_text(encoding="utf-8")) if check_path.exists() else {}
check.update({
    "status": "TECHNICAL_PASS_VISUAL_QA_COMPLETE_USER_REVIEW_PENDING",
    "image_count": len(records),
    "png_count": len(records),
    "jpg_count": len(records),
    "detail_long_dimensions": long_size,
    "checks": {
        "independent_visual_qa_for_all_final_hashes": "PASS",
        "image_decoding_and_native_dimensions": "PASS",
        "gallery_links_local_existing_and_in_archive": "PASS",
        "zip_crc_unique_paths_and_complete_inventory": "PASS"
    },
    "gallery_link_count": len(links.targets),
    "archive": {"path": str(archive_path.relative_to(batch)), "file_count": len(names),
                "bytes": archive_path.stat().st_size, "sha256": sha(archive_path)},
    "user_acceptance": "PENDING"
})
check_path.write_text(json.dumps(check, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"image_count": len(records), "detail_long_dimensions": long_size,
                  "archive": str(archive_path), "archive_bytes": archive_path.stat().st_size,
                  "overview_pages": preview_paths}, ensure_ascii=False, indent=2))
