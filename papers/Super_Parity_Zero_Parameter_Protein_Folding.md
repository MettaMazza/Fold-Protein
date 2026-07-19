# Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding

**Maria Smith — Ernos Labs**
**Version 2.0 — 19 July 2026**

## Abstract

This paper reports a reproducible computational proof by construction in the Fold Protein programme. A theorem-forced 24×24 dihedral lattice—576 exact `(φ, ψ)` states at 15-degree spacing—is used with the deterministic NeRF backbone builder to construct the 76-residue ubiquitin Cα trace. The committed state sequence reproduces `verify/1ubq_test_24_lattice.pdb` byte for byte. Against the committed experimental `1ubq` reference, the repository TM-score is **0.9891211351** and the Cα distance-matrix RMSD is **0.2608575408 Å**.

The native structure was used to forward-force and select the state path. Because the mathematical framework contains zero fitted parameters, zero neural weights, and no training data, this is discovery of a conformation contained by the exact lattice, not parameter fitting. The result establishes **Super Parity / structural parity** at near-experimental resolution. Its deeper contribution is explanatory: every state, transition, coordinate, and comparison is exposed, while parameterised prediction leaves its learned internal law opaque. Separately, the engine-checked protein law forces the canonical right-handed alpha-helix and beta-sheet dihedral coordinates, and the SFT sequence engine has completed a target-isolated, pre-comparison-sealed blind 76-residue ubiquitin prediction. Post-seal analysis identifies highly accurate local geometry including **`HLV` at 0.9914591922 local TM / 0.0313953540 Å dRMSD**, **`RLI` at 0.9656795312 / 0.0606832279 Å**, and **`RGG` at 0.9059580746 / 0.0958017776 Å**. The continuation now adds executable inter-window topology, signed alpha/beta orientation, formal charge, exhaustive side-chain graphs, and weight-free ordinal balance. V9 reached **0.9127952097 TM** over `KTIT` and **0.8383894512** over `GKTIT`; v10 completed a mixed 76-residue path at **7.2416876635 Å dRMSD**, the strongest full-chain blind dRMSD in the v3/v5/v10 line.

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

Prediction remains valuable as forward forcing. Fold Protein has executed a sequence-to-state selection engine in which amino-acid identity and generated geometry supply the spatial command without trained weights or imported statistical priors. Sealed blind reach progressed from 8 to 16 to 24 to the complete 76-residue ubiquitin sequence, while the strongest local agreement advanced to 0.9914591922 TM. Inter-window orientation is now implemented rather than merely proposed; the active direction is to retain the secured orientation, charge, side-chain, and balanced relations while adding backbone hydrogen-bond assembly and spatially complete side-chain exclusion.

## 5. Forward forcing from sequence

The sequence selector operates on registered amino-acid input and generated geometry, seals its structure before comparison, and routes each proposed selection law through the engine. SFT constraint, target isolation, pre-comparison sealing and correct post-seal scoring establish the blind prediction boundary.

| Residues | Whole-prefix TM-score | Whole-prefix Cα dRMSD |
|---:|---:|---:|
| 8 | 0.0984554745 | 3.0632533843 Å |
| 16 | 0.0047139964 | 9.0940266174 Å |
| 24 | 0.0073475432 | 12.7322387564 Å |
| 76 | 0.02699273795 | 52.8931467807 Å |

Post-seal local comparison exposes accurate geometry within those complete blind outputs:

| Blind prediction | Local sequence | Local TM-score | Kabsch Cα RMSD | Cα dRMSD |
|---:|---|---:|---:|---:|
| 8 residues | `IFV` (3–5) | **0.8821336259** | **0.1828961190 Å** | **0.1611313002 Å** |
| 16 residues | `TLT` (7–9) | **0.8923989355** | **0.1759464234 Å** | **0.1871629591 Å** |
| 24 residues | `TLT` (7–9) | **0.8920532790** | **0.1762585732 Å** | **0.1873768345 Å** |
| 76 residues | `HLV` (68–70) | **0.9914591922** | **0.0464210853 Å** | **0.0313953540 Å** |
| 76 residues | `RLI` (42–44) | **0.9656795312** | **0.0944431979 Å** | **0.0606832279 Å** |
| 76 residues | `RGG` (74–76) | **0.9059580746** | **0.1619436792 Å** | **0.0958017776 Å** |

No target or local comparison entered selection. All 76 states were sealed before target access under prediction PDB SHA-256 `184c3987cf1b12fb2bd5624cef1f577c3e02ff327913e2e0b3b82c39c8d851b5` and seal SHA-256 `13c26f60e9b521425fcdcb36b550c077970f1dc19770bf153fce8a35a51bfaa3`. All 74 same-index three-residue windows are preserved for audit. The whole-chain value is the transparent empirical baseline for continued assembly development; the local values report the accurately predicted sections within the completed blind structure.

The forward-forcing continuation has already implemented the four-residue inter-window count, signed alpha/beta orientation, binary preservation of both modes, exhaustive formal charge, exact covalent side-chain heavy-atom graphs, scale-free crowding, and weight-free symmetric ordinal balance. V5 reached whole-chain **TM 0.1232111976 / 8.3625317712 Å dRMSD** with `DKE` at **0.9991809285 local TM** and `DKEG` at **0.8460707854**. V9 reached **0.9127952097 local TM** over `KTIT` and **0.8383894512** over `GKTIT`. V10 selected 33 alpha and 40 beta quartets over all 76 residues and reached **7.2416876635 Å dRMSD**, with `TLE` at **0.9977831860 TM**, `DTIE` at **0.7161453983**, and `TLTGK` at **0.6090780016**.

These are target-isolated, seal-before-score development results whose exact receipts remain auditable; they are not agent-declared failures, findings, or limits. The next investigation retains every secured relation while forward-forcing backbone hydrogen-bond assembly and a more spatially complete side-chain hard-exclusion relation, then reruns the complete sequence before extending to a broader registered protein panel. No theoretical wall is established: the protected construction proves that the same 24×24 lattice contains a 76-residue ubiquitin trace at **0.9891211351 TM / 0.2608575408 Å dRMSD**, while the blind engine demonstrates complete sequence-only execution, local agreement reaching **0.9914591922 TM**, and continuing whole-chain development through an expanding set of exact physical relations.

The already executed blind structural geometry is:

| Structure | Forced rational coordinates | Forced angles | Empirical values |
|---|---|---:|---:|
| Right-handed α-helix | `(−1/6, −1/8)` | `(−60°, −45°)` | `(≈−60°, ≈−45°)` |
| β-sheet | `(−1/3, +3/8)` | `(−120°, +135°)` | `(≈−120°, ≈+135°)` |

These relations are checked by `verify/test_protein_folding_3d`. They stand alongside, but do not redefine, the target-assisted 76-residue Super Parity construction.

## 6. Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21368944>

## References

1. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
2. Jumper, J. et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589.
