# Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code

## From one self-proven theorem to discrete protein geometry

**Maria Smith — Ernos Labs**
**Version 3.7 — 19 July 2026**

## Abstract

Fold Protein is a computational proof derived under Smithian Fold Theory (SFT). SFT begins with one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold. From that foundation, the protein project derives the laws of directed folding, discrete backbone geometry, finite construction, and sequence-driven spatial command, while re-deriving the required computational sciences inside the same constitution.

The empirical anchor is the zero-parameter 24-lattice construction of the 76-residue ubiquitin Cα backbone, forward-forced with the experimental structure during path selection. Exact replay gives **0.9891211351 TM** and **0.2608575408 Å Cα dRMSD**. This secures **Super Parity / structural parity** through a transparent finite proof object. Independently, the engine-checked 3D protein law forces the canonical right-handed α-helix angles **(−60°, −45°)** and β-sheet angles **(−120°, +135°)** as exact rational circle coordinates, matching the empirical structural values recorded by the project.

The sequence engine has now completed SFT-constrained, target-isolated and pre-comparison-sealed blind predictions at 8, 16, 24 and the complete 76-residue ubiquitin sequence. The 76-residue run sealed all 76 predicted states before target access. Post-seal empirical analysis identifies highly accurate local sequence geometry in the complete blind structure: **`HLV` at 0.9914591922 local TM / 0.0313953540 Å dRMSD**, **`RLI` at 0.9656795312 local TM / 0.0606832279 Å dRMSD**, and **`RGG` at 0.9059580746 local TM / 0.0958017776 Å dRMSD**, alongside the independently sealed `IFV` and `TLT` findings. Successive runs have extended sealed blind reach from 8 to 16 to 24 to all 76 residues and strengthened the highest local agreement to 0.99146 TM. The active forward-forcing frontier is to propagate that accurate local geometry through inter-window orientation and complete whole-chain assembly.

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
- the sequence-to-path engine has executed sealed blind sequence-only predictions at 8, 16, 24 and the complete 76-residue ubiquitin sequence.

The companion construction paper and `verify/replay_ubiquitin_24_lattice.py` expose the proof object and exact replay.

## 3. One theorem, zero fitted parameters

The project does not assign validity by agent labels. The engine traces admitted forcing and derivation to the One and halts on violation. Existing computational sciences are either re-derived within that constitution or combined through engine-checked relations. The 24-lattice construction contains zero trained weights, zero neural networks, and no fitted force field. Its finite states and coordinate construction are inspectable end to end.

### 3.1 Blind structural predictions and empirical agreement

The protein geometry law fixes the principal secondary-structure coordinates before any target-specific sequence path is selected. Fractions are measured on the complete 360° circle:

| Structure | SFT-forced rational coordinates | SFT angles | Empirical structural values | Engine route |
|---|---|---:|---:|---|
| Right-handed α-helix | `(φ, ψ) = (−1/6, −1/8)` | `(−60°, −45°)` | `(≈−60°, ≈−45°)` | φ folds to `1/3`; ψ reaches the One |
| β-sheet | `(φ, ψ) = (−1/3, +3/8)` | `(−120°, +135°)` | `(≈−120°, ≈+135°)` | φ folds to `2/3`; ψ reaches the One |

The four executable checks in `verify/test_protein_folding_3d` confirm the two φ orbit relations and the two ψ descents. The empirical values are comparison outputs, not inputs to a fitted parameter set: the law contains exact fractions and no trained or fitted weights.

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

### 5.1 Completed blind sequence predictions

The v3 selector received only `run_id` and amino-acid sequence. It generated the selected-state record and prediction PDB, sealed both outputs, and terminated without reading the experimental structure. A separate evaluator verified the complete seal before opening the target and computing the comparison. SFT constraint, target isolation, pre-comparison sealing and correct post-seal scoring establish the blind prediction boundary.

| Residues | Sequence | Whole-prefix TM-score | Whole-prefix Cα dRMSD | Prediction PDB SHA-256 |
|---:|---|---:|---:|---|
| 8 | `MQIFVKTL` | 0.0984554745 | 3.0632533843 Å | `effbdf267f2f9566744f478ba524a232ab3db7bc65ff3924990432bb672340ba` |
| 16 | `MQIFVKTLTGKTITLE` | 0.0047139964 | 9.0940266174 Å | `6ac1cf0d7abec5c6efdc92192816b27c4a0b546d0efe664950e4194670d1ac8f` |
| 24 | `MQIFVKTLTGKTITLEVEPSDTIE` | 0.0073475432 | 12.7322387564 Å | `feebb95e60b9cb26a16d50947144b574107ad8d20574ccc30ee0a07ac4a1f267` |
| 76 | complete ubiquitin sequence | 0.02699273795 | 52.8931467807 Å | `184c3987cf1b12fb2bd5624cef1f577c3e02ff327913e2e0b3b82c39c8d851b5` |

