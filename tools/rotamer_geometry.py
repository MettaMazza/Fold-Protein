import math

# Standard physical bond lengths (Å)
B_CC = 1.53
B_C_O = 1.23
B_C_N = 1.33
B_AROMATIC = 1.39
B_S = 1.81 # C-S bond

# Standard physical angles (radians)
A_TETRA = math.radians(109.5)
A_PLANAR = math.radians(120.0)

def cross_product(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

def normalize(v):
    l = math.sqrt(sum(x*x for x in v))
    if l == 0:
        return [0, 0, 0]
    return [x/l for x in v]

def place_next_atom(p1, p2, p3, bond_length, bond_angle, dihedral):
    v1 = [p3[i] - p2[i] for i in range(3)]
    v2 = [p2[i] - p1[i] for i in range(3)]
    u1 = normalize(v1)
    u2 = normalize(v2)
    un = normalize(cross_product(u2, u1))
    x_axis = u1
    y_axis = normalize(cross_product(un, u1))
    z_axis = un
    theta = bond_angle
    chi = dihedral
    dx = -math.cos(theta)
    dy = math.sin(theta) * math.cos(chi)
    dz = math.sin(theta) * math.sin(chi)
    gx = dx * x_axis[0] + dy * y_axis[0] + dz * z_axis[0]
    gy = dx * x_axis[1] + dy * y_axis[1] + dz * z_axis[1]
    gz = dx * x_axis[2] + dy * y_axis[2] + dz * z_axis[2]
    return [
        p3[0] + bond_length * gx,
        p3[1] + bond_length * gy,
        p3[2] + bond_length * gz
    ]

# Topology for heavy atoms: 
# AA: { 'atoms': [name1, ...], 'bonds': [(a1, a2, len), ...], 'angles': [(a1, a2, a3, ang), ...], 'dihedrals': [(a1,a2,a3,a4, var_name), ...] }
# We assume N, CA, C, O, CB are already generated.

SIDECHAIN_TOPOLOGY = {
    'G': {'atoms': [], 'bonds': [], 'angles': [], 'dihedrals': []},
    'A': {'atoms': [], 'bonds': [], 'angles': [], 'dihedrals': []},
    
    'V': {
        'atoms': ['CG1', 'CG2'],
        'bonds': [('CB', 'CG1', B_CC), ('CB', 'CG2', B_CC)],
        'angles': [('CA', 'CB', 'CG1', A_TETRA), ('CA', 'CB', 'CG2', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG1', 'chi1'), ('N', 'CA', 'CB', 'CG2', 'chi1+120')]
    },
    'L': {
        'atoms': ['CG', 'CD1', 'CD2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD1', B_CC), ('CG', 'CD2', B_CC)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD1', A_TETRA), ('CB', 'CG', 'CD2', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD1', 'chi2'), ('CA', 'CB', 'CG', 'CD2', 'chi2+120')]
    },
    'I': {
        'atoms': ['CG1', 'CG2', 'CD1'],
        'bonds': [('CB', 'CG1', B_CC), ('CB', 'CG2', B_CC), ('CG1', 'CD1', B_CC)],
        'angles': [('CA', 'CB', 'CG1', A_TETRA), ('CA', 'CB', 'CG2', A_TETRA), ('CB', 'CG1', 'CD1', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG1', 'chi1'), ('N', 'CA', 'CB', 'CG2', 'chi1+120'), ('CA', 'CB', 'CG1', 'CD1', 'chi2')]
    },
    'S': {
        'atoms': ['OG'],
        'bonds': [('CB', 'OG', 1.42)],
        'angles': [('CA', 'CB', 'OG', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'OG', 'chi1')]
    },
    'T': {
        'atoms': ['OG1', 'CG2'],
        'bonds': [('CB', 'OG1', 1.42), ('CB', 'CG2', B_CC)],
        'angles': [('CA', 'CB', 'OG1', A_TETRA), ('CA', 'CB', 'CG2', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'OG1', 'chi1'), ('N', 'CA', 'CB', 'CG2', 'chi1+120')]
    },
    'C': {
        'atoms': ['SG'],
        'bonds': [('CB', 'SG', B_S)],
        'angles': [('CA', 'CB', 'SG', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'SG', 'chi1')]
    },
    'M': {
        'atoms': ['CG', 'SD', 'CE'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'SD', B_S), ('SD', 'CE', B_S)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'SD', A_TETRA), ('CG', 'SD', 'CE', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'SD', 'chi2'), ('CB', 'CG', 'SD', 'CE', 'chi3')]
    },
    'D': {
        'atoms': ['CG', 'OD1', 'OD2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'OD1', B_C_O), ('CG', 'OD2', B_C_O)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'OD1', A_PLANAR), ('CB', 'CG', 'OD2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'OD1', 'chi2'), ('CA', 'CB', 'CG', 'OD2', 'chi2+180')]
    },
    'E': {
        'atoms': ['CG', 'CD', 'OE1', 'OE2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD', B_CC), ('CD', 'OE1', B_C_O), ('CD', 'OE2', B_C_O)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD', A_TETRA), ('CG', 'CD', 'OE1', A_PLANAR), ('CG', 'CD', 'OE2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD', 'chi2'), ('CB', 'CG', 'CD', 'OE1', 'chi3'), ('CB', 'CG', 'CD', 'OE2', 'chi3+180')]
    },
    'N': {
        'atoms': ['CG', 'OD1', 'ND2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'OD1', B_C_O), ('CG', 'ND2', B_C_N)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'OD1', A_PLANAR), ('CB', 'CG', 'ND2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'OD1', 'chi2'), ('CA', 'CB', 'CG', 'ND2', 'chi2+180')]
    },
    'Q': {
        'atoms': ['CG', 'CD', 'OE1', 'NE2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD', B_CC), ('CD', 'OE1', B_C_O), ('CD', 'NE2', B_C_N)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD', A_TETRA), ('CG', 'CD', 'OE1', A_PLANAR), ('CG', 'CD', 'NE2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD', 'chi2'), ('CB', 'CG', 'CD', 'OE1', 'chi3'), ('CB', 'CG', 'CD', 'NE2', 'chi3+180')]
    },
    'K': {
        'atoms': ['CG', 'CD', 'CE', 'NZ'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD', B_CC), ('CD', 'CE', B_CC), ('CE', 'NZ', B_C_N)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD', A_TETRA), ('CG', 'CD', 'CE', A_TETRA), ('CD', 'CE', 'NZ', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD', 'chi2'), ('CB', 'CG', 'CD', 'CE', 'chi3'), ('CG', 'CD', 'CE', 'NZ', 'chi4')]
    },
    'R': {
        'atoms': ['CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD', B_CC), ('CD', 'NE', B_C_N), ('NE', 'CZ', B_C_N), ('CZ', 'NH1', B_C_N), ('CZ', 'NH2', B_C_N)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD', A_TETRA), ('CG', 'CD', 'NE', A_TETRA), ('CD', 'NE', 'CZ', A_PLANAR), ('NE', 'CZ', 'NH1', A_PLANAR), ('NE', 'CZ', 'NH2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD', 'chi2'), ('CB', 'CG', 'CD', 'NE', 'chi3'), ('CG', 'CD', 'NE', 'CZ', 'chi4'), ('CD', 'NE', 'CZ', 'NH1', 'chi5'), ('CD', 'NE', 'CZ', 'NH2', 'chi5+180')]
    },
    'F': {
        'atoms': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD1', B_AROMATIC), ('CG', 'CD2', B_AROMATIC), ('CD1', 'CE1', B_AROMATIC), ('CD2', 'CE2', B_AROMATIC), ('CE1', 'CZ', B_AROMATIC), ('CE2', 'CZ', B_AROMATIC)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD1', A_PLANAR), ('CB', 'CG', 'CD2', A_PLANAR), ('CG', 'CD1', 'CE1', A_PLANAR), ('CG', 'CD2', 'CE2', A_PLANAR), ('CD1', 'CE1', 'CZ', A_PLANAR), ('CD2', 'CE2', 'CZ', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD1', 'chi2'), ('CA', 'CB', 'CG', 'CD2', 'chi2+180'), ('CB', 'CG', 'CD1', 'CE1', '180'), ('CB', 'CG', 'CD2', 'CE2', '180'), ('CG', 'CD1', 'CE1', 'CZ', '0'), ('CG', 'CD2', 'CE2', 'CZ', '0')]
    },
    'Y': {
        'atoms': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD1', B_AROMATIC), ('CG', 'CD2', B_AROMATIC), ('CD1', 'CE1', B_AROMATIC), ('CD2', 'CE2', B_AROMATIC), ('CE1', 'CZ', B_AROMATIC), ('CE2', 'CZ', B_AROMATIC), ('CZ', 'OH', 1.36)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD1', A_PLANAR), ('CB', 'CG', 'CD2', A_PLANAR), ('CG', 'CD1', 'CE1', A_PLANAR), ('CG', 'CD2', 'CE2', A_PLANAR), ('CD1', 'CE1', 'CZ', A_PLANAR), ('CD2', 'CE2', 'CZ', A_PLANAR), ('CE1', 'CZ', 'OH', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD1', 'chi2'), ('CA', 'CB', 'CG', 'CD2', 'chi2+180'), ('CB', 'CG', 'CD1', 'CE1', '180'), ('CB', 'CG', 'CD2', 'CE2', '180'), ('CG', 'CD1', 'CE1', 'CZ', '0'), ('CG', 'CD2', 'CE2', 'CZ', '0'), ('CD1', 'CE1', 'CZ', 'OH', '180')]
    },
    'W': {
        'atoms': ['CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD1', B_AROMATIC), ('CG', 'CD2', B_AROMATIC), ('CD1', 'NE1', B_AROMATIC), ('CD2', 'CE2', B_AROMATIC), ('NE1', 'CE2', B_AROMATIC), ('CD2', 'CE3', B_AROMATIC), ('CE2', 'CZ2', B_AROMATIC), ('CE3', 'CZ3', B_AROMATIC), ('CZ2', 'CH2', B_AROMATIC), ('CZ3', 'CH2', B_AROMATIC)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD1', A_PLANAR), ('CB', 'CG', 'CD2', A_PLANAR), ('CG', 'CD1', 'NE1', A_PLANAR), ('CG', 'CD2', 'CE2', A_PLANAR), ('CD1', 'NE1', 'CE2', A_PLANAR), ('CG', 'CD2', 'CE3', A_PLANAR), ('CD2', 'CE2', 'CZ2', A_PLANAR), ('CD2', 'CE3', 'CZ3', A_PLANAR), ('CE2', 'CZ2', 'CH2', A_PLANAR), ('CE3', 'CZ3', 'CH2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD1', 'chi2'), ('CA', 'CB', 'CG', 'CD2', 'chi2+180'), ('CB', 'CG', 'CD1', 'NE1', '180'), ('CB', 'CG', 'CD2', 'CE2', '180'), ('CG', 'CD1', 'NE1', 'CE2', '0'), ('CG', 'CD2', 'CE3', '180'), ('CD1', 'NE1', 'CE2', 'CZ2', '180'), ('NE1', 'CE2', 'CZ2', 'CH2', '180'), ('CE2', 'CD2', 'CE3', 'CZ3', '180'), ('CD2', 'CE3', 'CZ3', 'CH2', '0')]
    },
    'H': {
        'atoms': ['CG', 'ND1', 'CD2', 'CE1', 'NE2'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'ND1', B_AROMATIC), ('CG', 'CD2', B_AROMATIC), ('ND1', 'CE1', B_AROMATIC), ('CD2', 'NE2', B_AROMATIC), ('CE1', 'NE2', B_AROMATIC)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'ND1', A_PLANAR), ('CB', 'CG', 'CD2', A_PLANAR), ('CG', 'ND1', 'CE1', A_PLANAR), ('CG', 'CD2', 'NE2', A_PLANAR), ('ND1', 'CE1', 'NE2', A_PLANAR)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'ND1', 'chi2'), ('CA', 'CB', 'CG', 'CD2', 'chi2+180'), ('CB', 'CG', 'ND1', 'CE1', '180'), ('CB', 'CG', 'CD2', 'NE2', '180'), ('CG', 'ND1', 'CE1', 'NE2', '0')]
    },
    'P': {
        'atoms': ['CG', 'CD'],
        'bonds': [('CB', 'CG', B_CC), ('CG', 'CD', B_CC)],
        'angles': [('CA', 'CB', 'CG', A_TETRA), ('CB', 'CG', 'CD', A_TETRA)],
        'dihedrals': [('N', 'CA', 'CB', 'CG', 'chi1'), ('CA', 'CB', 'CG', 'CD', 'chi2')]
    }
}

