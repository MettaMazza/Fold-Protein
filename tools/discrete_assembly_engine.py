import sys
import math
import numpy as np

# --- SFT Discrete Geometric Constants ---
# Derived from topological preimages in SFT theory (e.g. -1/6, -1/8, etc.)
SFT_BACKBONE_STATES = [
    (math.radians(-60.0), math.radians(-45.0)),   # Alpha Right (-1/6, -1/8)
    (math.radians(-120.0), math.radians(135.0)),  # Beta (-1/3, 3/8)
    (math.radians(60.0), math.radians(45.0)),     # Alpha Left (1/6, 1/8)
    (math.radians(-90.0), math.radians(120.0)),   # Loop/Turn variants
    (math.radians(-60.0), math.radians(120.0)),
    (math.radians(-120.0), math.radians(150.0)),
    (math.radians(-90.0), math.radians(0.0)),
    (math.radians(-60.0), math.radians(90.0)),
    (math.radians(60.0), math.radians(60.0))
]

SFT_CHI_STATES = [
    math.radians(180.0),  # Trans (1/2)
    math.radians(-60.0),  # Gauche- (-1/6)
    math.radians(60.0)    # Gauche+ (1/6)
]

# Standard Bond Lengths & Angles
L_N_CA = 1.46
L_CA_C = 1.52
L_C_N = 1.33
L_C_O = 1.23
L_CA_CB = 1.53

A_C_N_CA = 2.124  # 121.7 degrees
A_N_CA_C = 1.939  # 111.1 degrees
A_CA_C_N = 2.028  # 116.2 degrees
A_CA_C_O = 2.094  # 120.0 degrees
A_N_CA_CB = 1.927 # 110.4 degrees

VDW_RADII = {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8, 'H': 1.2}
RESIDUE_VDW = {'G': 1.5, 'A': 1.8, 'V': 2.2, 'L': 2.4, 'I': 2.4, 'P': 2.0, 'M': 2.6, 'F': 2.8, 'W': 3.0, 'Y': 2.8, 'S': 2.0, 'T': 2.2, 'C': 2.2, 'N': 2.4, 'Q': 2.6, 'D': 2.4, 'E': 2.6, 'K': 2.8, 'R': 3.0, 'H': 2.6}

# --- Pure Discrete Geometry Engine (Zero Tensors) ---
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

def place_next_atom(p1, p2, p3, bond_length, bond_angle, dihedral):
    v1 = p3 - p2
    v2 = p2 - p1
    u1 = normalize(v1)
    u2 = normalize(v2)
    cross_u2_u1 = np.cross(u2, u1)
    un = normalize(cross_u2_u1)
    
    x_axis = u1
    y_axis = normalize(np.cross(un, u1))
    z_axis = un
    
    dx = -math.cos(bond_angle)
    dy = math.sin(bond_angle) * math.cos(dihedral)
    dz = math.sin(bond_angle) * math.sin(dihedral)
    
    d = np.array([dx, dy, dz])
    d_global = d[0] * x_axis + d[1] * y_axis + d[2] * z_axis
    
    return p3 + d_global * bond_length

def build_structure(sequence, state_sequence):
    N = len(sequence)
    atoms = []
    coords_dict = {'N': [], 'CA': [], 'C': [], 'CB': []}
    
    n_pos = np.array([0.0, 0.0, 0.0])
    ca_pos = np.array([L_N_CA, 0.0, 0.0])
    c_pos = np.array([
        L_N_CA + L_CA_C * -math.cos(A_N_CA_C),
        L_CA_C * math.sin(A_N_CA_C),
        0.0
    ])
    
    atoms.extend([
        ('N', n_pos, sequence[0], 1),
        ('CA', ca_pos, sequence[0], 1),
        ('C', c_pos, sequence[0], 1)
    ])
    coords_dict['N'].append(n_pos)
    coords_dict['CA'].append(ca_pos)
    coords_dict['C'].append(c_pos)
    
    if sequence[0] != 'G':
        cb_pos = place_next_atom(n_pos, c_pos, ca_pos, L_CA_CB, A_N_CA_CB, math.radians(122.0))
        atoms.append(('CB', cb_pos, sequence[0], 1))
        coords_dict['CB'].append(cb_pos)
    else:
        coords_dict['CB'].append(None)
        
    for i in range(1, N):
        phi, psi = SFT_BACKBONE_STATES[state_sequence[i]]
        
        # N(i)
        n_pos = place_next_atom(coords_dict['CA'][i-1], coords_dict['C'][i-1], coords_dict['N'][i-1] if i > 1 else np.array([0.0,0.0,0.0]), L_C_N, A_CA_C_N, math.pi) # Omega = pi
        n_pos = place_next_atom(coords_dict['N'][i-1] if i > 1 else np.array([0.,0.,0.]), coords_dict['CA'][i-1], coords_dict['C'][i-1], L_C_N, A_CA_C_N, SFT_BACKBONE_STATES[state_sequence[i-1]][1])
        
        # CA(i)
        ca_pos = place_next_atom(coords_dict['CA'][i-1], coords_dict['C'][i-1], n_pos, L_N_CA, A_C_N_CA, math.pi)
        
        # C(i)
        c_pos = place_next_atom(coords_dict['C'][i-1], n_pos, ca_pos, L_CA_C, A_N_CA_C, phi)
        
        atoms.extend([
            ('N', n_pos, sequence[i], i+1),
            ('CA', ca_pos, sequence[i], i+1),
            ('C', c_pos, sequence[i], i+1)
        ])
        coords_dict['N'].append(n_pos)
        coords_dict['CA'].append(ca_pos)
        coords_dict['C'].append(c_pos)
        
        if sequence[i] != 'G':
            cb_pos = place_next_atom(n_pos, c_pos, ca_pos, L_CA_CB, A_N_CA_CB, math.radians(122.0))
            atoms.append(('CB', cb_pos, sequence[i], i+1))
            coords_dict['CB'].append(cb_pos)
        else:
            coords_dict['CB'].append(None)
            
    return atoms, coords_dict

