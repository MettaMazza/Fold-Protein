#!/usr/bin/env python3
"""Run and immutably seal boundary-closed selector V24.1."""
from __future__ import annotations
import argparse,json,os,shutil,tempfile
from pathlib import Path
from tools.blind_24_lattice_selector_v23 import DOMAIN_CAPACITY,DOMAIN_STATE_COUNT,FRONTIER_CAPACITY,SEGMENT_RESIDUES
from tools.blind_24_lattice_selector_v24_1 import select_state_path_v24_1
from tools.protein_backbone_geometry_v1 import write_pdb
from tools.run_blind_protocol_v21 import sha256_bytes,sha256_file
from tools.run_blind_protocol_v24 import ROOT,_registered_parent

def run_protocol_v24_1(manifest_path:Path,input_path:Path,output_dir:Path):
    manifest_path,input_path,output_dir=map(Path.resolve,(manifest_path,input_path,output_dir))
    if output_dir.exists():raise FileExistsError(output_dir)
    mr,ir=manifest_path.read_bytes(),input_path.read_bytes();m,i=json.loads(mr),json.loads(ir)
    if m.get("schema")!="fold-protein-blind-selector/v24.1":raise ValueError("unsupported V24.1 manifest")
    for relative,expected in m["source_sha256"].items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError(f"protocol source drift: {relative}")
    if set(i)!={"run_id","sequence","parent_run_id"}:raise ValueError("V24.1 input fields drift")
    sequence=i["sequence"].upper();parent,binding=_registered_parent(m,i["parent_run_id"],sequence)
    expected={"complete_domain_states":576,"domain_capacity":24,"segment_residues":4,"segment_frontier_capacity":24,"frontier_capacity":24,"segment_construction":"V19-wrapped V13 local tuple frontier","boundary_context":"all crossing local windows during assembly and every local window at reconciliation","assembly_directions":["forward","reverse"],"target":None,"template":None,"reward":None,"weight":None,"trained_parameter":None}
    if m.get("selector_config")!=expected:raise RuntimeError("V24.1 configuration drift")
    output_dir.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix="fold-protein-v24-1-sealed-",dir=output_dir.parent))
    try:
        (stage/"selector_input.json").write_bytes(ir)
        r=select_state_path_v24_1(sequence,parent["seed_states"],parent["domain_trace"])
        record={"schema":"fold-protein-selected-states/v24.1","status":"completed","run_id":i["run_id"],"sequence":sequence,"parent_run_id":i["parent_run_id"],"parent_selected_states_sha256":binding["sha256"],"states":r["states"],"seed_states":r["seed_states"],"parent_departures":r["parent_departures"],"segment_generation_trace":r["segment_generation_trace"],"assembly_trace":r["assembly_trace"],"reconciliation":r["reconciliation"],"final_relations":r["final_relations"],"constraint_graph_census":r["constraint_graph_census"],"domain_state_count":r["domain_state_count"],"domain_capacity":r["domain_capacity"],"frontier_capacity":r["frontier_capacity"],"segment_residues":r["segment_residues"],"segment_count":r["segment_count"],"whole_chain_evaluations":r["whole_chain_evaluations"],"whole_chain_cache_hits":r["whole_chain_cache_hits"],"runtime_seconds":r["runtime_seconds"],"orientation_modes":r["orientation_modes"],"orientation_trace":r["orientation_trace"],"charge_census":r["charge_census"],"steric_census":r["steric_census"],"hydrogen_bond_census":r["hydrogen_bond_census"],"topology_hydrogen_bond_census":r["topology_hydrogen_bond_census"],"sidechain_graph_spatial_census":r["sidechain_graph_spatial_census"]}
        sb=(json.dumps(record,indent=2,sort_keys=True)+"\n").encode();(stage/"selected_states.json").write_bytes(sb);write_pdb(r["atoms"],stage/"prediction.pdb")
        seal={"schema":"fold-protein-blind-seal/v24.1","status":"completed","result_type":"cumulative development benchmark","official_run":False,"execution":"boundary-closed coherent segment bidirectional assembly","run_id":i["run_id"],"protocol_manifest_sha256":sha256_bytes(mr),"selector_input_sha256":sha256_bytes(ir),"sequence_sha256":sha256_bytes(sequence.encode()),"parent_run_id":i["parent_run_id"],"parent_selected_states_sha256":binding["sha256"],"source_sha256":m["source_sha256"],"selected_states_sha256":sha256_bytes(sb),"prediction_pdb_sha256":sha256_file(stage/"prediction.pdb"),"path_length":len(r["states"]),"parent_departures":r["parent_departures"],"complete_domain_states":DOMAIN_STATE_COUNT,"domain_capacity":DOMAIN_CAPACITY,"segment_frontier_capacity":FRONTIER_CAPACITY,"frontier_capacity":FRONTIER_CAPACITY,"segment_residues":SEGMENT_RESIDUES,"segment_count":r["segment_count"],"whole_chain_evaluations":r["whole_chain_evaluations"],"runtime_seconds":r["runtime_seconds"]}
        (stage/"seal.json").write_text(json.dumps(seal,indent=2,sort_keys=True)+"\n");os.replace(stage,output_dir);return seal
    except Exception:shutil.rmtree(stage,ignore_errors=True);raise

def main():
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("selector_input",type=Path);p.add_argument("output_dir",type=Path);a=p.parse_args();print(json.dumps(run_protocol_v24_1(a.manifest,a.selector_input,a.output_dir),sort_keys=True))
if __name__=="__main__":main()
