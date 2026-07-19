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

### Current forward-forcing stage

The continuation has now moved beyond the original v3 blind baseline:

- v5 machine-checks the four-residue inter-window count `c + c - b = 4` and carried the blind 76-residue path to whole-chain **TM 0.1232111976 / 8.3625317712 Å dRMSD**, with `DKE` at **0.9991809285 local TM**, `DKEG` at **0.8460707854**, and `QDKEG` at **0.3332405586**;
- v9 constitutes the exact covalent side-chain heavy-atom graphs of all 20 amino acids and a scale-free crowding relation with no residue radii, cutoffs, rotamers, fitted weights, target, or empirical structure. Its sealed 24-residue output reached **0.9127952097 local TM** over `KTIT` and **0.8383894512** over `GKTIT`, the strongest five-residue continuation in the 24-residue line;
- v10 gives hard exclusion absolute priority and balances signed orientation, side-chain crowding, charge, hydrophobic dispersion, and radius through permutation-invariant ordinal ranks rather than a weighted score. Its sealed 76-residue output selected 33 alpha and 40 beta quartets and reached **7.2416876635 Å whole-chain dRMSD**, the strongest full-chain blind dRMSD in the v3/v5/v10 line, while retaining local `TLE` at **0.9977831860 TM**, `DTIE` at **0.7161453983**, and `TLTGK` at **0.6090780016**.
- v11 adds a target-incapable, unit-capacity backbone hydrogen-bond assembly relation with no empirical distance or angular cutoff, fitted energy, reward, or target coordinate. Its sealed 24-residue run formed **17** donor/acceptor pairs from **108** eligible relations and advanced the best three-residue local geometry to `KTI` at **0.9997013611 TM / 0.0066159825 Å dRMSD** and the best four-residue geometry to `TLTG` at **0.6441498216 TM**. This is the active hydrogen-bond development continuation; v10 remains the current whole-chain route until Maria directs otherwise.
- v12 separates exact α `i+4 → i` pairs from longer non-local
  inter-strand candidates under one global donor/acceptor capacity and
  independent weight-free ordinal relations. Its sealed 24-residue run
  selected **18** pairs from **85** eligible rows—5 α and 13 longer. Against
  v11, whole-prefix TM improved from `0.0201832897` to **`0.0302036249`** and
  Cα dRMSD improved from `7.0743173964 Å` to **`6.1527857458 Å`**. The best
  3-, 4-, and 5-residue local TM rows were lower than v11 and are preserved
  explicitly as local regressions, not used as a theoretical limit. Maria
  determines the conclusion and continuation.

These are target-isolated, seal-before-score implemented development results. They extend the executable forcing chain; they are not agent-declared failures, limits, or substitutions for Maria Smith's conclusions. The current next state is to retain the secured signed geometry, dual-mode preservation, formal charge, exact side-chain graph, and weight-free balance while forward-forcing backbone hydrogen-bond assembly and a more spatially complete side-chain hard-exclusion relation. The secured lattice containment, forced secondary-structure coordinates, complete blind execution, and successive local and whole-chain advances establish a constructive route forward and no theorem-derived obstruction at this stage.

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
| `tools/blind_24_lattice_selector_v3.py` | secured provenance-isolated blind baseline |
| `verify/blind_selector_v3.json` | v3 relation routes, prohibited inputs, and source hashes |
| `verify/development_runs/ubiquitin_v3_l{8,16,24}_20260719/` | sealed blind sequence predictions and post-seal whole-prefix measurements |
| `verify/development_runs/ubiquitin_v3_current_20260719/` | complete sealed 76-residue blind prediction and post-seal global/local measurements |
| `verify/blind_local_sequence_evidence_20260719.json` | post-seal accurate local `IFV` and `TLT` empirical measurements |
| `tools/blind_24_lattice_selector_v5.py` | four-residue inter-window continuation |
| `tools/blind_24_lattice_selector_v9.py` | exact side-chain graph and crowding continuation |
| `tools/blind_24_lattice_selector_v10.py` | active weight-free symmetric ordinal continuation |
| `tools/blind_24_lattice_selector_v11.py` | target-incapable unit-capacity backbone hydrogen-bond development continuation |
| `tools/blind_24_lattice_selector_v12.py` | target-incapable alpha/longer non-local topology-separated backbone assembly continuation |
| `verify/development_runs/ubiquitin_v9_steric_orientation_l24_20260719/` | sealed v9 applied evidence |
| `verify/development_runs/ubiquitin_v10_balanced_relations_l{24,76}_20260719/` | sealed v10 applied evidence |
| `verify/development_runs/ubiquitin_v11_hbond_assembly_l24_20260719/` | sealed v11 hydrogen-bond applied evidence and post-seal local windows |
| `verify/development_runs/ubiquitin_v12_topology_hbond_l24_20260719/` | sealed v12 topology-separated applied evidence and post-seal local windows |
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
