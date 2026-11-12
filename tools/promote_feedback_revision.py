"""Promote only the approved feedback revisions; retain prior selected bytes."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

project = Path(__file__).resolve().parents[1]
batch = next(p for p in (project / "production").iterdir()
             if (p / "revision-20261023-user-feedback").is_dir())
revision = batch / "revision-20261023-user-feedback"
read = lambda p: json.loads(p.read_text())
assert read(batch / "delivery-check.json").get("status") != "REBUILD_REQUIRED_CLIENT_GEOMETRY_FEEDBACK", "Client geometry rejection supersedes this old revision; do not promote it."
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(revision / "revision-plan.json")
selected_doc = read(revision / "selected-manifest.json")
selected_rows = selected_doc if isinstance(selected_doc, list) else selected_doc["assets"]
selected = {row["id"]: row for row in selected_rows}
assert len(selected) == len(selected_rows) == 17
assert set(selected) == set(plan["execution_ids"])
reviews = {row["id"]: row for row in read(revision / "qa-review.json")["reviews"]}
accepted = ("PASS", "PASS_WITH_LIMITATIONS")
for key, row in selected.items():
    candidate = Path(row["selected_candidate"])
    if not candidate.is_absolute():
        candidate = revision / candidate
    review = reviews[key]
    assert review["overall_status"] in accepted, key
    assert sha(candidate) == row["sha256"] == review["sha256"], key
    for axis in ("composition", "subject_scale", "color_light", "type_layout", "information_density"):
        assert review["reference_fidelity"][axis]["status"] in accepted, (key, axis)
    if key in plan["fresh_portraits"]:
        assert row["fresh_generation"] is True, key
    assert Path(row["prompt"]).is_file(), key

manifest = read(batch / "image-manifest.json")
old_assets = {row["id"]: row for row in manifest["assets"]}
baseline = {row["id"]: row for row in read(revision / "before/image-manifest.json")["assets"]}
for key in set(old_assets) - set(selected):
    assert sha(batch / "final" / (key + ".png")) == baseline[key]["sha256"], key

qa = read(batch / "qa-review.json")
mapping = read(batch / "reference-map.json")
for key, row in selected.items():
    destination = batch / "final" / (key + ".png")
    old = revision / "before/final" / destination.name
    old.parent.mkdir(parents=True, exist_ok=True)
    if not old.exists():
        assert sha(destination) == baseline[key]["sha256"], key
        shutil.copy2(destination, old)
    assert sha(old) == baseline[key]["sha256"], key
    source = Path(row["selected_candidate"])
    if not source.is_absolute():
        source = revision / source
    shutil.copy2(source, destination)
    asset = old_assets[key]
    for field in ("prompt", "source_images", "reference_ids", "actual_dimensions", "tool_references", "generation_method"):
        if field in row:
            asset[field] = row[field]
    asset.update(output=str(destination), selected_candidate=str(source), generated_path=str(source),
                 sha256=row["sha256"], qa_status=reviews[key]["overall_status"],
                 user_acceptance="PENDING", revision_batch=revision.name,
                 fresh_generation=row.get("fresh_generation", False))
    review = copy.deepcopy(reviews[key])
    review.update(image_path=str(destination), candidate_only=False,
                  selected_candidate=str(source), revision_batch=revision.name)
    qa["reviews"].append(review)
    for task in mapping["actual_execution_32"]:
        if task["id"] == key:
            task.update(selected_sha256=row["sha256"], actual_dimensions=row["actual_dimensions"],
                        output=str(destination), user_acceptance="PENDING",
                        production_status="FEEDBACK_REVISION_VISUAL_QA_PASSED")

latest = {row["id"]: row for row in qa["reviews"]}
qa["latest_status_by_id"] = {key: latest[key]["overall_status"] for key in old_assets}
qa["batch_closeout"] = {
    "status": "PASS_WITH_LIMITATIONS",
    "reviewed_final_count": len(old_assets),
    "same_sha_final_count": len(old_assets),
    "planned_id_count": len(old_assets),
    "revision_batch": revision.name,
    "revised_count": len(selected),
    "unchanged_prior_qa_reused_count": len(old_assets) - len(selected),
    "final_receipts": [{
        "id": key,
        "sha256": asset["sha256"],
        "latest_revision": latest[key].get("revision", "UNKNOWN"),
        "final_path": str(batch / "final" / (key + ".png")),
    } for key, asset in old_assets.items()],
    "method": "17 newly selected images passed current independent visual QA; 15 unchanged images retain prior same-byte QA. Prior closeout retained in revision/before/qa-review.json.",
    "user_acceptance": "PENDING",
    "root_acceptance": "PENDING",
}
mapping["execution_status"] = "FEEDBACK_REVISION_VISUAL_QA_PASSED_ROOT_REVIEW_PENDING"
mapping["feedback_revision"] = {
    "batch": revision.name,
    "revised_ids": sorted(selected),
    "unchanged_count": len(old_assets) - len(selected),
    "reference_inventory_and_original_mapping": "RETAINED",
    "user_acceptance": "PENDING",
}

write(batch / "image-manifest.json", manifest)
write(batch / "qa-review.json", qa)
write(batch / "reference-map.json", mapping)
print(json.dumps({"promoted": sorted(selected), "unchanged": 15, "user_acceptance": "PENDING"}))
