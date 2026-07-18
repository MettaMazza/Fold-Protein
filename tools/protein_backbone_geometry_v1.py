#!/usr/bin/env python3
"""Target-incapable peptide-backbone coordinate constitution.

This module is deliberately smaller than ``predict_structure.py``.  It contains
only the declared peptide geometry and the deterministic NeRF construction used
by the protected 24-lattice witness.  It cannot read a target, score a target,
optimise a path, sample, anneal, or select a state.

The dimensioned peptide geometry is a named forward-forcing bridge from the
established coordinate construction, not silently relabelled as a theorem-only
quantity.  Exact declared rationals are converted to floating point only at the
Cartesian readout boundary.  ``verify/protein_backbone_geometry_v1.json`` binds
the bridge and ``verify/replay_protein_backbone_geometry_v1.py`` checks it against
the protected construction byte for byte.
"""
from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path


# Exact declarations carried to the Cartesian readout boundary.
BOND_N_CA = Fraction(146, 100)
BOND_CA_C = Fraction(152, 100)
BOND_C_N = Fraction(133, 100)

ANGLE_C_N_CA_DEGREES = Fraction(121, 1)
ANGLE_N_CA_C_DEGREES = Fraction(111, 1)
ANGLE_CA_C_N_DEGREES = Fraction(116, 1)
DIHEDRAL_OMEGA_DEGREES = Fraction(180, 1)


def _radians(degrees: Fraction | int | float) -> float:
    return math.radians(float(degrees))


def _cross(first, second):
    return [
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    ]


def _normalise(vector):
    length = math.sqrt(sum(value * value for value in vector))
    if length == 0:
        raise RuntimeError("degenerate backbone frame")
    return [value / length for value in vector]


def place_next_atom(p1, p2, p3, bond_length: Fraction, bond_angle, dihedral):
    """Place one atom by the declared deterministic NeRF relation."""
    v1 = [p3[index] - p2[index] for index in range(3)]
    v2 = [p2[index] - p1[index] for index in range(3)]
    u1 = _normalise(v1)
    u2 = _normalise(v2)
    normal = _normalise(_cross(u2, u1))
    y_axis = _normalise(_cross(normal, u1))

    dx = -math.cos(bond_angle)
    dy = math.sin(bond_angle) * math.cos(dihedral)
    dz = math.sin(bond_angle) * math.sin(dihedral)
    direction = [
        dx * u1[index] + dy * y_axis[index] + dz * normal[index]
        for index in range(3)
    ]
    length = float(bond_length)
    return [p3[index] + length * direction[index] for index in range(3)]


def build_backbone_coordinates(sequence: str, phi_angles, psi_angles):
    """Build N, C-alpha, C coordinates from sequence and declared dihedrals."""
    sequence = str(sequence).strip().upper()
    if not sequence:
        raise ValueError("sequence must be non-empty")
    if len(phi_angles) != len(sequence) or len(psi_angles) != len(sequence):
        raise ValueError("one phi and psi value is required per residue")

    angle_c_n_ca = _radians(ANGLE_C_N_CA_DEGREES)
    angle_n_ca_c = _radians(ANGLE_N_CA_C_DEGREES)
    angle_ca_c_n = _radians(ANGLE_CA_C_N_DEGREES)
    omega = _radians(DIHEDRAL_OMEGA_DEGREES)

    atoms = []
    n_coord = [0.0, 0.0, 0.0]
    ca_coord = [float(BOND_N_CA), 0.0, 0.0]
    c_coord = [
        ca_coord[0] + float(BOND_CA_C) * math.cos(math.pi - angle_n_ca_c),
        ca_coord[1] + float(BOND_CA_C) * math.sin(math.pi - angle_n_ca_c),
        0.0,
    ]
    atoms.extend([
        {"name": "N", "resnum": 1, "resname": sequence[0], "coord": n_coord},
        {"name": "CA", "resnum": 1, "resname": sequence[0], "coord": ca_coord},
        {"name": "C", "resnum": 1, "resname": sequence[0], "coord": c_coord},
    ])

    for index in range(1, len(sequence)):
        p1 = atoms[-3]["coord"]
        p2 = atoms[-2]["coord"]
        p3 = atoms[-1]["coord"]
        n_coord = place_next_atom(
            p1, p2, p3, BOND_C_N, angle_ca_c_n, psi_angles[index - 1]
        )
        ca_coord = place_next_atom(
            p2, p3, n_coord, BOND_N_CA, angle_c_n_ca, omega
        )
        c_coord = place_next_atom(
            p3, n_coord, ca_coord, BOND_CA_C, angle_n_ca_c, phi_angles[index]
        )
        resnum = index + 1
        resname = sequence[index]
        atoms.extend([
            {"name": "N", "resnum": resnum, "resname": resname, "coord": n_coord},
            {"name": "CA", "resnum": resnum, "resname": resname, "coord": ca_coord},
            {"name": "C", "resnum": resnum, "resname": resname, "coord": c_coord},
        ])
    return atoms


def write_pdb(atoms, file_path: str | Path) -> None:
    """Write the exact historical Fold Protein backbone PDB representation."""
    residue_names = {
        "A": "ALA", "R": "ARG", "N": "ASN", "D": "ASP", "C": "CYS",
        "Q": "GLN", "E": "GLU", "G": "GLY", "H": "HIS", "I": "ILE",
        "L": "LEU", "K": "LYS", "M": "MET", "F": "PHE", "P": "PRO",
        "S": "SER", "T": "THR", "W": "TRP", "Y": "TYR", "V": "VAL",
    }
    with Path(file_path).open("w") as handle:
        handle.write("HEADER    SFT PREDICTED STRUCTURE\n")
        for atom_number, atom in enumerate(atoms, start=1):
            x, y, z = atom["coord"]
            residue = residue_names.get(atom["resname"], "ALA")
            handle.write(
                f"ATOM  {atom_number:5d}  {atom['name']:<4s}{residue} "
                f"A{atom['resnum']:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  "
                f"1.00  0.00           {atom['name'][0]}\n"
            )
        handle.write("END\n")
