"""Export a reference-mapped batch; keep every selected native PNG unchanged."""

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
parser.add_argument("--scroll-width", type=int, default=790)
parser.add_argument("--jpg-only", action="store_true", help="Deliver JPEG only; keep native PNG sources outside the archive")
args = parser.parse_args()
batch = args.batch_dir.resolve()
reference = json.loads((batch / "reference-map.json").read_text())
plan = reference["actual_execution_32"]
ids = [row["id"] for row in plan]
assert len(ids) == len(set(ids))
expected_references = {f"R{i:03d}" for i in range(1, 36)} | {f"A{i:03d}" for i in range(1, 40)}
assert len(reference["entries"]) == len(expected_references), "Reference inventory has duplicate or missing rows"
assert {row["id"] for row in reference["entries"]} == expected_references
merge = reference["merge_map"]
for row in reference["entries"]:
    targets = [merge.get(key, key) for key in row["proposed_outputs"]]
    assert targets and all(key in ids or key.startswith("ASSEMBLY") for key in targets), row["id"]

production = json.loads((batch / "image-manifest.json").read_text())
assets = {row["id"]: row for row in production["assets"]}
assert len(assets) == len(production["assets"]), "Duplicate selected image manifest IDs"
assert set(assets) == set(ids)
qa = json.loads((batch / "qa-review.json").read_text())
latest = {row["id"]: row for row in qa["reviews"]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
copies = {row["id"]: row for row in json.loads((batch / "copy-v2.json").read_text())["assets"]}
for key in ids:
    path = batch / "final" / f"{key}.png"
    assert path.is_file(), key + " missing final image"
    assert latest[key]["overall_status"] in ("PASS", "PASS_WITH_LIMITATIONS"), key + " has unresolved QA"
    fidelity = latest[key].get("reference_fidelity", {})
    for axis in ("composition", "subject_scale", "color_light", "type_layout", "information_density"):
        assert fidelity.get(axis, {}).get("status") in ("PASS", "PASS_WITH_LIMITATIONS"), key + " has unresolved reference axis: " + axis
    assert sha(path) == latest[key]["sha256"] == assets[key]["sha256"], key + " changed after QA"

for row in plan:
    merged_ids = {task["id"] for task in row.get("merged_reading_tasks", [])}
    if not merged_ids:
        continue
    coverage = latest[row["id"]].get("merged_tasks_coverage", {})
    assert coverage.get("status") in ("PASS", "PASS_WITH_LIMITATIONS"), row["id"] + " has unresolved merged reading tasks"
    reviewed_ids = {task["id"] if isinstance(task, dict) else task for task in coverage.get("tasks", [])}
    assert merged_ids <= reviewed_ids, row["id"] + " is missing merged-task QA"

jpg_dir = batch / "exports" / "JPG"
preview_dir = batch / "previews"
jpg_dir.mkdir(parents=True, exist_ok=True)
preview_dir.mkdir(exist_ok=True)
records = []
for row in plan:
    key = row["id"]
    source = batch / "final" / f"{key}.png"
    target = jpg_dir / f"{key}.jpg"
    with Image.open(source) as image:
        assert image.format == "PNG", key + " final file is not PNG"
        image.load()
        size = list(image.size)
        image.convert("RGB").save(target, quality=95, subsampling=0, optimize=True)
    records.append({"id": key, "title": row["reading_task"],
                    "headline": copies[key].get("headline", ""),
                    "reference_ids": list(dict.fromkeys(row["reference_ids"] +
                                      [ref for task in row.get("merged_reading_tasks", [])
                                       for ref in task["reference_ids"]])),
                    "merged_reading_tasks": [{"id": task["id"], "title": task["reading_task"],
                                               "reference_ids": task["reference_ids"]}
                                              for task in row.get("merged_reading_tasks", [])],
                    "native_dimensions": size,
                    "png": str(source.relative_to(batch)), "png_sha256": sha(source),
                    "jpg": str(target.relative_to(batch)), "jpg_sha256": sha(target),
                    "visual_qa": latest[key]["overall_status"]})

assert len({row["png_sha256"] for row in records}) == len(records), "Selected images contain a byte-identical duplicate"

scrolls = []
root_review_pages = []
review_dir = batch / "qa-previews"
review_dir.mkdir(exist_ok=True)
for prefix, name in (("D", "冷蓝白详情长图"), ("V", "暖金补充长图")):
    group = [row for row in records if row["id"].startswith(prefix)]
    sources = []
    try:
        for row in group:
            with Image.open(batch / row["png"]) as image:
                image.load()
                sources.append(image.convert("RGB"))
        width = min(args.scroll_width, min(image.width for image in sources))
        pieces = [image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
                  if image.width != width else image.copy() for image in sources]
        result = Image.new("RGB", (width, sum(image.height for image in pieces)), "white")
        y = 0
        for image in pieces:
            result.paste(image, (0, y))
            y += image.height
            image.close()
        assert result.height < 65500, "Long image exceeds JPEG height limit"
        target = batch / "exports" / f"{name}.jpg"
        result.save(target, quality=95, subsampling=0, optimize=True)
        # Internal readable pagination for reviewing the complete stitched order.
        # These derivatives do not replace or crop the client-facing images.
        for top in range(0, result.height, 2080):
            bottom = min(top + 2200, result.height)
            page_path = review_dir / f"{prefix}_{top:05d}_{bottom:05d}.jpg"
            with result.crop((0, top, width, bottom)) as page:
                page.save(page_path, quality=94, subsampling=0, optimize=True)
            root_review_pages.append({"path": str(page_path.relative_to(batch)),
                                      "scroll": str(target.relative_to(batch)),
                                      "top": top, "bottom": bottom})
            if bottom == result.height:
                break
        scrolls.append({"title": name, "path": str(target.relative_to(batch)),
                        "dimensions": list(result.size), "sha256": sha(target),
                        "source_ids": [row["id"] for row in group],
                        "method": "Uniform-width downscaling only, aspect ratios preserved, no cropping or upscaling; native PNGs retained"})
        result.close()
    finally:
        for image in sources:
            image.close()

font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 23)
overviews = []
for start in range(0, len(records), 8):
    canvas = Image.new("RGB", (1600, 1240), "#eeeef0")
    draw = ImageDraw.Draw(canvas)
    for j, row in enumerate(records[start:start + 8]):
        x, y = (j % 4) * 400, (j // 4) * 620
        with Image.open(batch / row["png"]) as image:
            thumb = image.convert("RGB")
            thumb.thumbnail((372, 558), Image.Resampling.LANCZOS)
            canvas.paste(thumb, (x + (400 - thumb.width) // 2, y + 10 + (558 - thumb.height) // 2))
        draw.text((x + 15, y + 578), row["id"], fill="#222222", font=font)
    target = preview_dir / f"overview_{len(overviews) + 1:02d}.jpg"
    canvas.save(target, quality=94, subsampling=0, optimize=True)
    overviews.append(str(target.relative_to(batch)))

q = lambda path: quote(str(path), safe="/")
e = html.escape
parts = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>花洒参考重构套图</title><style>body{margin:0;background:#f2f3f5;color:#20232a;font-family:-apple-system,"PingFang SC",sans-serif}header,main{max-width:1480px;margin:auto;padding:28px}p{line-height:1.7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}article{background:#fff;padding:16px;border-radius:10px}article img{width:100%;height:430px;object-fit:contain}a{color:#225d9c}.meta{font-size:13px;color:#606875}section{margin:32px 0}h3{font-size:18px}</style>',
         f'<header><h1>花洒参考重构套图</h1><p>{len(records)}张独立图片，另附两条路线的组合长图。无品牌，单花洒。</p><p>{"仅交付JPG，保持各图原生尺寸；长图统一宽度并保留比例。" if args.jpg_only else "点击图片查看PNG，JPG保持各图原生尺寸；长图统一宽度并保留比例。"}</p></header><main>']
groups = (("主图与场景", "M"), ("三色SKU", "K"), ("冷蓝白详情", "D"), ("暖金补充", "V"))
for title, prefix in groups:
    parts.append(f'<section><h2>{title}</h2><div class="grid">')
    for row in records:
        if not row["id"].startswith(prefix):
            continue
        w, h = row["native_dimensions"]
        native_link = "" if args.jpg_only else f'<a href="{q(row["png"])}">PNG</a> · '
        image_link = row["jpg"] if args.jpg_only else row["png"]
        parts.append(f'<article><a href="{q(image_link)}"><img loading="lazy" src="{q(row["jpg"])}" alt="{e(row["id"])}"></a><h3>{e(row["id"])} · {e(row["title"])}</h3><p class="meta">{w}×{h} · 参考 {e(" / ".join(row["reference_ids"]))}</p>{native_link}<a href="{q(row["jpg"])}">JPG</a></article>')
    parts.append('</div></section>')
parts.append('<section><h2>组合长图</h2>')
for row in scrolls:
    parts.append(f'<p><a href="{q(row["path"])}">{e(row["title"])} · {row["dimensions"][0]}×{row["dimensions"][1]}</a></p>')
parts.append('</section></main></html>')
(batch / "交付总览.html").write_text("\n".join(parts) + "\n")
delivery = {"image_count": len(records), "png_count": 0 if args.jpg_only else len(records), "jpg_count": len(records),
            "assets": [{k: v for k, v in row.items() if k not in ("png", "png_sha256")} for row in records] if args.jpg_only else records,
            "scrolls": scrolls, "overview_pages": overviews,
            "reference_analysis_count": len(reference["entries"]), "user_acceptance": "PENDING"}
prior_receipt_path = batch / "delivery-check.json"
prior_receipt = json.loads(prior_receipt_path.read_text()) if prior_receipt_path.is_file() else {}
delivery["product_fact_notes"] = []
if prior_receipt.get("pending_product_fact", {}).get("status") == "USER_QUESTION_PENDING":
    delivery["product_fact_notes"].append("银色裸露螺纹的颜色待实物确认；现有实拍连接着配件，尚未显示该处。")
elif prior_receipt.get("pending_product_fact", {}).get("status") == "USER_CONFIRMED_SILVER":
    delivery["product_fact_notes"].append("银色SKU裸露螺纹颜色已按用户确认还原为银色；单花洒展示，接口规格未作标注。")
(batch / "delivery-manifest.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n")
readme = ["# 花洒参考重构套图", "", f"{len(records)}张独立成品，附JPG及两条路线长图。" if args.jpg_only else f"{len(records)}张独立成品，附PNG、同尺寸JPG及两条路线长图。", "",
          "[打开图片总览](交付总览.html)", "",
          "| 编号 | 内容 | JPG | 原生尺寸 |" if args.jpg_only else "| 编号 | 内容 | PNG | JPG | 原生尺寸 |",
          "| --- | --- | --- | --- |" if args.jpg_only else "| --- | --- | --- | --- | --- |"]
for row in records:
    w, h = row["native_dimensions"]
    if args.jpg_only:
        readme.append(f'| {row["id"]} | {row["title"]} | [打开]({q(row["jpg"])}) | {w}×{h} |')
    else:
        readme.append(f'| {row["id"]} | {row["title"]} | [打开]({q(row["png"])}) | [打开]({q(row["jpg"])}) | {w}×{h} |')
readme += ["", "仅交付JPG；原生制作源、参考、实拍与制作核验资料另存项目中。长图仅统一宽度后按原比例拼接。" if args.jpg_only else "PNG与JPG是同一批图片的两种格式；长图仅统一宽度后拼接，原生PNG保留。原始参考、实拍、提示词与制作核验资料另存于项目中。", ""]
if delivery["product_fact_notes"]:
    readme += delivery["product_fact_notes"] + [""]
(batch / "README.md").write_text("\n".join(readme))

paths = [batch / row[key] for row in records for key in (("jpg",) if args.jpg_only else ("png", "jpg"))]
paths += [batch / row["path"] for row in scrolls]
if not args.jpg_only:
    paths += [batch / path for path in overviews]
    paths += [batch / name for name in ("交付总览.html", "README.md", "delivery-manifest.json")]
archive_path = batch / ("花洒参考重构_JPG交付.zip" if args.jpg_only else "花洒参考重构_交付.zip")
with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in paths:
        archive.write(path, str(path.relative_to(batch)))
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert len(names) == len(set(names)) == len(paths)
    assert set(names) == {str(path.relative_to(batch)) for path in paths}

class Links(HTMLParser):
    def handle_starttag(self, tag, attributes):
        for key, value in attributes:
            if key in ("href", "src") and value:
                url = urlsplit(value)
                assert not url.scheme and not url.netloc
                target = unquote(url.path)
                assert (batch / target).is_file() and target in names

Links().feed((batch / "交付总览.html").read_text())
for row in records:
    with Image.open(batch / row["jpg"]) as image:
        assert image.format == "JPEG"
        image.load()
        assert list(image.size) == row["native_dimensions"]
for row in scrolls:
    with Image.open(batch / row["path"]) as image:
        image.load()
        assert list(image.size) == row["dimensions"]
receipt_path = batch / "delivery-check.json"
receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
receipt.update({"status": "TECHNICAL_PASS_ROOT_VISUAL_REVIEW_PENDING", "image_count": len(records),
           "checks": {"reference_mapping_inventory": "PASS", "same_hash_independent_visual_qa": "PASS",
                      "selected_png_byte_uniqueness": "PASS",
                      "native_exports_and_long_images": "PASS", "archive_crc_inventory_and_local_links": "PASS"},
           "archive": {"path": archive_path.name, "file_count": len(names), "bytes": archive_path.stat().st_size, "sha256": sha(archive_path)},
           "temporary_files": [], "deleted_files": [], "user_acceptance": "PENDING"})
receipt["root_review_pages"] = root_review_pages
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"images": len(records), "archive": str(archive_path), "bytes": archive_path.stat().st_size,
                  "scrolls": scrolls, "overview_pages": overviews}, ensure_ascii=False, indent=2))
