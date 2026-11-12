"""Rebuild the offline catalog from the preserved intake manifests; no image generation."""

from pathlib import Path
from urllib.parse import quote
import html
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "references/2026-10-22_首批参考"
ARCHIVE = BASE / "02_鼎江压缩包"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_url(project_path):
    return quote(Path(project_path).relative_to(BASE.relative_to(ROOT)).as_posix(), safe="/")


wechat = read(BASE / "wechat_manifest.json")
archive = read(ARCHIVE / "archive_manifest.json")
long = read(BASE / "long_preview_manifest.json")
members = [r for r in archive["members"] if r.get("reference_id")]
records = [dict(r, collection="微信参考") for r in wechat["files"]]
for member in members:
    records.append({
        "id": member["reference_id"],
        "title": member["relative_path"],
        "collection": "鼎江压缩包",
        "source_archive_member": member["relative_path"],
        "project_path": str((ARCHIVE / "extracted" / member["relative_path"]).relative_to(ROOT)),
        "bytes": member["bytes"], "sha256": member["sha256"],
        "width": member["image"]["width"], "height": member["image"]["height"],
        "integrity_verified": member["integrity_verified"], "readable": member["readable"],
    })
assert len(wechat["files"]) == 35 and len(members) == 39 and len(records) == 74
seen, duplicates = {}, []
for record in records:
    if record["sha256"] in seen:
        duplicates.append({"id": record["id"], "same_bytes_as": seen[record["sha256"]]})
    else:
        seen[record["sha256"]] = record["id"]

css = """body{margin:0;background:#f2f1ee;color:#20201e;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}
header,main{max-width:1450px;margin:auto;padding:28px}h1{font-size:30px;margin:0 0 12px}p{line-height:1.7}a{color:#2156a5}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}.card{background:white;padding:16px;border-radius:12px}
.card img{display:block;width:100%;height:440px;object-fit:contain;background:#fafafa}h3{font-size:17px;line-height:1.5;margin:12px 0 4px}
.meta{font-size:13px;color:#686862}section{margin:32px 0}summary{cursor:pointer;font-weight:600}details img{width:100%;height:auto}
footer{padding:28px;text-align:center;color:#666}"""
parts = [
    '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>电商参考图库 · 2026-10-22</title><style>' + css + '</style></head><body>',
    '<header><h1>电商参考图库</h1><p>2026-10-22 · 35张微信参考 + 压缩包39张图片 = 74张来源记录。原件保留，重复标注。</p>',
    '<p><strong>每次生图前重新查看全部参考。</strong> 点击原图可看细节。参数、品牌、认证与服务承诺需按实际商品核实。</p>',
    '<nav><a href="#wechat">微信参考</a> · <a href="#archive">压缩包参考</a> · <a href="#long">超长图可读分页</a> · <a href="../README.md">参考库说明</a></nav></header><main>',
]
for slug, label, group in (
    ("wechat", "微信参考 R001—R035", records[:35]),
    ("archive", "鼎江压缩包 A001—A039", records[35:]),
):
    parts.append(f'<section id="{slug}"><h2>{label}</h2><div class="grid">')
    for record in group:
        url = local_url(record["project_path"])
        label = html.escape(record["id"] + " · " + record["title"])
        duplicate = next((r["same_bytes_as"] for r in duplicates if r["id"] == record["id"]), None)
        note = f" · 与{duplicate}字节相同，来源保留" if duplicate else ""
        parts.append(
            f'<article class="card" id="{record["id"]}"><a href="{url}"><img loading="lazy" decoding="async" src="{url}" alt="{label}"></a>'
            f'<h3>{label}</h3><div class="meta">{record["width"]} × {record["height"]}{note}</div><p><a href="{url}">打开原图</a></p></article>'
        )
    parts.append("</div></section>")
