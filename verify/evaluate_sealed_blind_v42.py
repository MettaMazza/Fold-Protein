#!/usr/bin/env python3
"""Verify the V42 frontier seal, then compare every retained prediction."""
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
import numpy as np
from calculate_tm import compute_tm, parse_ca

ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_v42_seal(manifest_path: Path, sealed_dir: Path):
    manifest_path,sealed_dir=manifest_path.resolve(),sealed_dir.resolve()
    manifest=json.loads(manifest_path.read_text());seal=json.loads((sealed_dir/"seal.json").read_text())
    if manifest.get("schema")!="fold-protein-blind-selector/v42" or seal.get("schema")!="fold-protein-blind-seal/v42": raise RuntimeError("invalid V42 seal")
    checks={"protocol_manifest_sha256":sha(manifest_path),"selector_input_sha256":sha(sealed_dir/"selector_input.json"),"frontier_sha256":sha(sealed_dir/"frontier.json")}
    for key,value in checks.items():
        if seal.get(key)!=value: raise RuntimeError(f"V42 seal mismatch: {key}")
    for name,value in seal["prediction_pdb_sha256"].items():
        if sha(sealed_dir/name)!=value: raise RuntimeError(f"V42 PDB drift: {name}")
    for relative,value in manifest["source_sha256"].items():
        if sha(ROOT/relative)!=value or seal["source_sha256"].get(relative)!=value: raise RuntimeError(f"V42 source drift: {relative}")
    frontier=json.loads((sealed_dir/"frontier.json").read_text())
    if frontier["component_cube_candidates"]!=8192 or frontier["connected_frontier_count"]!=3 or [r["mask"] for r in frontier["frontier"]]!=[2178,5814,5815]: raise RuntimeError("V42 complete frontier drifted")
    return seal,frontier

def evaluate_v42(manifest_path,sealed_dir,target_path,output_path):
    seal,frontier=verify_v42_seal(manifest_path,sealed_dir);target=parse_ca(str(Path(target_path).resolve()))
    rows=[]
    for row in frontier["frontier"]:
        name=f"prediction_mask_{row['mask']}.pdb";pred=parse_ca(str(Path(sealed_dir).resolve()/name));n=min(len(pred),len(target));p,q=pred[:n],target[:n]
        pd=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2);qd=np.linalg.norm(q[:,None,:]-q[None,:,:],axis=2)
        rows.append({"mask":row["mask"],"matched_ca_atoms":n,"tm_score":float(compute_tm(p,q)),"ca_drmsd_angstrom":float(np.sqrt(np.mean((pd-qd)**2))),"graph_components":row["graph_components"],"interblock_edges":row["interblock_edges"],"contact_residue_pairs":row["contact_residue_pairs"],"contact_atom_pairs":row["contact_atom_pairs"],"prediction_pdb_sha256":seal["prediction_pdb_sha256"][name]})
    evidence={"schema":"fold-protein-blind-evaluation/v42","status":"completed","result_type":"cumulative development benchmark","official_run":False,"execution":"post-seal comparison of complete connected frontier","seal_sha256":sha(Path(sealed_dir)/"seal.json"),"target_id":Path(target_path).name,"target_sha256":sha(target_path),"frontier":rows}
    if Path(output_path).exists(): raise FileExistsError(output_path)
    Path(output_path).write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n");return evidence

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("sealed_dir",type=Path);p.add_argument("target",type=Path);p.add_argument("output",type=Path);a=p.parse_args();print(json.dumps(evaluate_v42(a.manifest,a.sealed_dir,a.target,a.output),sort_keys=True))
