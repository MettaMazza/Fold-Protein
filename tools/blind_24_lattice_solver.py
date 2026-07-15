#!/usr/bin/env python3
import sys
import math
import numpy as np
from predict_structure import build_backbone_coordinates, write_pdb

# 24-Lattice Exact Rational Preimages (15 degree increments = 1/24 of circle)
SFT_CANDIDATES = []
for phi_deg in range(-180, 180, 15):
    for psi_deg in range(-180, 180, 15):
        SFT_CANDIDATES.append((math.radians(phi_deg), math.radians(psi_deg)))

HYDROPHOBICS = set(['V', 'I', 'L', 'M', 'F', 'W', 'C', 'Y'])

def score_geometric_topology(partial_seq_chars, P_partial):
    """
    Zero-Parameter Geometric Scoring Function.
    Evaluates the Topological Wavefront exclusively via Radius of Gyration 
    and Hydrophobic Compaction, with no Oracle RMSD reference.
    """
    N = len(P_partial)
    if N < 2:
        return 0.0
        
    # 1. Topological Radius of Gyration (Compaction)
    center = np.mean(P_partial, axis=0)
    rg_sq = np.sum((P_partial - center)**2) / N
    rg = math.sqrt(rg_sq)
    
    # 2. Hydrophobic Collapse Reward
    # Drives micelle-like compaction of the hydrophobic core deterministically
    hp_reward = 0.0
    if N > 4:
        hp_indices = [i for i, res in enumerate(partial_seq_chars) if res in HYDROPHOBICS]
        for idx1 in range(len(hp_indices)):
            for idx2 in range(idx1 + 1, len(hp_indices)):
                i = hp_indices[idx1]
                j = hp_indices[idx2]
                if j - i > 3:  # Only reward non-local compaction
                    dist = np.linalg.norm(P_partial[i] - P_partial[j])
                    if dist < 8.0:
                        hp_reward += 10.0 / dist
                        
    # Total geometric energy (minimize this value)
    return rg - hp_reward

def blind_beam_search(sequence, output_path, beam_width=2000):
    secondary_structures = ['C'] * len(sequence) # Neutral prior topology
    
    # Beam contains tuples of (geometric_score, state_sequence)
    beam = [(0.0, [])]
    
    print(f"Launching Blind SFT 24-Lattice Assembly. Sequence Length: {len(sequence)}")
    
    for i in range(len(sequence)):
        next_beam = []
        for score, state_seq in beam:
            for cand_idx in range(len(SFT_CANDIDATES)):
                new_seq = state_seq + [cand_idx]
                
                partial_seq_chars = sequence[:i+1]
                partial_ss = secondary_structures[:i+1]
                phi_angles = [SFT_CANDIDATES[idx][0] for idx in new_seq]
                psi_angles = [SFT_CANDIDATES[idx][1] for idx in new_seq]
                
                atoms = build_backbone_coordinates(partial_seq_chars, partial_ss, phi_angles, psi_angles)
                ca_atoms = [atom for atom in atoms if atom['name'] == 'CA']
                P_partial = np.array([ca['coord'] for ca in ca_atoms])
                
                # O(1) Steric Clash Filter
                if i >= 3:
                    new_ca = P_partial[-1]
                    dists = np.linalg.norm(P_partial[:-3] - new_ca, axis=1)
                    if np.any(dists < 3.2):
                        continue # Reject mathematically impossible overlaps
                        
                geom_score = score_geometric_topology(partial_seq_chars, P_partial)
                next_beam.append((geom_score, new_seq))
                
        if not next_beam:
            print("ERROR: Total Steric Collapse. Beam exhausted.")
            sys.exit(1)
            
        # Sort by lowest geometric score (most compacted topology)
        next_beam.sort(key=lambda x: x[0])
        beam = next_beam[:beam_width]
        
        best = beam[0][0]
        worst = beam[-1][0]
        print(f"Topological Depth {i+1:02d}/{len(sequence)} | Fold-Natural Capacity: {len(beam)} | Best E: {best:.3f} | Worst E: {worst:.3f}", flush=True)
        
    best_seq = beam[0][1]
    
    # Rebuild the final atomic coordinates for the global minimum trajectory
    phi_angles = [SFT_CANDIDATES[idx][0] for idx in best_seq]
    psi_angles = [SFT_CANDIDATES[idx][1] for idx in best_seq]
    best_atoms = build_backbone_coordinates(sequence, secondary_structures, phi_angles, psi_angles)
    
    write_pdb(best_atoms, output_path)
    print(f"Blind Assembly Complete! Deterministic zero-parameter structure saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 blind_24_lattice_solver.py <sequence> <output.pdb>")
        sys.exit(1)
        
    seq = sys.argv[1].upper()
    out = sys.argv[2]
    
    # We maintain a high beam width for maximum Fold-Natural Capacity
    blind_beam_search(seq, out, beam_width=2000)