parts.append('<section id="long"><h2>A039完整长图 · 4页可读预览</h2><p>每页从左到右逐列阅读；4页覆盖原图y=0—25920，未遗漏内容。</p>')
for i, page in enumerate(long["pages"], 1):
    url = local_url(page["path"])
    parts.append(f'<details><summary>展开第{i}页</summary><p><a href="{url}">单独打开分页</a></p><img loading="lazy" src="{url}" alt="A039第{i}页"></details>')
parts.append('</section></main><footer>图片均在本项目内，无远程图片、外部字体或脚本。本图册为参考预览，没有生成新的商品广告图。</footer></body></html>')
(BASE / "参考图库.html").write_text("\n".join(parts) + "\n", encoding="utf-8")

lines = [
    "# 压缩包参考逐图索引", "",
    "来源：`10.11鼎江.rar`。39张JPEG，3个目录，0个非图片文件。全部成员解压和完整解码通过；A编号对应`archive_manifest.json`。", "",
    "原始成员名保留。标题、参数和颜色名称是来源资料，不构成本项目新商品的已核实事实。", "",
    "| 编号 | 原始成员 | 图片尺寸 | 原图 |", "| --- | --- | --- | --- |",
]
for record in records[35:]:
    lines.append(f'| {record["id"]} | {record["source_archive_member"]} | {record["width"]}×{record["height"]} | [打开]({local_url(record["project_path"])}) |')
(BASE / "压缩包参考索引.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

preview_paths = [r["path"] for r in wechat["contact_sheets"]]
preview_paths += [str((ARCHIVE / "previews" / f"contact_sheet_{i:02d}.png").relative_to(ROOT)) for i in range(1, 5)]
preview_paths += [r["path"] for r in long["pages"]]
receipt = {
    "date": "2026-10-22", "timezone": "Asia/Shanghai", "project_root": str(ROOT),
    "status": "参考接收整理已完成", "scope": "保存、编号、解压、索引、视觉预览；没有生成新商品图或外部上传",
    "image_source_records": 74, "wechat_images": 35, "archive_images": 39, "unique_byte_hashes": len(seen),
    "byte_identical_duplicates_preserved": duplicates,
    "archive_source": archive["source_archive"],
    "archive_project_copy": str((ARCHIVE / "10.11鼎江.rar").relative_to(ROOT)),
    "verification": {
        "wechat_source_copy_sha256_match": wechat["all_source_copy_sha256_match"],
        "wechat_full_decode": wechat["all_images_decode"],
        "archive_byte_identical": archive["copied_archive"]["byte_identical"],
        "archive_all_members_verified": all(r["integrity_verified"] for r in members),
        "archive_file_count": archive["file_count"], "archive_directories": archive["directory_count"],
        "all_archive_images_readable": all(r["readable"] for r in members), "original_downloads_preserved": True,
    },
    "visual_review": {
        "method": "用户附件原图、全部9页联系表、A039全部4页可读分页；未做逐字OCR或商品真实性验证",
        "all_source_ids_covered": [r["id"] for r in records], "viewed_preview_paths": preview_paths,
        "long_original_size": [790, 25920], "long_pixel_coverage": "全宽790px，y=0..25920，12段连续覆盖",
        "repeat_review_required_before_every_generation_call": True,
    },
    "instructions_entry": "AGENTS.md", "gallery": str((BASE / "参考图库.html").relative_to(ROOT)), "files": records,
    "generated_files_purpose": {
        "previews": "供当前及后续查看参考，保留交付物",
        "indexes_and_gallery": "来源映射、浏览与执行入口", "manifests": "副本及解压完整性证据",
        "tools/build_reference_catalog.py": "离线重建本批图册与汇总清单；不会生成商品图",
    },
    "temporary_files": [],
}
save(BASE / "接收记录.json", receipt)
print(json.dumps({"records": 74, "unique_byte_hashes": len(seen), "duplicates": duplicates, "preview_pages": len(preview_paths), "gallery": str(BASE / "参考图库.html")}, ensure_ascii=False))
