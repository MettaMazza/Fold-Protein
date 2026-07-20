#!/usr/bin/env python3
"""Verify and evaluate sealed branch-reconciliation selector V27."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from calculate_tm import compute_tm, parse_ca  # noqa: E402

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(manifest_path, sealed_dir):
    manifest_path,sealed_dir=Path(manifest_path).resolve(),Path(sealed_dir).resolve();manifest=json.loads(manifest_path.read_text());seal=json.loads((sealed_dir/"seal.json").read_text())
    if manifest.get("schema") != "fold-protein-blind-selector/v27" or seal.get("schema") != "fold-protein-blind-seal/v27": raise RuntimeError("invalid V27 seal; target access forbidden")
    for field,path in {"protocol_manifest_sha256":manifest_path,"selector_input_sha256":sealed_dir/"selector_input.json","selected_states_sha256":sealed_dir/"selected_states.json","prediction_pdb_sha256":sealed_dir/"prediction.pdb"}.items():
        if seal.get(field) != sha(path): raise RuntimeError(f"V27 seal mismatch: {field}")
    states=json.loads((sealed_dir/"selected_states.json").read_text());binding=manifest["parent_records"][seal["v25_run_id"]]
    for path_key,hash_key in (("v25_path","v25_sha256"),("v26_1_path","v26_1_sha256"),("domain_path","domain_sha256")):
        if sha(ROOT/binding[path_key]) != binding[hash_key]: raise RuntimeError("V27 branch lineage drift")
    if len(states["states"]) != len(states["sequence"]) or states["branch_cube"]["complete_candidate_count"] != 1 << states["branch_cube"]["binary_dimension"]: raise RuntimeError("V27 branch cube closure mismatch")
    for relative,expected in manifest["source_sha256"].items():
        if sha(ROOT/relative) != expected: raise RuntimeError(f"V27 source drift: {relative}")
    return seal,states

def evaluate(manifest_path,sealed_dir,target_path,output_path):
    seal,states=verify(manifest_path,sealed_dir);sealed_dir=Path(sealed_dir).resolve();target_path=Path(target_path).resolve();output_path=Path(output_path)
    p,t=parse_ca(str(sealed_dir/"prediction.pdb")),parse_ca(str(target_path));n=min(len(p),len(t));p,t=p[:n],t[:n];pd=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2);td=np.linalg.norm(t[:,None,:]-t[None,:,:],axis=2)
    result={"schema":"fold-protein-blind-evaluation/v27","status":"completed","result_type":"cumulative development benchmark","official_run":False,"run_id":seal["run_id"],"execution":"post-seal structural comparison","seal_sha256":sha(sealed_dir/"seal.json"),"target_id":target_path.name,"target_sha256":sha(target_path),"matched_ca_atoms":n,"tm_score":float(compute_tm(p,t)),"ca_drmsd_angstrom":float(np.sqrt(np.mean((pd-td)**2))),"sequence_length":len(states["sequence"]),"v25_departures":states["v25_departures"],"v26_1_departures":states["v26_1_departures"],"branch_cube_candidates":states["branch_cube"]["complete_candidate_count"]}
    if output_path.exists(): raise FileExistsError(output_path)
    output_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");return result

def main():
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("sealed_dir",type=Path);p.add_argument("target",type=Path);p.add_argument("output",type=Path);a=p.parse_args();print(json.dumps(evaluate(a.manifest,a.sealed_dir,a.target,a.output),sort_keys=True))
if __name__ == "__main__":main()
