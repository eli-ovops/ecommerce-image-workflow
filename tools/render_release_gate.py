"""Narrow review gate for the user-authorized three dry model-render main images.

Checks lineage and unchanged composited product pixels, not physical shape accuracy.
The original photo/water/portrait pilot remains a separate schema-1 experiment.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def place_layers(size, layers, get_file):
    canvas = Image.new("RGBA", size)
    for layer in layers:
        p = get_file(layer.get("file"), "render_layer")
        if p is None:
            continue
        with Image.open(p) as im:
            if im.mode != "RGBA":
                raise ValueError("Product layer must retain rendered alpha")
            alpha = im.getchannel("A")
            bbox = alpha.getbbox()
            if bbox is None or alpha.getextrema()[0] != 0:
                raise ValueError("Expected nonempty isolated product render")
            cropped = im.crop(bbox)
            target = tuple(layer["size"])
            if len(target) != 2 or min(target) <= 0:
                raise ValueError("Invalid placement dimensions")
            # Preserve the render's aspect; integer rounding is the only tolerance.
            if abs(target[0] / target[1] - cropped.width / cropped.height) > 2 / min(target):
                raise ValueError("Product render stretched")
            cropped = cropped.resize(target, Image.Resampling.LANCZOS)
            canvas.alpha_composite(cropped, tuple(layer["xy"]))
    return canvas


def evaluate(manifest, root, stage="review"):
    root = Path(root).resolve()
    issues = []
    checked = []
    def reject(code, item, detail):
        issues.append({"code": code, "item": item, "detail": detail})
    def get_file(rec, label):
        if not isinstance(rec, dict) or not rec.get("path") or not rec.get("sha256"):
            reject("MISSING_FILE", label, "Path and current hash required")
            return None
        p = (root / rec["path"]).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            reject("INVALID_PATH", label, "File missing or outside project")
            return None
        if digest(p) != rec["sha256"]:
            reject("HASH_CHANGED", label, "File differs from recorded hash")
            return None
        return p
    def read_json(rec, label):
        p = get_file(rec, label)
        return json.loads(p.read_text()) if p else {}
    if manifest.get("production_state") != "EXPERIMENT_ENABLED":
        reject("PAUSED", "manifest", "Explicit resumed state required")
    if stage not in {"review", "delivery"}:
        reject("STAGE", "manifest", "Unsupported stage")
    if manifest.get("task_scope") != "THREE_DRY_MODEL_MAIN_IMAGES":
        reject("ASSET_SCOPE", "manifest", "Only the explicitly simplified three-image trial is supported")
    geo = manifest.get("geometry_source", {})
    model = get_file(geo.get("file"), "geometry_source")
    approval = read_json(geo.get("authorization"), "model_authorization")
    origin = read_json(geo.get("render_receipt"), "render_origin")
    model_hash = digest(model) if model else None
    if not model_hash or approval.get("model_sha256") != model_hash or not approval.get("user_quote"):
        reject("MODEL_AUTHORIZATION", "manifest", "Current model must be bound to actual user instruction")
    if origin.get("source_model_sha256") != model_hash or origin.get("body_geometry_unchanged") is not True:
        reject("MODEL_CHANGED", "manifest", "Render source must preserve approved body mesh")
    get_file(origin.get("raw_evidence"), "geometry_readback_evidence")
    source_hashes = []
    for source in manifest.get("appearance_sources", []):
        p = get_file(source, "appearance_source")
        if p:
            source_hashes.append(digest(p))
    if not source_hashes:
        reject("NO_SOURCES", "manifest", "Own-SKU appearance sources required")
    assets = manifest.get("assets", [])
    if len(assets) != 3 or {a.get("id") for a in assets} != {"P01", "P02", "P03"}:
        reject("ASSET_SCOPE", "manifest", "Expected three distinct dry-image roles")
    jpg_hashes = {}
    for asset in assets:
        key = asset.get("id", "UNKNOWN")
        if asset.get("has_water") is not False or asset.get("has_person") is not False:
            reject("UNSUPPORTED_CONTENT", key, "Water/person routes require their own implemented checks")
        candidate = get_file(asset.get("candidate"), key + ":candidate")
        mask_path = get_file(asset.get("protected_mask"), key + ":mask")
        jpg = get_file(asset.get("client_jpg"), key + ":jpg")
        if candidate and mask_path:
            with Image.open(candidate) as ci, Image.open(mask_path) as mi:
                if ci.format not in {"PNG", "TIFF"}:
                    raise ValueError("Lossless candidate required for pixel protection")
                layers = asset.get("product_layers", [])
                if not layers:
                    reject("NO_PRODUCT_LAYER", key, "Actual render layer required")
                expected = place_layers(ci.size, layers, get_file)
                expected_mask = expected.getchannel("A").point(lambda p: 255 if p == 255 else 0)
                if not expected_mask.getbbox() or mi.size != ci.size or ImageChops.difference(expected_mask, mi.convert("L")).getbbox():
                    reject("MASK_SCOPE", key, "Protection must cover all opaque rendered product pixels")
                delta = ImageChops.difference(ci.convert("RGB"), expected.convert("RGB"))
                if any(ImageChops.multiply(c, expected_mask).getextrema()[1] for c in delta.split()):
                    reject("PRODUCT_CHANGED", key, "Product pixels altered after rendering")
                for layer in layers:
                    if (layer.get("file") or {}).get("sha256") not in origin.get("render_sha256", []):
                        reject("RENDER_LINEAGE", key, "Layer absent from actual render receipt")
            review = read_json(asset.get("review"), key + ":visual_review")
            if (review.get("status") != "PASS" or review.get("candidate_sha256") != digest(candidate)
                    or review.get("model_sha256") != model_hash or not review.get("reviewer")
                    or not review.get("reviewed_at") or not review.get("finding")
                    or not all(review.get("checks", {}).get(k) == "PASS" for k in ["geometry", "style", "copy", "export"])):
                reject("VISUAL_REVIEW", key, "Actual geometry/style/copy/export review bound to candidate required")
            if jpg:
                with Image.open(jpg) as ji, Image.open(candidate) as ci:
                    ji.load()
                    if ji.format != "JPEG" or ji.size != ci.size:
                        reject("JPG_FORMAT", key, "Current same-size JPEG required")
                    if review.get("jpg_sha256") != digest(jpg):
                        reject("STALE_EXPORT_REVIEW", key, "Review must bind exported JPEG")
        if jpg:
            jpg_hashes[key] = digest(jpg)
        checked.append({"id": key})
    if len(set(jpg_hashes.values())) != len(jpg_hashes):
        reject("DUPLICATE_OUTPUT", "manifest", "Distinct image roles must not reuse identical output")
    if stage == "delivery":
        acceptance = read_json(manifest.get("client_acceptance"), "client_acceptance")
        if acceptance.get("status") != "ACCEPTED" or acceptance.get("accepted_jpg_sha256") != jpg_hashes:
            reject("CUSTOMER_ACCEPTANCE", "manifest", "Current final JPGs have no customer acceptance")
        get_file(acceptance.get("receipt"), "customer_receipt")
    return {"stage": stage, "status": "PASS" if not issues else "REJECTED", "issues": issues, "assets": checked,
            "limitations": "Model/render lineage and protected pixels only. Manual visual review; no automatic physical-fit, flow or skin test. User model authorization is not customer acceptance."}
