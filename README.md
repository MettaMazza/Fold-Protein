# Fold Protein

Fold Protein is the protein-structure computational-proof project of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything). SFT begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold.

## Secured result

The repository contains a reproducible **target-assisted construction-parity result** for the 76-residue ubiquitin Cα backbone on a fixed 24×24 dihedral lattice:

- repository-defined Kabsch TM-like score: **0.9891211351**;
- Cα distance-matrix RMSD: **0.2608575408 Å**;
- zero trained weights and no gradient training;
- committed state path, source hashes, witness PDB, and byte-exact replay.

Run the release check:

```sh
python3 verify/replay_ubiquitin_24_lattice.py
```

The native `1ubq` coordinates were used during development to select the successful state path. This secures **construction parity / structural parity** at the declared comparison boundary; “parity” is not being redefined to mean predictive parity. Blind sequence-to-structure prediction is the active forward-forcing extension, not a condition placed on the secured construction victory.

## Claim discipline

Every project element is labelled as one of:

- **forced** from the theorem through the SFT engine;
- **constitutionally re-derived** from established mathematics/computation;
- **engineering**, pending derivation or replacement.

No agent or author preference defines validity. The engine's trace and halt standards do. Maria Smith defines which bounded conclusions are ready to publish from the resulting evidence and may re-steer the investigation.

## Evidence map

| Path | Role |
|---|---|
| `verify/ubiquitin_24_lattice_manifest.json` | exact sequence, 76 lattice states, hashes, metrics, and claim boundary |
| `verify/replay_ubiquitin_24_lattice.py` | independent release replay |
| `verify/1ubq_test_24_lattice.pdb` | constructed witness |
| `verify/1ubq.pdb` | experimental target used in development and scoring |
| `tools/predict_structure.py` | committed NeRF backbone builder |
| `calculate_tm.py` | repository Kabsch TM-like scorer |
| `verify/test_protein_folding*.c` | project law checks |
| `papers/` | current bounded papers |

The producing 576-state target-assisted search is not preserved as a complete executable provenance chain. The committed `beam_search_engine.py` is not represented as the producer of this witness.

## Papers

- [Super Parity in a Target-Assisted 24-Lattice Construction of the Ubiquitin Cα Backbone](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)
- [Fold Protein: A Forced-Geometry Programme for Protein Structure](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)

Sibling computational-proof projects: [UnisonAI](https://github.com/MettaMazza/UnisonAI) · [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).