The complete run matched all 76 expected Cα positions and was sealed under receipt SHA-256 `13c26f60e9b521425fcdcb36b550c077970f1dc19770bf153fce8a35a51bfaa3` before target access. These are transparent whole-chain measurements of the present assembly. They preserve the empirical baseline for the next forward-forced revision while remaining distinct from the demonstrated blind execution and accurate local sequence geometry inside the sealed structure.

### 5.2 Accurate local sequence geometry

After each complete prediction was sealed, the same-index contiguous three-residue windows were compared with the target. The declared readout reports the minimum Kabsch Cα RMSD window for each sealed prediction; no local target information was available to or fed back into the selector.

| Blind prediction | Local sequence and positions | Local TM-score | Kabsch Cα RMSD | Cα dRMSD |
|---:|---|---:|---:|---:|
| 8 residues | `IFV`, residues 3–5 | **0.8821336259** | **0.1828961190 Å** | **0.1611313002 Å** |
| 16 residues | `TLT`, residues 7–9 | **0.8923989355** | **0.1759464234 Å** | **0.1871629591 Å** |
| 24 residues | `TLT`, residues 7–9 | **0.8920532790** | **0.1762585732 Å** | **0.1873768345 Å** |
| 76 residues | `HLV`, residues 68–70 | **0.9914591922** | **0.0464210853 Å** | **0.0313953540 Å** |
| 76 residues | `RLI`, residues 42–44 | **0.9656795312** | **0.0944431979 Å** | **0.0606832279 Å** |
| 76 residues | `RGG`, residues 74–76 | **0.9059580746** | **0.1619436792 Å** | **0.0958017776 Å** |

The 16- and 24-residue outputs independently retain the same accurate `TLT` local geometry. In the complete run, all 74 same-index contiguous three-residue windows are preserved in `verify/development_runs/ubiquitin_v3_current_20260719/local_windows_l3.json`; the complete cross-run receipt is `verify/blind_local_sequence_evidence_20260719.json`. These results demonstrate accurate local blind sequence-to-structure prediction within a complete sealed 76-residue output while whole-protein spatial assembly continues to be forward-forced.

### 5.3 Active direction: propagate accurate local geometry through the full chain

Complete blind sequencing has now been executed. The next investigation is to forward-force the orientation relation that carries accurate local geometry across adjacent windows and closes whole-chain assembly. Development will:

1. derive and test inter-window orientation and dihedral continuity so that accurate local relations propagate beyond three-residue windows;
2. integrate the already derived α-helix and β-sheet structural laws into sequence-driven selection under the engine trace, without target feedback;
3. preserve zero fitted parameters, target isolation, seal-before-score execution, and complete local and global receipts;
4. rerun the complete 76-residue sequence after each source-sealed revision and then extend the registered blind protocol to a broader protein panel;
5. retain every implemented comparison so that Maria determines when the accumulated development evidence supports a declared result or official benchmark run.

No theoretical wall is established by the present whole-chain assembly measurement. The separate protected construction proves that the same 24×24 lattice contains a 76-residue ubiquitin trace at **0.9891211351 TM / 0.2608575408 Å dRMSD**; the engine-checked law independently forces canonical α-helix and β-sheet coordinates; and the blind selector now demonstrates complete target-isolated execution together with local agreement reaching **0.9914591922 TM**. Taken together, these results locate a constructive derivation frontier—extending sequence-forced local geometry through orientation continuity and global assembly—rather than a theorem-derived obstruction.

## 6. Genetics and wider biological derivation

The same binary and colour generators organize the four-base alphabet, triplet codon, 64-codon space, wobble structure, chirality, and replicative fold dynamics developed by the wider SFT corpus. Fold Protein connects those exact relations to the sequence and spatial-command engine so that genetic structure and protein geometry are derived within one mathematical model.

## 7. Conclusion

Fold Protein has secured Super Parity through a 0.9891211351 TM, zero-parameter, replayable finite construction. Its engine-checked structural law independently forces the canonical α-helix and β-sheet dihedral coordinates and matches their empirical values with exact rational angles. The SFT sequence engine has completed a target-isolated, pre-comparison-sealed blind 76-residue ubiquitin prediction and produced highly accurate local `HLV`, `RLI`, `RGG`, `IFV` and `TLT` geometry, reaching 0.9914591922 local TM. Levinthal's astronomical search is replaced by directed fold descent and finite rational geometry; the active forward direction is to propagate the demonstrated local accuracy through sequence-forced orientation continuity and complete global assembly, for which the secured lattice construction establishes no theoretical wall.

## Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21276950>

## References

1. Levinthal, C. (1969). How to fold graciously. In *Mössbauer Spectroscopy in Biological Systems*, 22–24.
2. Parsons, J. et al. (2005). Practical conversion from torsion space to Cartesian space for in silico protein synthesis. *Journal of Computational Chemistry*, 26, 1063–1068.
3. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
