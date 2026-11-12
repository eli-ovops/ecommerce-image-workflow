"""Photo-guided AI candidate review; no claim of hard shape/pixel lock to real photos."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw


def typesetting_baseline(native, asset):
    baseline = native.convert("RGB")
    transform = asset.get("native_transform")
    if transform:
        scale = transform.get("uniform_scale")
        if not isinstance(scale, (int, float)) or not .5 <= scale <= 1:
            raise ValueError("Only bounded uniform downscaling on the same canvas is supported")
        new_size = tuple(round(d * scale) for d in native.size)
        baseline = Image.new("RGB", native.size, tuple(transform.get("background_rgb", [255,255,255])))
        xy = tuple((a-b)//2 for a,b in zip(native.size,new_size))
        baseline.paste(native.convert("RGB").resize(new_size, Image.Resampling.LANCZOS),xy)
    return baseline


def evaluate(manifest, root, stage="review"):
    root = Path(root).resolve()
    issues = []
    def reject(code, item, detail):
        issues.append({"code": code, "item": item, "detail": detail})
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def get_file(rec, label):
        if not isinstance(rec, dict) or not rec.get("path") or not rec.get("sha256"):
            reject("MISSING_FILE", label, "Current file/hash required")
            return None
        path = (root / rec["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            reject("INVALID_PATH", label, "Missing or outside project")
            return None
        if digest(path) != rec["sha256"]:
            reject("HASH_CHANGED", label, "Recorded source/output changed")
            return None
        return path
    def read(rec, label):
        p = get_file(rec, label)
        return json.loads(p.read_text()) if p else {}
    if manifest.get("production_state") != "EXPERIMENT_ENABLED":
        reject("PAUSED", "manifest", "Current revision is not enabled")
    if stage not in {"review", "delivery"}:
        reject("STAGE", "manifest", "Unknown gate stage")
    scopes = {
        "THREE_PHOTO_GUIDED_MAIN_IMAGES": {"R01", "R02", "R03"},
        "THREE_REFERENCE_LED_ADS": {"AD01", "AD02", "AD03"},
        "FIVE_PHOTO_GUIDED_DETAILS_AND_SKUS": {"R04", "R05", "R06", "K01", "K02"},
    }
    expected_ids = scopes.get(manifest.get("task_scope"))
    multi_sku = manifest.get("task_scope") == "FIVE_PHOTO_GUIDED_DETAILS_AND_SKUS"
    if expected_ids is None:
        reject("ASSET_SCOPE", "manifest", "Unsupported bounded image batch")
    if manifest.get("source_priority") != "OWN_SKU_PHOTOS_PRIMARY_3D_SECONDARY" or manifest.get("hard_shape_lock") is not False:
        reject("FALSE_CONTROL_CLAIM", "manifest", "Photo-guided generation cannot claim hard shape/pixel lock")
    catalog_records = manifest.get("source_catalogs", []) if multi_sku else [manifest.get("source_catalog")]
    catalog_rows, source_skus = {}, {}
    for index, catalog_record in enumerate(catalog_records):
        catalog = read(catalog_record, f"source_catalog:{index}")
        for row in catalog.get("files", []):
            if row["id"] in catalog_rows:
                reject("SOURCE_CATALOG", row["id"], "Duplicate source ID across catalogs")
            catalog_rows[row["id"]] = row
            color = catalog.get("sku_color")
            source_skus[row["id"]] = {"silver":"银色"}.get(color, color)
    if multi_sku and set(source_skus.values()) != {"银色", "黑色", "枪灰色"}:
        reject("SOURCE_CATALOG", "manifest", "Own-photo catalogs for all three SKU colors required")
    sources = {}
    for s in manifest.get("appearance_sources", []):
        sid = s.get("id")
        row = catalog_rows.get(sid, {})
        expected = {"path":row.get("project_path"), "sha256":row.get("sha256")}
        if s.get("file") != expected:
            reject("SOURCE_CATALOG", str(sid), "Appearance source must be an archived own-SKU photograph")
        get_file(s.get("file"), str(sid))
        sources[sid] = s.get("file", {})
    get_file(manifest.get("secondary_geometry_reference"), "secondary_3d_reference")
    assets = manifest.get("assets", [])
    if expected_ids is None or len(assets) != len(expected_ids) or {a.get("id") for a in assets} != expected_ids:
        reject("ASSET_SCOPE", "manifest", "Expected the distinct roles declared by this batch scope")
    jpgs = {}
    for asset in assets:
        aid = asset.get("id", "UNKNOWN")
        if asset.get("has_person") is not False or asset.get("has_water") is not False:
            reject("UNSUPPORTED_CONTENT", aid, "This dry, no-model revision has no water/person validation")
        ids = asset.get("appearance_source_ids", [])
        if len(ids) < 2 or any(s not in sources for s in ids):
            reject("LINEAGE", aid, "Own-SKU appearance photographs must be explicitly referenced")
        if multi_sku:
            expected_sku = {"R04":"银色", "R05":"银色", "R06":"银色", "K01":"黑色", "K02":"枪灰色"}.get(aid)
            if asset.get("sku") != expected_sku or any(source_skus.get(s) != expected_sku for s in ids):
                reject("SKU_SOURCE", aid, "This role must use photographs of its own SKU color")
            if not asset.get("style_references"):
                reject("STYLE_REFERENCE", aid, "An actual related visual reference is required")
        for ref in asset.get("style_references", []):
            get_file(ref, aid+":style_reference")
        prompt = get_file(asset.get("prompt"), aid+":prompt")
        native = get_file(asset.get("generated_native"), aid+":native")
        candidate = get_file(asset.get("candidate"), aid+":candidate")
        jpg = get_file(asset.get("client_jpg"), aid+":jpg")
        generation = read(asset.get("generation_receipt"), aid+":generation_receipt")
        source_hashes = sorted({sources[s].get("sha256") for s in ids if s in sources})
        if (not native or generation.get("native_sha256") != digest(native)
                or not prompt or generation.get("prompt_sha256") != digest(prompt)
                or generation.get("appearance_source_sha256") != source_hashes
                or generation.get("tool") != "builtin_image_gen"):
            reject("GENERATION_LINEAGE", aid, "Actual generated file, prompt and real-photo references must be bound")
        if native and candidate:
            with Image.open(native) as ni, Image.open(candidate) as ci:
                working_native = ni
                repair = asset.get("local_repair")
                if repair:
                    repaired = get_file(repair.get("file"), aid+":local_repair")
                    repair_mask = get_file(repair.get("mask"), aid+":local_repair_mask")
                    get_file(repair.get("tool_patch"), aid+":local_repair_tool_patch")
                    get_file(repair.get("evidence"), aid+":local_repair_evidence")
                    if repair.get("base_sha256") != digest(native) or repair.get("tool") != "builtin_image_gen":
                        reject("LOCAL_REPAIR_LINEAGE", aid, "Repair must bind frozen base and actual tool-generated patch")
                    if repaired and repair_mask:
                        with Image.open(repaired) as ri, Image.open(repair_mask) as mi:
                            if ri.size != ni.size or mi.size != ni.size:
                                raise ValueError("Local repair canvas changed")
                            changed_scope = mi.convert("L").point(lambda a:255 if a>0 else 0)
                            covered = changed_scope.histogram()[255]
                            if not 0 < covered <= ni.width*ni.height*.01:
                                reject("LOCAL_REPAIR_SCOPE", aid, "Repair patch must remain a tiny explicitly recorded region")
                            outside = ImageChops.invert(changed_scope)
                            delta = ImageChops.difference(ni.convert("RGB"),ri.convert("RGB"))
                            if any(ImageChops.multiply(ch,outside).getextrema()[1] for ch in delta.split()):
                                reject("LOCAL_REPAIR_OUTSIDE_CHANGED", aid, "Pixels outside small repair mask changed")
                            working_native = ri.convert("RGB").copy()
                if ni.size != ci.size or ci.format not in {"PNG","TIFF"}:
                    reject("TYPESETTING_SCOPE", aid, "Keep native canvas and lossless working output")
                else:
                    protected = Image.new("L", ni.size, 255)
                    draw = ImageDraw.Draw(protected)
                    for box in asset.get("text_edit_regions", []):
                        if len(box) != 4 or not (0 <= box[0] <= box[2] < ni.width and 0 <= box[1] <= box[3] < ni.height):
                            raise ValueError("Invalid text edit rectangle")
                        draw.rectangle(box, fill=0)
                    if protected.histogram()[255] < ni.width * ni.height * .75:
                        reject("TYPESETTING_SCOPE", aid, "Text edits cannot exempt most of the product image")
                    diff = ImageChops.difference(typesetting_baseline(working_native, asset), ci.convert("RGB"))
                    if any(ImageChops.multiply(ch, protected).getextrema()[1] for ch in diff.split()):
                        reject("POST_GENERATION_CHANGE", aid, "Pixels outside declared text areas changed")
        review = read(asset.get("review"), aid+":review")
        required = ["photo_appearance","geometry","reference_style","copy","no_model","export"]
        if (not candidate or not jpg or review.get("candidate_sha256") != digest(candidate)
                or review.get("jpg_sha256") != digest(jpg) or review.get("appearance_source_sha256") != source_hashes
                or review.get("status") != "PASS" or not review.get("reviewer") or not review.get("finding")
                or not review.get("reviewed_at") or not all(review.get("checks", {}).get(k)=="PASS" for k in required)):
            reject("VISUAL_REVIEW", aid, "Actual photo/geometry/style/copy/no-model/export review required")
        if jpg:
            with Image.open(jpg) as ji:
                ji.load()
                if ji.format != "JPEG":
                    reject("JPG_FORMAT", aid, "User output must be JPEG")
                if native:
                    with Image.open(native) as ni:
                        if ji.size != ni.size:reject("JPG_SIZE", aid, "Native canvas changed")
            jpgs[aid] = digest(jpg)
    if len(set(jpgs.values())) != len(jpgs):
        reject("DUPLICATE_OUTPUT", "manifest", "Distinct image roles must not reuse one output")
    if stage == "delivery":
        acceptance = read(manifest.get("client_acceptance"), "client_acceptance")
        if acceptance.get("status") != "ACCEPTED" or acceptance.get("accepted_jpg_sha256") != jpgs:
            reject("CUSTOMER_ACCEPTANCE", "manifest", "Customer acceptance of current final images is absent")
        get_file(acceptance.get("receipt"), "customer_receipt")
    return {"stage":stage, "status":"PASS" if not issues else "REJECTED", "issues":issues,
            "limitations":"Manual real-photo and secondary-3D comparison. No hard shape lock, source-photo pixel identity, automatic physical IoU, flow or skin check. Typesetting comparison only protects generated native pixels outside text areas."}
