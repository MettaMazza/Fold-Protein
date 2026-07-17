#!/usr/bin/env python3
import sys
import math
import numpy as np
from predict_structure import parse_pdb_backbone, build_backbone_coordinates

SFT_CANDIDATES = [
    (math.radians(-60.0), math.radians(-45.0)),
    (math.radians(-120.0), math.radians(135.0)),
    (math.radians(60.0), math.radians(45.0)),
    (math.radians(-90.0), math.radians(120.0)),
    (math.radians(-60.0), math.radians(120.0)),
    (math.radians(-120.0), math.radians(150.0)),
    (math.radians(-90.0), math.radians(0.0)),
    (math.radians(-60.0), math.radians(90.0)),
    (math.radians(60.0), math.radians(60.0))
]

def rmsd_kabsch(P, Q):
    P_center = np.mean(P, axis=0)
    Q_center = np.mean(Q, axis=0)
    P_centered = P - P_center
    Q_centered = Q - Q_center
    C = np.dot(P_centered.T, Q_centered)
    U, S, Vt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(U) * np.linalg.det(Vt))
    D = np.diag([1, 1, d])
    R = np.dot(U, np.dot(D, Vt))
    P_aligned = np.dot(P_centered, R)
    diff = P_aligned - Q_centered
    rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=-1)))
    return rmsd

def beam_search(sequence, target_pdb_path, output_path, beam_width=1000):
    with open(target_pdb_path) as f:
        target_content = f.read()
    target_residues = parse_pdb_backbone(target_content)
    Q_full = np.array([r["CA"] for r in target_residues])
    
    # Beam contains tuples of (rmsd, state_sequence)
    # Start with an empty sequence
    beam = [(0.0, [])]
    
    # We need a dummy secondary structures list for build_backbone_coordinates
    secondary_structures = ['C'] * len(sequence)
    
    for i in range(len(sequence)):
        next_beam = []
        Q_partial = Q_full[:i+1]
        
        for _, state_seq in beam:
            for cand_idx in range(len(SFT_CANDIDATES)):
                new_seq = state_seq + [cand_idx]
                
                # We need to build the coordinates for the partial sequence.
                # To do this using build_backbone_coordinates, we pad the rest with 0s.
                pad_len = len(sequence) - len(new_seq)
                full_seq = new_seq + [0] * pad_len
                
                phi_angles = [SFT_CANDIDATES[idx][0] for idx in full_seq]
                psi_angles = [SFT_CANDIDATES[idx][1] for idx in full_seq]
                
                atoms = build_backbone_coordinates(sequence, secondary_structures, phi_angles, psi_angles)
                ca_atoms = [atom for atom in atoms if atom['name'] == 'CA']
                
                # Take the first i+1 CA atoms
                P_partial = np.array([ca['coord'] for ca in ca_atoms[:i+1]])
                
                # Calculate RMSD
                if len(P_partial) > 1:
                    r = rmsd_kabsch(P_partial, Q_partial)
                else:
                    r = 0.0
                
                next_beam.append((r, new_seq))
                
        # Sort by RMSD and slice top beam_width
        next_beam.sort(key=lambda x: x[0])
        beam = next_beam[:beam_width]
        
        print(f"Step {i+1:02d}/{len(sequence)} | Beam Best RMSD: {beam[0][0]:.3f}A | Beam Worst RMSD: {beam[-1][0]:.3f}A")
        
    best_seq = beam[0][1]
    print(f"\nBeam Search Complete. Best sequence: {best_seq}")
    
    # Calculate final full TM-score
    from predict_structure import eval_candidate_sequence_multi, write_pdb
    tm, drmsd, best_atoms = eval_candidate_sequence_multi(sequence, best_seq, Q_full, SFT_CANDIDATES)
    print(f"Final Full TM-score: {tm:.4f} | dRMSD: {drmsd:.3f}A")
    write_pdb(best_atoms, output_path)

if __name__ == '__main__':
    seq = sys.argv[1].upper()
    target = sys.argv[2]
    out = sys.argv[3]
    beam_search(seq, target, out, beam_width=500)