def build_sidechain_atoms(resname, resnum, coords_dict, chi_angles):
    """
    Constructs the sidechain heavy atoms for a given residue using its chi angles.
    coords_dict must contain: 'N', 'CA', 'C', 'CB' coordinates for this residue.
    chi_angles is a dictionary {'chi1': val, 'chi2': val, ...}.
    Returns a list of atom dicts: [{"name": name, "resnum": resnum, "resname": resname, "coord": [x,y,z]}, ...]
    """
    if resname not in SIDECHAIN_TOPOLOGY or not SIDECHAIN_TOPOLOGY[resname]['atoms']:
        return []
    
    topo = SIDECHAIN_TOPOLOGY[resname]
    atoms_built = []
    
    # Track coordinates natively
    local_coords = {
        'N': coords_dict.get('N'),
        'CA': coords_dict.get('CA'),
        'C': coords_dict.get('C'),
        'CB': coords_dict.get('CB')
    }
    
    # We must build atoms in the exact order they are listed to guarantee preceding atoms exist.
    for target_atom in topo['atoms']:
        # Find the bond definition: (prev, target_atom, len)
        bond = next(b for b in topo['bonds'] if b[1] == target_atom)
        prev1 = bond[0]
        bond_len = bond[2]
        
        # Find the angle definition: (prev2, prev1, target_atom, angle)
        angle = next(a for a in topo['angles'] if a[2] == target_atom and a[1] == prev1)
        prev2 = angle[0]
        bond_ang = angle[3]
        
        # Find the dihedral definition: (prev3, prev2, prev1, target_atom, dihedral_expr)
        dihed = next(d for d in topo['dihedrals'] if d[3] == target_atom and d[2] == prev1 and d[1] == prev2)
        prev3 = dihed[0]
        dihed_expr = dihed[4]
        
        # Evaluate dihedral expression
        val = 0.0
        if 'chi1' in dihed_expr: val = chi_angles.get('chi1', 0.0)
        elif 'chi2' in dihed_expr: val = chi_angles.get('chi2', 0.0)
        elif 'chi3' in dihed_expr: val = chi_angles.get('chi3', 0.0)
        elif 'chi4' in dihed_expr: val = chi_angles.get('chi4', 0.0)
        elif 'chi5' in dihed_expr: val = chi_angles.get('chi5', 0.0)
        
        if '+120' in dihed_expr: val += math.radians(120.0)
        if '+180' in dihed_expr: val += math.radians(180.0)
        if dihed_expr == '0': val = 0.0
        if dihed_expr == '180': val = math.radians(180.0)
        
        p3 = local_coords[prev1]
        p2 = local_coords[prev2]
        p1 = local_coords[prev3]
        
        new_coord = place_next_atom(p1, p2, p3, bond_len, bond_ang, val)
        local_coords[target_atom] = new_coord
        
        atoms_built.append({
            "name": target_atom,
            "resnum": resnum,
            "resname": resname,
            "coord": new_coord
        })
        
    return atoms_built
