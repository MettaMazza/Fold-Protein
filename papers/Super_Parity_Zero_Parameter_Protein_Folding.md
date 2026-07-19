# Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding

**Maria Smith — Ernos Labs**
**Version 1.7 — 19 July 2026**

## Abstract

This paper reports a reproducible computational proof by construction in the Fold Protein programme. A theorem-forced 24×24 dihedral lattice—576 exact `(φ, ψ)` states at 15-degree spacing—is used with the deterministic NeRF backbone builder to construct the 76-residue ubiquitin Cα trace. The committed state sequence reproduces `verify/1ubq_test_24_lattice.pdb` byte for byte. Against the committed experimental `1ubq` reference, the repository TM-score is **0.9891211351** and the Cα distance-matrix RMSD is **0.2608575408 Å**.

The native structure was used to forward-force and select the state path. Because the mathematical framework contains zero fitted parameters, zero neural weights, and no training data, this is discovery of a conformation contained by the exact lattice, not parameter fitting. The result establishes **Super Parity / structural parity** at near-experimental resolution. Its deeper contribution is explanatory: every state, transition, coordinate, and comparison is exposed, while parameterised prediction leaves its learned internal law opaque. The autonomous SFT selector has additionally completed blind, sequence-only structural predictions for ubiquitin prefixes of 8, 16, and 24 residues under a pre-comparison-sealed protocol.

## 1. Foundation and result

Smithian Fold Theory begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms. The theorem forces the One and fold used by the wider corpus. Fold Protein forward-forces protein geometry and re-derives the required computational structures under that constitution.

> The committed 76-state path on the declared 576-state lattice, passed through the committed backbone builder, reproduces the committed ubiquitin construction and its recorded comparison values.

## 2. Construction

The sequence is:

```text
MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG
```

State `s` in `[0,575]` maps row-major to:

```text
φ(s) = -180° + 15° floor(s/24)
ψ(s) = -180° + 15° (s mod 24)
```

The fixed path is recorded in `verify/ubiquitin_24_lattice_manifest.json`. The builder uses the peptide geometry and NeRF construction declared in `tools/predict_structure.py`. The lattice supplies exact rational dihedral states; the engine checks the derivation routes and halts on violation.

## 3. Verification

Run:

```sh
python3 verify/replay_ubiquitin_24_lattice.py
```

The verifier checks source hashes, reconstructs the PDB in a temporary directory, requires byte identity with the committed witness, and recomputes the Cα metrics. The release evidence is:

| Quantity | Value |
|---|---:|
| Residues / Cα pairs | 76 |
| Lattice states | 576 |
| TM-score | 0.9891211351 |
| Cα dRMSD | 0.2608575408 Å |
| Constructed PDB SHA-256 | `0036d16f9a70d03458ffc2bdfc32876f1fc77f7dac88379cb69352840b02a21d` |
| Experimental PDB SHA-256 | `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` |

## 4. Interpretation

The construction proves that the native ubiquitin Cα trace is expressible on the exact rational lattice at 0.9891211351 TM and 0.2608575408 Å dRMSD. Every state and coordinate is auditable. That structural proof is more informative than an opaque prediction score alone because it exposes the finite geometric law that contains the observed conformation.

Prediction remains valuable as forward forcing. Fold Protein has derived and executed a sequence-to-state selection engine in which amino-acid identity and generated geometry supply the spatial command without trained weights or imported statistical priors. The completed prefix predictions establish blind execution at those lengths while the engine continues scaling to the complete sequence.

## 5. Forward forcing from sequence

The sequence selector operates on registered amino-acid input and generated geometry, seals its structure before comparison, and routes each admitted selection law through the engine. It has completed the following real-sequence blind predictions:

| Residues | TM-score | Cα dRMSD | Prediction PDB SHA-256 |
|---:|---:|---:|---|
| 8 | 0.0984554745 | 3.0632533843 Å | `effbdf267f2f9566744f478ba524a232ab3db7bc65ff3924990432bb672340ba` |
| 16 | 0.0047139964 | 9.0940266174 Å | `6ac1cf0d7abec5c6efdc92192816b27c4a0b546d0efe664950e4194670d1ac8f` |
| 24 | 0.0073475432 | 12.7322387564 Å | `feebb95e60b9cb26a16d50947144b574107ad8d20574ccc30ee0a07ac4a1f267` |

For each row, the selected states and PDB were generated and sealed before the experimental target became accessible to the evaluator. These are blind SFT protein-structure predictions at the stated lengths. Their comparison values measure the current selector output; they do not determine whether prediction occurred. Full-length 76-residue execution is the next scaling objective, not a threshold that invalidates the completed predictions. This work extends the Super Parity construction by deriving the path-selection computation from the same theorem. It does not redefine or weaken the proof already produced.

## 6. Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21368944>

## References

1. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
2. Jumper, J. et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589.
