#!/usr/bin/env python3
"""Verify and evaluate sealed boundary-closed selector V24.1."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from calculate_tm import compute_tm,parse_ca
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify(manifest_path,sealed_dir):
    manifest_path,sealed_dir=Path(manifest_path).resolve(),Path(sealed_dir).resolve();m=json.loads(manifest_path.read_text());s=json.loads((sealed_dir/"seal.json").read_text())
    if m.get("schema")!="fold-protein-blind-selector/v24.1" or s.get("schema")!="fold-protein-blind-seal/v24.1":raise RuntimeError("invalid V24.1 seal")
    for f,p in {"protocol_manifest_sha256":manifest_path,"selector_input_sha256":sealed_dir/"selector_input.json","selected_states_sha256":sealed_dir/"selected_states.json","prediction_pdb_sha256":sealed_dir/"prediction.pdb"}.items():
        if s.get(f)!=sha(p):raise RuntimeError(f"V24.1 seal mismatch: {f}")
    states=json.loads((sealed_dir/"selected_states.json").read_text());parent=m["parent_records"][s["parent_run_id"]]
    if sha(ROOT/parent["path"])!=parent["sha256"]:raise RuntimeError("V24.1 parent drift")
    if states["reconciliation"]["complete_local_window_count"]!=len(states["sequence"])-1:raise RuntimeError("V24.1 local closure mismatch")
    for relative,expected in m["source_sha256"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError(f"V24.1 source drift: {relative}")
    return s,states
def evaluate(manifest_path,sealed_dir,target_path,output_path):
    s,states=verify(manifest_path,sealed_dir);sealed_dir=Path(sealed_dir).resolve();target_path=Path(target_path).resolve();output_path=Path(output_path);p,t=parse_ca(str(sealed_dir/"prediction.pdb")),parse_ca(str(target_path));n=min(len(p),len(t));p,t=p[:n],t[:n];pd=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2);td=np.linalg.norm(t[:,None,:]-t[None,:,:],axis=2);r={"schema":"fold-protein-blind-evaluation/v24.1","status":"completed","result_type":"cumulative development benchmark","official_run":False,"run_id":s["run_id"],"execution":"post-seal structural comparison","seal_sha256":sha(sealed_dir/"seal.json"),"target_id":target_path.name,"target_sha256":sha(target_path),"matched_ca_atoms":n,"tm_score":float(compute_tm(p,t)),"ca_drmsd_angstrom":float(np.sqrt(np.mean((pd-td)**2))),"sequence_length":len(states["sequence"]),"parent_departures":states["parent_departures"]}
    if output_path.exists():raise FileExistsError(output_path)
    output_path.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");return r
def main():
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("sealed_dir",type=Path);p.add_argument("target",type=Path);p.add_argument("output",type=Path);a=p.parse_args();print(json.dumps(evaluate(a.manifest,a.sealed_dir,a.target,a.output),sort_keys=True))
if __name__=="__main__":main()
