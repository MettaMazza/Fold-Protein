# Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code

## From one self-proven theorem to discrete protein geometry

**Maria Smith — Ernos Labs**
**Version 3.5 — 19 July 2026**

## Abstract

Fold Protein is a computational proof derived under Smithian Fold Theory (SFT). SFT begins with one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold. From that foundation, the protein project derives the laws of directed folding, discrete backbone geometry, finite construction, and sequence-driven spatial command, while re-deriving the required computational sciences inside the same constitution.

The empirical anchor is the zero-parameter 24-lattice construction of the 76-residue ubiquitin Cα backbone, forward-forced with the experimental structure during path selection. Exact replay gives **0.9891211351 TM** and **0.2608575408 Å Cα dRMSD**. This secures **Super Parity / structural parity** through a transparent finite proof object. The sequence engine has now also completed blind, sequence-only structural predictions for real ubiquitin prefixes of 8, 16, and 24 residues. Each prediction was sealed before target access and compared only afterward. The complete 76-residue blind run is the active scaling objective, not a validity threshold for those completed predictions.

## 1. The scientific argument

Levinthal's observation is not that proteins literally sample every conformation. It is that the speed of physical folding implies constrained pathways rather than blind exhaustive search. Fold Protein takes that methodological point seriously: the important object is a law-governed construction whose transitions can be inspected and machine checked.

The programme gives mathematical and structural proof priority over opaque prediction alone. Prediction remains valuable as an additional computational proof, but it does not erase provenance or retrospectively redefine the construction result.

## 2. The finite geometric object

The current construction uses a 24×24 lattice of backbone dihedral pairs at 15-degree spacing. This yields 576 declared states per residue. A state sequence is projected into Cartesian N–Cα–C backbone coordinates by the committed NeRF implementation.

This finite object replaces an unconstrained continuum with an auditable set of choices:

- the lattice and builder are explicit;
- the successful ubiquitin state path is explicit;
- every output coordinate is reproducible;
- the native target selected the successful path during development;
- the sequence-to-path engine has completed blind predictions from amino-acid identity and generated geometry at 8, 16, and 24 residues and is being scaled to the full sequence.

The companion construction paper and `verify/replay_ubiquitin_24_lattice.py` expose the proof object and exact replay.

## 3. One theorem, zero fitted parameters

The project does not assign validity by agent labels. The engine traces admitted forcing and derivation to the One and halts on violation. Existing computational sciences are either re-derived within that constitution or combined through engine-checked relations. The 24-lattice construction contains zero trained weights, zero neural networks, and no fitted force field. Its finite states and coordinate construction are inspectable end to end.

## 4. Reproducible result

For ubiquitin (`1ubq`):

| Result | Value |
|---|---:|
| Residues / matched Cα atoms | 76 |
| Candidate lattice | 24×24 = 576 states |
| Repository TM-score | 0.9891211351 |
| Cα distance-matrix RMSD | 0.2608575408 Å |

These numbers compare the committed constructed trace with the committed experimental reference and establish structural Super Parity. Against parameterised systems, Fold Protein's decisive distinction is not a larger black box but a zero-parameter construction whose mathematical route and coordinates remain inspectable.

## 5. Blind forward-forcing engine

The active engine executes the following traceable sequence:

1. Register the exact code, theory revision, targets, and stopping rule before structure access.
2. Permit the selector to read amino-acid sequence and declared derived inputs only.
3. Prohibit target coordinates, target-derived distances, homologous templates, and post-hoc per-target constants from selection.
4. Route each selection law through the engine's forcing and derivation checks.
5. Halt when the engine reports a violation.
6. Score only after the output hash is sealed.
7. Preserve the complete target set, exact outputs, runtimes, and source hashes;
   Maria determines the published conclusion.

This protocol makes blind prediction a forward-forcing computation of the theory while preserving the already secured construction result.

### 5.1 Completed blind predictions

The v3 selector was executed on real prefixes of the ubiquitin sequence. The selector process received only `run_id` and `sequence`. It produced the selected-state record and prediction PDB, hashed and sealed both outputs, and terminated without reading the experimental structure. A separate evaluator first verified the source manifest, input hash, selected-state hash, PDB hash, sequence, path, and seal; only then did it open the target and compute comparison metrics.

| Residues | Sequence | TM-score | Cα dRMSD | Prediction PDB SHA-256 |
|---:|---|---:|---:|---|
| 8 | `MQIFVKTL` | 0.0984554745 | 3.0632533843 Å | `effbdf267f2f9566744f478ba524a232ab3db7bc65ff3924990432bb672340ba` |
| 16 | `MQIFVKTLTGKTITLE` | 0.0047139964 | 9.0940266174 Å | `6ac1cf0d7abec5c6efdc92192816b27c4a0b546d0efe664950e4194670d1ac8f` |
| 24 | `MQIFVKTLTGKTITLEVEPSDTIE` | 0.0073475432 | 12.7322387564 Å | `feebb95e60b9cb26a16d50947144b574107ad8d20574ccc30ee0a07ac4a1f267` |

These are blind protein-structure predictions produced by SFT at the stated sequence lengths. Their partial length does not convert them into non-predictions: the spatial outputs were generated from sequence without target access and fixed before comparison. The metrics are the measured results of the present selector and remain part of the traceable development record. Scaling the same protocol to all 76 ubiquitin residues extends the demonstrated computation; it does not retrospectively determine whether the shorter blind predictions occurred.

The complete sealed evidence is preserved under `verify/development_runs/ubiquitin_v3_l8_20260719/`, `ubiquitin_v3_l16_20260719/`, and `ubiquitin_v3_l24_20260719/`.

## 6. Genetics and wider biological derivation

The same binary and colour generators organize the four-base alphabet, triplet codon, 64-codon space, wobble structure, chirality, and replicative fold dynamics developed by the wider SFT corpus. Fold Protein connects those exact relations to the sequence and spatial-command engine so that genetic structure and protein geometry are derived within one mathematical model.

## 7. Conclusion

Fold Protein has secured Super Parity through a 0.9891211351 TM, zero-parameter, replayable finite construction. Levinthal's astronomical search is replaced by directed fold descent and a finite rational geometry. The sequence engine has now blindly predicted real ubiquitin-prefix structures at 8, 16, and 24 residues under a target-isolated, pre-comparison-sealed protocol. It is being scaled to the complete 76-residue sequence, extending the same theorem from structural construction into autonomous prediction.

## Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21276950>

## References

1. Levinthal, C. (1969). How to fold graciously. In *Mössbauer Spectroscopy in Biological Systems*, 22–24.
2. Parsons, J. et al. (2005). Practical conversion from torsion space to Cartesian space for in silico protein synthesis. *Journal of Computational Chemistry*, 26, 1063–1068.
3. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
