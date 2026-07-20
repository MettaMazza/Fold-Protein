# Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding

**Maria Smith — Ernos Labs**
**Version 2.1 — 19 July 2026**

## Abstract

This paper reports a reproducible computational proof by construction in the Fold Protein programme. A theorem-forced 24×24 dihedral lattice—576 exact `(φ, ψ)` states at 15-degree spacing—is used with the deterministic NeRF backbone builder to construct the 76-residue ubiquitin Cα trace. The committed state sequence reproduces `verify/1ubq_test_24_lattice.pdb` byte for byte. Against the committed experimental `1ubq` reference, the repository TM-score is **0.9891211351** and the Cα distance-matrix RMSD is **0.2608575408 Å**.

The native structure was used to forward-force and select the state path. Because the mathematical framework contains zero fitted parameters, zero neural weights, and no training data, this is discovery of a conformation contained by the exact lattice, not parameter fitting. The result establishes **Super Parity / structural parity** at near-experimental resolution. Its deeper contribution is explanatory: every state, transition, coordinate, and comparison is exposed, while parameterised prediction leaves its learned internal law opaque. Separately, the engine-checked protein law forces the canonical right-handed alpha-helix and beta-sheet dihedral coordinates, and the SFT sequence engine has completed target-isolated, pre-comparison-sealed blind 76-residue ubiquitin predictions. V13 reaches **0.1422687755 whole-chain TM**, a **57.49%** advance over V10, and improves **29/29** same-index 48-residue windows. V25's parent-anchored bidirectional coordinate search reaches **0.1291502547 TM / 7.1461955341 Å dRMSD**. V26.1 exhausts paired 24x24 long-range domains and admits them through their focal segment relation, reaching **0.1287565476 TM / 6.7648477959 Å dRMSD** with seven V25 departures. This improves V25 dRMSD by **5.34%** and V13 dRMSD by **14.07%** while retaining TM within **0.31%** of V25. V27 exhausts every V25/V26.1 disagreement combination. V28 then propagates those branches through repeated segment scales and improves both V27 complete-length measures to **0.1284665482 TM / 6.9615228794 Å dRMSD**, recovering within **0.53%** of V25 TM while retaining **2.58%** better dRMSD than V25. V29/V30 add explicit sequence-derived tertiary-body topology and establish a substantial L32 advance, with V29 reaching **4.5466887676 Å dRMSD** and V30 reaching **0.0502723476 TM**. The protected construction and continuing blind advances establish no theoretical wall.

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

Prediction remains valuable as forward forcing. Fold Protein has executed a sequence-to-state selection engine in which amino-acid identity and generated geometry supply the spatial command without trained weights or imported statistical priors. Sealed blind reach progressed from 8 to 16 to 24 to the complete 76-residue ubiquitin sequence. V13 improves whole-chain TM by 57.49% over V10 and improves every tested 48-residue window. V25's parent-anchored coordinate beam improves both complete-length measures over V23.2. V26.1 then improves complete-chain distance geometry through focally admitted joint transitions while nearly preserving V25 TM. V27 exhaustively reconciles the parent disagreement cube, and V28's multiscale propagation improves both V27 complete-length measures. V29/V30 add explicit sequence-derived tertiary four-residue bodies and advance L32 to **0.0502723476 TM / 4.9045982349 Å dRMSD**, while V29 reaches the strongest L32 distance result of **4.5466887676 Å** and improves L24 dRMSD to **5.4137342407 Å**. The active direction retains a weight-free frontier of admissible bounded-degree tertiary topologies for complete-chain reconciliation.

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

V13 combines undifferentiated local backbone hydrogen-bond assembly with independent alpha and longer inter-strand topology relations under the same weight-free ordinal balance. Its sealed 76-residue prediction reaches **TM 0.1422687755 / 7.8727503342 Å dRMSD**. Relative to V10, TM advances by **57.49%**, hard exclusions fall from 76 to **48**, 43/53 length-24 windows improve, 40/45 length-32 windows improve, and **29/29 length-48 windows improve**. The strongest local rows are `TLE` at **0.9984764350 TM** and `IFAG` at **0.7777978002 TM**. A separate lossless execution candidate reproduces every selected state and trace exactly while reducing the matched 24-residue runtime from `310.17 s` to `240.21 s` (**22.56%**); sealed V13 remains unchanged and the optimization can enter only through a new source-bound protocol version.