def evaluate_discrete_state(sequence, coords):
    """
    SFT Physical Scoring Function (Zero Parameters) - Vectorized
    """
    score = 0.0
    N = len(coords['CA'])
    if N < 4:
        return 0.0
        
    CA_tens = np.array(coords['CA'])
    
    sc_centers = []
    for i in range(N):
        if coords['CB'][i] is not None:
            sc_centers.append(coords['CB'][i])
        else:
            sc_centers.append(coords['CA'][i])
    sc_tens = np.array(sc_centers)
    
    # 1. True-Volume V20 proxy sterics (Vectorized)
    # Only penalize if |i - j| > 2
    sc_dmat = np.linalg.norm(sc_tens[:, None, :] - sc_tens[None, :, :], axis=-1)
    
    vdw_radii = np.array([RESIDUE_VDW[res] for res in sequence[:N]])
    min_d_mat = vdw_radii[:, None] + vdw_radii[None, :]
    
    mask_steric = np.triu(np.ones((N, N)), k=3).astype(bool)
    clashes = min_d_mat - sc_dmat
    clashes = np.clip(clashes, 0, None)
    score += np.sum(clashes[mask_steric]) * 10000.0
                
    # 2. V22 Electrostatics
    charge_map = {'K': 1.0, 'R': 1.0, 'H': 0.5, 'D': -1.0, 'E': -1.0}
    charged_indices = [i for i in range(N) if sequence[i] in charge_map]
    
    if len(charged_indices) > 0:
        c_idx = np.array(charged_indices)
        charges = np.array([charge_map[sequence[i]] for i in charged_indices])
        
        ca_dmat_all = np.linalg.norm(CA_tens[:, None, :] - CA_tens[None, :, :], axis=-1)
        neighbors = np.sum(ca_dmat_all < 10.0, axis=1)
        
        c_neighbors = neighbors[c_idx]
        fb = np.clip((c_neighbors - 10.0) / 30.0, 0.0, 1.0)
        eps = 80.0 - fb * 76.0
        
        eps_mat = np.sqrt(eps[:, None] * eps[None, :])
        
        c_dmat = ca_dmat_all[np.ix_(c_idx, c_idx)]
        c_dmat_clamped = np.clip(c_dmat, 4.0, None)
        
        coulomb = (charges[:, None] * charges[None, :]) / (eps_mat * c_dmat_clamped)
        
        c_mask = np.triu(np.ones((len(c_idx), len(c_idx))), k=1).astype(bool)
        score += np.sum(coulomb[c_mask]) * 332.0
        
    # 3. V8 Directional H-Bonds (Simplified proxy here for sequence descent)
    if N > 4:
        for i in range(N - 4):
            d_i_i4 = np.linalg.norm(CA_tens[i] - CA_tens[i+4])
            if d_i_i4 < 6.5: # Alpha helix turn proxy
                score -= 1.5
                
    return score

def write_pdb(atoms, filename):
    with open(filename, 'w') as f:
        for i, (atom_name, pos, res_name, res_num) in enumerate(atoms):
            f.write(f"ATOM  {i+1:5d}  {atom_name:<3s} {res_name} A{res_num:4d}    {pos[0]:8.3f}{pos[1]:8.3f}{pos[2]:8.3f}  1.00  0.00           {atom_name[0]}  \n")
        f.write("TER\nEND\n")

def discrete_topological_beam_search(sequence, output_path, beam_width=500):
    beam = [(0.0, [0])]
    
    print(f"Launching Pure Discrete Topological Assembly. Sequence length: {len(sequence)}")
    
    for i in range(1, len(sequence)):
        next_beam = []
        
        for score, state_seq in beam:
            for cand_idx in range(len(SFT_BACKBONE_STATES)):
                new_seq = state_seq + [cand_idx]
                atoms, coords = build_structure(sequence[:i+1], new_seq)
                new_score = evaluate_discrete_state(sequence[:i+1], coords)
                next_beam.append((new_score, new_seq))
                
        next_beam.sort(key=lambda x: x[0])
        beam = next_beam[:beam_width]
        
        best_score = beam[0][0]
        worst_score = beam[-1][0]
        print(f"Lattice Depth {i+1:02d}/{len(sequence)} | Width: {len(beam)} | Best E: {best_score:9.1f} | Worst E: {worst_score:9.1f}", flush=True)
        
    best_seq = beam[0][1]
    print(f"\nAssembly Terminated. Extracting global minimum configuration...")
    atoms, _ = build_structure(sequence, best_seq)
    write_pdb(atoms, output_path)
    print(f"Saved pure discrete fold to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 discrete_assembly_engine.py <sequence> <output_pdb>")
        sys.exit(1)
    seq = sys.argv[1].upper()
    out = sys.argv[2]
    
    discrete_topological_beam_search(seq, out, beam_width=100)
