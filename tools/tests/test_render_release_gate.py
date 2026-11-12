"""Synthetic software rejection cases; never product/model acceptance evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

SPEC = importlib.util.spec_from_file_location("render_gate", Path(__file__).parents[1] / "render_release_gate.py")
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


class RenderGateRegression(unittest.TestCase):
    def record(self, name):
        return {"path": name, "sha256": G.digest(self.root / name)}

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data))
        return self.record(name)

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="render-gate-test-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "model.blend").write_bytes(b"SYNTHETIC SOFTWARE FIXTURE ONLY")
        model = self.record("model.blend")
        layer = Image.new("RGBA", (8, 8))
        layer.paste((80, 90, 100, 255), (2, 2, 6, 6))
        layer.save(self.root / "layer.png")
        layer_record = self.record("layer.png")
        raw = self.write("raw.json", {"synthetic": True})
        origin = self.write("origin.json", {"source_model_sha256": model["sha256"],
            "body_geometry_unchanged": True, "raw_evidence": raw, "render_sha256": [layer_record["sha256"]]})
        authorization = self.write("authorization.json", {"model_sha256": model["sha256"],
            "user_quote": "SYNTHETIC TEST AUTHORIZATION, NOT REAL USER ACCEPTANCE"})
        self.m = {"schema_version": 2, "experiment_id": "TEST-ONLY", "production_state": "EXPERIMENT_ENABLED",
            "task_scope": "THREE_DRY_MODEL_MAIN_IMAGES", "geometry_source": {"file": model,
                "authorization": authorization, "render_receipt": origin}, "appearance_sources": [raw], "assets": []}
        for i in range(1, 4):
            key = f"P0{i}"
            layers = [{"file": layer_record, "xy": [2, 2], "size": [4, 4]}]
            expected = G.place_layers((8, 8), layers, lambda rec, _: self.root / rec["path"])
            canvas = Image.new("RGBA", (8, 8), (i * 30, 0, 0, 255))
            canvas.alpha_composite(expected)
            canvas.save(self.root / f"{key}.png")
            canvas.convert("RGB").save(self.root / f"{key}.jpg")
            expected.getchannel("A").point(lambda a: 255 if a == 255 else 0).save(self.root / f"{key}-mask.png")
            candidate = self.record(f"{key}.png")
            jpg = self.record(f"{key}.jpg")
            review = self.write(f"{key}-review.json", {"status": "PASS", "candidate_sha256": candidate["sha256"],
                "model_sha256": model["sha256"], "jpg_sha256": jpg["sha256"], "reviewer": "synthetic-reviewer",
                "reviewed_at": "TEST-ONLY", "finding": "SYNTHETIC SOFTWARE CONTROL ONLY",
                "checks": {k: "PASS" for k in ["geometry", "style", "copy", "export"]}})
            self.m["assets"].append({"id": key, "has_water": False, "has_person": False,
                "product_layers": layers, "candidate": candidate, "client_jpg": jpg,
                "protected_mask": self.record(f"{key}-mask.png"), "review": review})

    def codes(self, stage="review"):
        return {x["code"] for x in G.evaluate(self.m, self.root, stage)["issues"]}

    def test_valid_control_only_passes_review(self):
        self.assertEqual(self.codes(), set())

    def test_changed_frozen_model_is_rejected(self):
        (self.root / "model.blend").write_bytes(b"CHANGED")
        self.assertIn("HASH_CHANGED", self.codes())

    def test_shrunk_mask_cannot_hide_product_change(self):
        mask = Image.new("L", (8, 8))
        mask.putpixel((2, 2), 255)
        mask.save(self.root / "P01-mask.png")
        self.m["assets"][0]["protected_mask"] = self.record("P01-mask.png")
        self.assertIn("MASK_SCOPE", self.codes())

    def test_repainted_product_pixels_are_rejected(self):
        p = self.root / "P01.png"
        with Image.open(p) as im:
            im.putpixel((3, 3), (255, 0, 0, 255))
            im.save(p)
        self.m["assets"][0]["candidate"] = self.record("P01.png")
        self.assertIn("PRODUCT_CHANGED", self.codes())

    def test_water_cannot_bypass_unimplemented_checks(self):
        self.m["assets"][1]["has_water"] = True
        self.assertIn("UNSUPPORTED_CONTENT", self.codes())

    def test_review_cannot_claim_customer_acceptance(self):
        self.assertIn("CUSTOMER_ACCEPTANCE", self.codes("delivery"))