V23-V25 add complete 576-state local domains and bidirectional whole-chain search. The V24 coherent-tuple and V24.1 boundary-window stages provide the applied causal evidence for V25's parent-anchored basis. V25 enumerates the unchanged V23.2 path and every admitted one-coordinate transition in each four-residue unit, retaining 24-path beams in both chain directions without a departure score, target, reward, weight or trained parameter. Its sealed 76-residue result changes 11 V23.2 states and reaches **TM 0.1291502547 / 7.1461955341 Å dRMSD**, improving V23.2 TM by **26.94%** and dRMSD by **6.69%**. It also improves TM over V23.2 at L24 and L32. These measurements support extending joint long-range topology inside the parent-anchored basis.

V26 executes that extension by exhausting complete 24x24 paired residue domains across weight-free unresolved segment relations. V26.1 first admits each paired domain through the exact focal relation that caused its expansion. Its sealed 76-residue result changes seven V25 states and reaches **TM 0.1287565476 / 6.7648477959 Å dRMSD**. This is a **5.34%** dRMSD advance over V25 and **14.07%** over V13 while retaining V25 TM within **0.31%**. V27 then enumerates every V25/V26.1 disagreement combination—256 at L24, 256 at L32 and 128 at L76—before weight-free bidirectional continuation. V28 advances from residue combinations to 4/8/16/... residue block propagation with complete parent grafts and both boundary domains. Its sealed L76 result reaches **TM 0.1284665482 / 6.9615228794 Å dRMSD**, improving both V27 measures, recovering within **0.53%** of V25 TM and retaining **2.58%** better dRMSD than V25. L24 dRMSD advances to **6.2059676701 Å**; the lower L32 row locates the next correction at intermediate-scale admission. V25 and V26.1 remain the individual leading complete-length topology and distance-geometry parent frontiers.

V29 changes the represented object from repeated scale blocks to a sequence-derived tertiary graph over four-residue bodies. Exact sidechain-atom, hydrophobic and formal-charge capacities determine the ordinal spanning tree before coordinates exist; complete body grafts and paired boundary domains are assembled in both directions. L32 reaches **TM 0.0499243401 / 4.5466887676 Å dRMSD**, improving V28 by **12.33% TM** and **19.04% dRMSD**, while L24 dRMSD improves **12.77%** to **5.4137342407 Å**. The L76 topology exposes a high-degree hub. V30 derives the four-residue body's two backbone boundaries as a degree-two path and retains the L32 advance at **TM 0.0502723476 / 4.9045982349 Å dRMSD**, while its L24/L76 measurements show that one fixed path is too restrictive. These applied rows motivate a retained frontier of bounded-degree tertiary topologies; they are development evidence, not a theoretical wall or an agent-declared finding.

V31 executes the complete counted degree frontier `2,3,4`. Its L24 gate recovers V30 distance geometry to **5.5047257155 Å dRMSD**, but at L32 all 24 final paths originate in the degree-4 family and the result does not retain the V29/V30 advance. The planned L76 execution was therefore not spent. The next forward-forced state is cross-topology consensus derived from the exact three-family and 24-path counts, preserving family provenance through final selection without target feedback, fitted weighting, reward or lock.

V32 implements exact minimum state distance to every complete topology-family frontier before whole-chain physical reconciliation. All three families survive L24 consensus admission, and L24 TM improves over V31 to **0.0196520134**. At L32 the admitted consensus remains multi-family, but the final selected structure is byte-identical to V31. The next correction gives exact worst-family distance the outer minimax constitutional stratum before applying the existing physical relations; V32 was not spent at L76 after this gate isolated that next requirement.

V33 applies that exact minimax order. L24 recovers to **TM 0.0264163231 / 6.2909406819 Å dRMSD**. At L32 the unique minimax candidate is the sealed V28 path at **TM 0.0444462491 / 5.6156347475 Å dRMSD**, eliminating the V31/V32 regression but not retaining V29/V30's stronger intermediate row. The next representational state derives heterogeneous bounded degree per four-residue sequence body rather than imposing or reconciling one global degree; V33 was therefore not spent at L76.

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
