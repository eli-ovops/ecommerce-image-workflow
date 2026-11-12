"""Select only the latest same-hash QA-approved candidates. No image generation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("batch", type=Path)
args = parser.parse_args()
batch = args.batch.resolve()
reference = json.loads((batch / "reference-map.json").read_text())
qa = json.loads((batch / "qa-review.json").read_text())
latest = {row["id"]: row for row in qa["reviews"]}
assets = []
(batch / "final").mkdir(exist_ok=True)
for task in reference["actual_execution_32"]:
    key = task["id"]
    review = latest.get(key, {})
    if review.get("overall_status") not in ("PASS", "PASS_WITH_LIMITATIONS"):
        continue
    for axis in ("composition", "subject_scale", "color_light", "type_layout", "information_density"):
        assert review.get("reference_fidelity", {}).get(axis, {}).get("status") in ("PASS", "PASS_WITH_LIMITATIONS"), (key, axis)
    if task.get("merged_reading_tasks"):
        coverage = review.get("merged_tasks_coverage", {})
        assert coverage.get("status") in ("PASS", "PASS_WITH_LIMITATIONS"), key
        reviewed = {r["id"] if isinstance(r, dict) else r for r in coverage.get("tasks", [])}
        assert {r["id"] for r in task["merged_reading_tasks"]} <= reviewed, key
    source = Path(review["image_path"])
    assert source.is_relative_to(batch), source
    fingerprint = hashlib.sha256(source.read_bytes()).hexdigest()
    assert fingerprint == review["sha256"], key
    with Image.open(source) as image:
        image.load()
        dimensions = list(image.size)
    target = batch / "final" / f"{key}.png"
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != fingerprint:
        shutil.copy2(source, target)
    assets.append({"id": key, "role": task["reading_task"], "reference_ids": task["reference_ids"],
                   "output": str(target), "generated_path": str(source), "sha256": fingerprint,
                   "actual_dimensions": dimensions, "qa_status": review["overall_status"],
                   "user_acceptance": "PENDING"})
    task.update(production_status="CURRENT_GEOMETRY_QA_PASS_WITH_LIMITATIONS", output=str(target),
                selected_sha256=fingerprint, actual_dimensions=dimensions, user_acceptance="PENDING")
(batch / "image-manifest.json").write_text(json.dumps({"route": {"actual_model": "UNKNOWN", "actual_effort": "UNKNOWN"}, "assets": assets}, ensure_ascii=False, indent=2) + "\n")
(batch / "reference-map.json").write_text(json.dumps(reference, ensure_ascii=False, indent=2) + "\n")
receipt_path = batch / "delivery-check.json"
receipt = json.loads(receipt_path.read_text())
receipt.update(selected_images=len(assets), required_images=len(reference["actual_execution_32"]),
               client_image_format="JPG_ONLY", native_sources_retained=True, format_conversion_is_generation=False,
               status="REBUILD_IN_PROGRESS", user_acceptance="PENDING")
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"selected": [r["id"] for r in assets], "count": len(assets)}, ensure_ascii=False))
