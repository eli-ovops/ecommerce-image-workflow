"""Fail-closed pilot checks. No generation, export, packaging, or external sends."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_scope_sha256(asset):
    keys = ["id", "role", "producer", "geometry_route", "geometry_source_ids", "has_water",
            "has_person", "local_repairs", "candidate", "protected_baseline", "protected_mask"]
    return hashlib.sha256(json.dumps({k: asset.get(k) for k in keys}, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def evaluate(manifest, root, stage="review"):
    if manifest.get("schema_version") in {2, 3, 4}:
        import importlib.util
        gate_name = {2:"render_release_gate", 3:"photo_guided_gate", 4:"suite_release_gate"}[manifest["schema_version"]]
        spec = importlib.util.spec_from_file_location(gate_name, Path(__file__).with_name(gate_name + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.evaluate(manifest, root, stage)
    root = Path(root).resolve()
    issues = []

    def reject(code, item, detail):
        issues.append({"code": code, "item": item, "detail": detail})

    def file_record(record, item):
        if not isinstance(record, dict) or not record.get("path") or not record.get("sha256"):
            reject("MISSING_FILE", item, "Required path and sha256 are absent")
            return None
        path = (root / record["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            reject("INVALID_PATH", item, "File missing or outside project")
            return None
        if digest(path) != record["sha256"]:
            reject("HASH_CHANGED", item, "Current file differs from recorded evidence")
            return None
        return path

    def load_evidence(record, item):
        path = file_record(record, item)
        if path is None:
            return None
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict):
                raise ValueError("Evidence must be an object")
            return data
        except (ValueError, OSError) as exc:
            reject("INVALID_EVIDENCE", item, str(exc))
            return None

    if manifest.get("schema_version") != 1:
        reject("SCHEMA", "manifest", "Expected explicit schema_version 1")
    if manifest.get("production_state") != "EXPERIMENT_ENABLED":
        reject("PAUSED", "manifest", "Image work remains paused or state is unknown")
    if stage not in {"review", "delivery"}:
        reject("STAGE", "manifest", "Unsupported gate stage")

    catalog = load_evidence(manifest.get("source_catalog"), "source_catalog")
    catalog_rows = {}
    if catalog is not None:
        if manifest["source_catalog"]["path"] != "products/主推花洒/银色/manifest.json" or catalog.get("asset_kind") != "real_product_photos":
            reject("SOURCE_CATALOG", "manifest", "Expected archived own-SKU photo catalog")
        catalog_rows = {row["id"]: row for row in catalog.get("files", [])}
    sources = {}
    for source in manifest.get("sources", []):
        key = source.get("id")
        if not key or key in sources:
            reject("SOURCE_ID", str(key), "Missing or duplicate source id")
            continue
        sources[key] = source
        if source.get("kind") != "real_photo" or source.get("sku") != "silver":
            reject("UNSUPPORTED_SOURCE", key, "v0.1 permits own silver real photos only")
        file_record(source.get("file"), key)
        archived = catalog_rows.get(key, {})
        if source.get("file") != {"path": archived.get("project_path"), "sha256": archived.get("sha256")}:
            reject("SOURCE_CATALOG", key, "Source not identical to archived real-photo entry")
    if not sources:
        reject("NO_SOURCES", "manifest", "No real geometry sources registered")

    assets = manifest.get("assets", [])
    ids = [a.get("id") for a in assets]
    if len(ids) != 3 or set(ids) != {"E01", "E02", "E03"}:
        reject("ASSET_SCOPE", "manifest", "Pilot requires exactly E01/E02/E03")
    used_source_hashes = set()
    baseline_hashes, mask_hashes, candidate_hashes, jpg_hashes = set(), set(), set(), set()
    checked = []
    for asset in assets:
        key = asset.get("id", "UNKNOWN")
        source_ids = asset.get("geometry_source_ids", [])
        if not source_ids or any(s not in sources for s in source_ids):
            reject("LINEAGE", key, "Real geometry source ids missing or unresolved")
        hashes = sorted({sources[s]["file"]["sha256"] for s in source_ids if s in sources})
        used_source_hashes.update(hashes)
        if asset.get("geometry_route") != "photo_locked":
            reject("UNIMPLEMENTED_ROUTE", key, "3D/generated geometry route not implemented in v0.1")
        producer = asset.get("producer")
        if not producer:
            reject("PRODUCER", key, "Actual producer is required")
        for flag in ["has_water", "has_person"]:
            if type(asset.get(flag)) is not bool:
                reject("APPLICABILITY", key, flag + " must be explicitly true or false")
        if asset.get("has_water") != (key == "E02") or asset.get("has_person") != (key == "E03"):
            reject("TASK_APPLICABILITY", key, "Pilot task requirements cannot be disabled by flags")
        repairs = asset.get("local_repairs")
        if type(repairs) is not int or not 0 <= repairs <= 2:
            reject("REPAIR_BUDGET", key, "Local repair count unknown or exceeds two")

        candidate = file_record(asset.get("candidate"), key + ":candidate")
        baseline = file_record(asset.get("protected_baseline"), key + ":baseline")
        mask_path = file_record(asset.get("protected_mask"), key + ":mask")
        if baseline:
            baseline_hashes.add(digest(baseline))
        if mask_path:
            mask_hashes.add(digest(mask_path))
        if candidate:
            if digest(candidate) in candidate_hashes:
                reject("DUPLICATE_OUTPUT", key, "One image cannot stand in for multiple pilot tasks")
            candidate_hashes.add(digest(candidate))
        protected_pixels = None
        if candidate and baseline and mask_path:
            try:
                with Image.open(candidate) as ci, Image.open(baseline) as bi, Image.open(mask_path) as mi:
                    if ci.format not in {"PNG", "TIFF"} or bi.format not in {"PNG", "TIFF"}:
                        raise ValueError("Protection proof requires lossless working sources")
                    if not ci.size == bi.size == mi.size:
                        raise ValueError("Candidate, baseline, and mask must share canvas")
                    mask = mi.convert("L")
                    values = set(mask.getdata())
                    if not values <= {0, 255} or 255 not in values:
                        raise ValueError("Protection mask must be binary and nonempty")
                    protected_pixels = mask.histogram()[255]
                    delta = ImageChops.difference(ci.convert("RGBA"), bi.convert("RGBA"))
                    if any(channel.getextrema()[1] for channel in [ImageChops.multiply(c, mask) for c in delta.split()]):
                        reject("PRODUCT_CHANGED", key, "Protected product pixels changed")
            except (ValueError, OSError) as exc:
                reject("PIXEL_PROOF", key, str(exc))

        required = ["geometry", "mask_scope", "reference_style", "copy"]
        if asset.get("has_water") is True:
            required.append("water")
        if asset.get("has_person") is True:
            required.append("person")
        if candidate:
            for check in required:
                evidence = load_evidence(asset.get("checks", {}).get(check), key + ":" + check)
                if evidence is None:
                    continue
                if evidence.get("status") != "PASS":
                    reject("CHECK_NOT_PASS", key + ":" + check, "Only explicit PASS can proceed")
                if (evidence.get("experiment_id") != manifest.get("experiment_id")
                        or not manifest.get("experiment_id") or evidence.get("check_type") != check
                        or evidence.get("asset_scope_sha256") != asset_scope_sha256(asset)):
                    reject("REVIEW_SCOPE", key + ":" + check, "Review attached to wrong experiment, check or task configuration")
                if evidence.get("subject_sha256") != digest(candidate) or evidence.get("source_sha256") != hashes:
                    reject("STALE_REVIEW", key + ":" + check, "Review not bound to current candidate and sources")
                if (not baseline or not mask_path or evidence.get("protected_baseline_sha256") != digest(baseline)
                        or evidence.get("protected_mask_sha256") != digest(mask_path)
                        or evidence.get("asset_id") != key):
                    reject("STALE_PROTECTION_REVIEW", key + ":" + check, "Review not bound to current baseline, protection mask and task")
                if not evidence.get("reviewer") or evidence.get("reviewer") == producer:
                    reject("INDEPENDENCE", key + ":" + check, "Named independent reviewer required")
                if not evidence.get("reviewed_at") or not evidence.get("finding"):
                    reject("EMPTY_REVIEW", key + ":" + check, "Actual date and finding required")

        jpg = file_record(asset.get("client_jpg"), key + ":jpg")
        if jpg:
            if digest(jpg) in jpg_hashes:
                reject("DUPLICATE_OUTPUT", key, "Duplicate client JPG across tasks")
            jpg_hashes.add(digest(jpg))
            try:
                with Image.open(jpg) as im:
                    im.load()
                    if im.format != "JPEG" or jpg.suffix.lower() not in {".jpg", ".jpeg"}:
                        raise ValueError("Client output must actually be JPEG")
                    if candidate:
                        with Image.open(candidate) as ci:
                            if ci.size != im.size:
                                raise ValueError("JPG dimensions differ from selected source")
            except (ValueError, OSError) as exc:
                reject("JPG_FORMAT", key, str(exc))
            export = load_evidence(asset.get("export_review"), key + ":export")
            if export is not None and (export.get("status") != "PASS" or export.get("subject_sha256") != digest(jpg)
                           or not candidate or export.get("native_sha256") != digest(candidate)
                           or export.get("reviewer") == producer or export.get("asset_id") != key
                           or export.get("experiment_id") != manifest.get("experiment_id")
                           or export.get("check_type") != "export"
                           or not all(export.get(f) for f in ["reviewer", "reviewed_at", "finding"])):
                reject("EXPORT_REVIEW", key, "Export needs current JPG/native hashes and actual visual review")
        checked.append({"id": key, "protected_pixels": protected_pixels})

    if stage == "delivery":
        acceptance = load_evidence(manifest.get("baseline_acceptance"), "baseline_acceptance")
        if acceptance is not None:
            e01 = next((a for a in assets if a.get("id") == "E01"), {})
            expected_jpgs = {a.get("id"): (a.get("client_jpg") or {}).get("sha256") for a in assets}
            if acceptance.get("status") != "ACCEPTED" or acceptance.get("source_sha256") != sorted(used_source_hashes):
                reject("CUSTOMER_ACCEPTANCE", "manifest", "Current geometry baseline not accepted")
            if (acceptance.get("experiment_id") != manifest.get("experiment_id") or not manifest.get("experiment_id")
                    or acceptance.get("baseline_sha256") != sorted(baseline_hashes)
                    or acceptance.get("mask_sha256") != sorted(mask_hashes)
                    or acceptance.get("geometry_candidate_sha256") != (e01.get("candidate") or {}).get("sha256")
                    or acceptance.get("accepted_jpg_sha256") != expected_jpgs):
                reject("STALE_CUSTOMER_ACCEPTANCE", "manifest", "Customer acceptance not bound to current experiment/product baselines/masks")
            if not acceptance.get("reviewed_at") or not acceptance.get("finding"):
                reject("CUSTOMER_ACCEPTANCE", "manifest", "Actual acceptance record missing")
            file_record(acceptance.get("receipt"), "customer_receipt")

    return {"stage": stage, "status": "PASS" if not issues else "REJECTED", "issues": issues,
            "assets": checked, "limitations": "Mechanical evidence and pixel checks only; not automatic visual or customer acceptance"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=["review", "delivery"], default="review")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        report = evaluate(json.loads(args.manifest.read_text()), root, args.stage)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report = {"status": "REJECTED", "issues": [{"code": "INVALID_MANIFEST", "detail": str(exc)}]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
