"""Select an independently approved candidate without touching the original32."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
from PIL import Image

project = Path(__file__).resolve().parents[1]
revision = next(p / "revision-20261023-user-feedback"
                for p in (project / "production").iterdir()
                if (p / "revision-20261023-user-feedback").is_dir())
call_id = sys.argv[1]
key = call_id.split("-")[0]
candidate = revision / (call_id + ".png")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = sha(candidate)
reviews = json.loads((revision / "qa-review.json").read_text())["reviews"]
review = next(x for x in reversed(reviews) if x["id"] == key)
assert review["sha256"] == digest
assert review["overall_status"] in ("PASS", "PASS_WITH_LIMITATIONS")
records = [json.loads(line) for line in (revision / "generation-review.jsonl").read_text().splitlines()]
preflight = next(x for x in reversed(records) if x.get("call_id") == call_id
                 and any(k in x for k in ("refs", "references_passed", "tool_references")))
references = next(preflight[k] for k in ("refs", "references_passed", "tool_references") if k in preflight)
plan = json.loads((revision / "revision-plan.json").read_text())
fresh = key in plan["fresh_portraits"]
if fresh:
    assert preflight.get("fresh") is True or preflight.get("fresh_generation") is True
prompt = revision / (call_id + "-prompt.txt")
assert prompt.is_file()
destination = revision / "final" / (key + ".png")
assert not destination.exists() or sha(destination) == digest
shutil.copy2(candidate, destination)
row = {"id": key, "selected_candidate": str(destination), "sha256": digest,
       "actual_dimensions": list(Image.open(destination).size), "prompt": str(prompt),
       "tool_references": references, "fresh_generation": fresh,
       "reference_ids": preflight.get("reference_ids", []), "qa_status": review["overall_status"]}
if "generation_method" in preflight:
    row["generation_method"] = preflight["generation_method"]
if not row["reference_ids"]:
    mapping = json.loads((revision.parent / "reference-map.json").read_text())
    task = next(x for x in mapping["actual_execution_32"] if x["id"] == key)
    row["reference_ids"] = task["reference_ids"]
path = revision / "selected-manifest.json"
selected = [x for x in json.loads(path.read_text()) if x["id"] != key] + [row]
path.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"selected": key, "sha256": digest, "count": len(selected)}))
