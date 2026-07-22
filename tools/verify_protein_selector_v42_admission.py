#!/usr/bin/env python3
"""Verify V42 source binding and complete-frontier admission."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_selector_v42_admission():
    receipt=json.loads((ROOT/"verify/protein_selector_v42_admission_v1.json").read_text())
    for relative,value in receipt["source_sha256"].items():
        if sha(ROOT/relative)!=value: raise RuntimeError(f"V42 source drift: {relative}")
    if receipt["complete_frontier"]["masks"]!=[2178,5814,5815]: raise RuntimeError("V42 frontier registration drifted")
    return {"schema":"fold-protein-selector-v42-admission-verification/v1","status":"verified","cube_candidates":8192,"connected_frontier_count":3,"masks":[2178,5814,5815]}
if __name__=="__main__": print(json.dumps(verify_selector_v42_admission(),sort_keys=True))
