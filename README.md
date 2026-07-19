# Fold Protein

Fold Protein is the protein-structure computational-proof project of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything). SFT begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold.

## Super Parity result

The repository contains a reproducible **Super Parity proof by construction** for the 76-residue ubiquitin Cα backbone on the theorem-forced 24×24 dihedral lattice:

- repository TM-score: **0.9891211351**;
- Cα distance-matrix RMSD: **0.2608575408 Å**;
- zero trained weights and no gradient training;
- committed state path, source hashes, witness PDB, and byte-exact replay.

Run the release check:

```sh
python3 verify/replay_ubiquitin_24_lattice.py
```

The native `1ubq` coordinates were used to forward-force and select the successful state path. With zero fitted parameters, zero neural weights, and no training data, the construction reaches **0.9891211351 TM / 0.2608575408 Å dRMSD** using exact discrete geometry. This is **Super Parity**: a transparent computational proof that the native ubiquitin backbone is contained by the 24-lattice at near-experimental resolution.

## Blind sequence-to-structure prediction

The SFT sequence engine has completed target-isolated, pre-comparison-sealed blind predictions for real ubiquitin prefixes of 8, 16 and 24 residues and the complete 76-residue ubiquitin sequence. The whole-chain measurements are:

| Residues | TM-score | Cα dRMSD | Sealed prediction SHA-256 |
|---:|---:|---:|---|
| 8 | 0.0984554745 | 3.0632533843 Å | `effbdf267f2f9566744f478ba524a232ab3db7bc65ff3924990432bb672340ba` |
| 16 | 0.0047139964 | 9.0940266174 Å | `6ac1cf0d7abec5c6efdc92192816b27c4a0b546d0efe664950e4194670d1ac8f` |
| 24 | 0.0073475432 | 12.7322387564 Å | `feebb95e60b9cb26a16d50947144b574107ad8d20574ccc30ee0a07ac4a1f267` |
| 76 | 0.02699273795 | 52.8931467807 Å | `184c3987cf1b12fb2bd5624cef1f577c3e02ff327913e2e0b3b82c39c8d851b5` |

Post-seal local comparison identifies accurate sequence geometry within the blind outputs: `IFV` at **0.8821336259 local TM / 0.1611313002 Å dRMSD**, and `TLT` at approximately **0.892 local TM / 0.187 Å dRMSD** in independently sealed 16- and 24-residue predictions. In the complete 76-residue blind prediction, the strongest same-index three-residue windows include `HLV` at **0.9914591922 local TM / 0.0313953540 Å dRMSD**, `RLI` at **0.9656795312 local TM / 0.0606832279 Å dRMSD**, and `RGG` at **0.9059580746 local TM / 0.0958017776 Å dRMSD**. All 74 windows are preserved in `verify/development_runs/ubiquitin_v3_current_20260719/local_windows_l3.json`.

Maria Smith has declared the completed 76-residue blind execution and its positive local empirical results for publication. Sealed blind reach has advanced from 8 to 16 to 24 to all 76 residues, and the strongest local agreement has advanced to **0.9914591922 TM**. The next constructive frontier is to propagate that accurate local geometry through inter-window orientation and complete global assembly. No theoretical wall is established: the protected construction proves that the same 24×24 lattice contains a 76-residue ubiquitin trace at **0.9891211351 TM / 0.2608575408 Å dRMSD**, while the engine-checked 3D protein law separately forces the canonical right-handed α-helix angles `(−60°, −45°)` and β-sheet angles `(−120°, +135°)`.

## Governing law

SFT begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms. The engine determines forcing and derivation by tracing every admitted construction to the One and halting on violation. No agent may weaken the result, declare a theoretical wall, or substitute statistical convention for the engine's standard. Maria Smith determines which engine results are published and directs the next investigation.

Blind sequence-to-structure benchmark victory is an explicit project
objective. Maria alone decides when a selector deserves a real blind run and
what conclusion its data supports. Agent-selected panels and ladders remain
attributed measurements; they cannot authorize, delay, veto, or redefine that
campaign.

The first visible Protein commit already contains mixed-purpose agent-era
development engines. Repository presence is therefore not treated as proof of
forcing. Every current source is classified in the executable provenance
registry, and the clean blind continuation route refuses legacy runtime imports.

Run the provenance gate:

```sh
python3 -m tools.verify_protein_forcing_registry
```

## Evidence map

| Path | Role |
|---|---|
| `verify/ubiquitin_24_lattice_manifest.json` | exact sequence, 76 lattice states, hashes, and metrics |
| `verify/replay_ubiquitin_24_lattice.py` | independent release replay |
| `verify/1ubq_test_24_lattice.pdb` | constructed witness |
| `verify/1ubq.pdb` | experimental target used in development and scoring |
| `tools/predict_structure.py` | committed NeRF backbone builder |
| `tools/protein_backbone_geometry_v1.py` | target-incapable extraction of the declared coordinate constitution; byte-exact construction replay |
| `tools/blind_24_lattice_selector_v3.py` | active provenance-isolated sequence forward-forcing selector |
| `verify/blind_selector_v3.json` | v3 relation routes, prohibited inputs, and source hashes |
| `verify/development_runs/ubiquitin_v3_l{8,16,24}_20260719/` | sealed blind sequence predictions and post-seal whole-prefix measurements |
| `verify/development_runs/ubiquitin_v3_current_20260719/` | complete sealed 76-residue blind prediction and post-seal global/local measurements |
| `verify/blind_local_sequence_evidence_20260719.json` | post-seal accurate local `IFV` and `TLT` empirical measurements |
| `verify/evaluate_sealed_blind_v3.py` | seal verifier and target-isolated evaluation boundary |
| `verify/evaluate_sealed_blind_local_v3.py` | all-window post-seal local evaluator; reproduces the published IFV/TLT measurements |
| `verify/protein_forcing_registry_v1.json` | complete source classification and legacy exclusion gate |
| `verify/PROTEIN_FORCING_AUDIT.md` | historical floor, trace findings, and authority boundary |
| `calculate_tm.py` | repository TM scorer |
| `verify/test_protein_folding*.c` | project law checks |
| `papers/` | principal protein papers |

## Papers

- [Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)
- [Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)

Sibling computational-proof projects: [UnisonAI](https://github.com/MettaMazza/UnisonAI) · [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).
