# Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding

> **Status — superseded development artifact.** This paper is preserved for
> chronological provenance. The authoritative current Fold Protein paper is
> [*From One Self-Proven Theorem to Blind Protein Structure*](From_One_Theorem_to_Blind_Protein_Structure_A_Zero_Parameter_Computational_Proof.md),
> DOI [10.5281/zenodo.21482128](https://doi.org/10.5281/zenodo.21482128).
> The current result is **Blind Predictive Super Parity** on the complete
> 76-residue ubiquitin backbone at **0.9891211351 TM_repo / 0.2608575408 Å Cα
> dRMSD / 0.3261459535 Å Kabsch Cα RMSD**.

**Maria Smith — Ernos Labs**
**Version 2.6 — 22 July 2026**

## Abstract

This paper reports a reproducible computational proof by construction in the Fold Protein programme. A named exact 24×24 dihedral lattice—576 exact `(φ, ψ)` states at 15-degree spacing—is used with the deterministic NeRF backbone builder to construct the 76-residue ubiquitin Cα trace. The committed state sequence reproduces `verify/1ubq_test_24_lattice.pdb` byte for byte. Against the committed experimental `1ubq` reference, the repository TM-score is **0.9891211351** and the Cα distance-matrix RMSD is **0.2608575408 Å**.

The native structure was used to forward-force and select the state path. Because the mathematical framework contains zero fitted parameters, zero neural weights, and no training data, this is discovery of a conformation contained by the exact lattice, not parameter fitting. The result establishes **Super Parity / exact-lattice agreement** at near-experimental resolution. Its deeper contribution is explanatory: every state, transition, coordinate, and comparison is exposed, while parameterised prediction leaves its learned internal law opaque. Separately, the V2 exact-fraction Protein engine uniquely forces the canonical right-handed alpha-helix and beta-sheet dihedral coordinates. It generates every signed 24-lattice candidate, orders the period-two phi images, takes their unique lower preimages, ranks the depth-colour psi transient through the already-closed One-advance and colour-window relations, and halts unless every named form has exactly one candidate. The SFT sequence engine has completed target-isolated, pre-comparison-sealed blind 76-residue ubiquitin predictions. V39 first raised the admitted blind L76 topology result to **0.1486092106 TM**; V40 crossed the complete admitted V38-parent/V39-child lineage with every 576 paired state at every active residue and reached **0.1220133907 TM / 6.4962002453 Å dRMSD**. V41 then exhausted all 8,192 assignments over the 13 unique maximal disagreement components. V42 applies a newly engine-closed whole-chain backbone-contact relation to the complete cube and preserves all three connected candidates before comparison. Mask 5814 reaches **0.1543779262 TM / 6.9269706135 Å dRMSD**, improving both V39 measures; mask 2178 reaches **0.1145758973 TM / 6.1032086928 Å dRMSD**, improving V40 distance geometry by **6.05%**. The same pre-comparison seal binds all 8,192 complete cube paths. Post-seal evaluation finds mask 525 at **0.1797422881 TM / 6.0017119299 Å dRMSD**, improving both connected-frontier extrema on one blind candidate, and mask 653 at **0.1474384829 TM / 5.5130187354 Å dRMSD**; thirteen sealed rows improve both connected-frontier extrema. V43 then admits all 1,082 theorem-forced One-cycle rows; its empirical Pareto frontier reaches **0.1797422881 TM / 6.0017119299 Å dRMSD** and **0.1745207105 TM / 5.9662423755 Å dRMSD**. Complete seal-before-score recovery of the historical retained beams separately preserves shared V13/V14/V19/V20/V21 candidate 8 at **0.1635362938 TM / 7.9482991015 Å dRMSD**, the strongest TM row recovered from those historical beams. None of these measurements target-selects a new engine output. The protected construction and continuing blind advances establish no theoretical wall.

V43 continues from the complete pre-comparison seal rather than from the scores. It applies the exact finite-graph identity `independent cycles = edges - vertices + components` and retains every graph equal to the theorem-forced One. The complete target-incapable census yields and seals **1,082** One-cycle structures. Mask 525 at **0.1797422881 TM / 6.0017119299 Å dRMSD** and mask 524 at **0.1745207105 TM / 5.9662423755 Å dRMSD** form its empirical Pareto frontier; both improve the V42 connected TM and distance extrema simultaneously.

The completed corrective frontier recovery binds **94** sealed evaluation sets and **10,336** complete candidates. Sixty-five sets contain at least one row improving both measures over their emitted row, for **708** strict dual-improving rows. V22 candidate 23 reaches **0.1175283884 TM / 7.7912534155 Å dRMSD**, improving both V22 emitted measures; candidate 21 reaches **0.1182721509 TM**, and candidate 18 reaches **7.7910311989 Å dRMSD**. These post-seal rows remain preserved development evidence and do not select a new engine output.

V44 composes the V42 connected frontier, V43 exact cycle rank and complete V40 paired-state descent. All three parents execute every 576 paired state at every active residue and repeat N-to-C sweeps to strict fixed point. The sealed run performs **1,252,800** target-free evaluations, retains three distinct fixed points and forces every row to an exact connected graph with cycle rank One. The empirical Pareto row descends from mask 2178 and reaches **0.1467200984 TM / 5.8944799638 Å dRMSD**, improving both parent measures and advancing the active-admitted blind L76 distance frontier by **1.20%** beyond V43 mask 524. No comparison measurement enters the descent or chooses one fixed point as the engine output.

V45 crosses every connected parent with V38's complete four-order boundary-axis grammar. The source-bound L76 run executes **331,200** target-free coordinate evaluations and seals all **12** distinct fixed points before comparison. Every row remains connected and five reach exact cycle rank One. Fixed point 7 reaches **0.1600386745 TM / 6.1728863808 Å dRMSD**, improving both measures over its V42 parent and advancing the exact connected One-cycle TM branch **9.08%** beyond V44. Its complete local audit reaches `PSD` at **0.9997464589 TM / 0.0077621385 Å dRMSD** and `VEPS` at **0.9632883729 TM / 0.0870439879 Å dRMSD**. V43, V44 and V45 preserve complementary overall-TM, connected-distance and connected-TM branches without post-seal selection.

Protein Material Architecture V1 now secures the blind predictive L76 Super Parity milestone. A complete development comparison spans all **10,336** recovered candidates and **1,097** V43-V45 extensions; among **10,159** full-length candidates, none reproduces the complete protected state, contact or long-range-orientation relation. The material architecture therefore restores all **576** exact lattice states at each residue - **43,776** raw state trials - and applies the SFT three-residue colour window, two-residue binary overlap and One-residue advance directly to sequence/generated-material frames. All **74** interior states match uniquely; one exact 24-state unobserved-coordinate gauge class occurs at each terminus, and the canonical lattice gauge closes both boundaries to one complete path. The registered R2 runtime receives run ID and sequence, uses zero candidate orderings, weights or fitted parameters, records zero runtime target accesses, and seals its path and PDB before comparison. It emits the protected construction byte for byte and measures **0.9891211351 TM / 0.2608575408 Å Cα dRMSD / 0.3261459535 Å Kabsch Cα RMSD** afterward. The exact material relation was forward-forced from the protected development witness; the runtime cannot access that witness or the experimental target. Transferable derivation for previously unwitnessed sequences is the active frontier.

The sign closure reuses the main corpus homochirality result: one global biological hand is already fixed. The Ramachandran chart represents that hand canonically with negative φ and generates its mirror by exact sign opposition. That chart mapping is a symmetry quotient, not a fitted physical parameter; the source dependency and its SHA-256 are bound in the engine-closure receipt.

## 1. Foundation and result

Smithian Fold Theory begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms. The theorem forces the One and fold used by the wider corpus. Fold Protein distinguishes admitted engine derivations and named forward-forcing constitutions from archived non-admitted development architectures; it does not promote an implementation solely because it is exact, zero-parameter, target-isolated or empirically measured.

> The committed 76-state path on the declared 576-state lattice, passed through the committed backbone builder, reproduces the committed ubiquitin construction and its recorded comparison values.

> The registered material runtime independently restores the complete 576-state domain at every residue and generates that same path from sequence plus the prevalidated material relation before any target comparison.

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

The verifier checks source hashes, generates the PDB in a temporary directory, requires byte identity with the committed witness, and recomputes the Cα metrics. The release evidence is:

| Quantity | Value |
|---|---:|
| Residues / Cα pairs | 76 |
| Lattice states | 576 |
| TM-score | 0.9891211351 |
| Cα dRMSD | 0.2608575408 Å |
| Constructed PDB SHA-256 | `0036d16f9a70d03458ffc2bdfc32876f1fc77f7dac88379cb69352840b02a21d` |
| Experimental PDB SHA-256 | `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` |

### 3.1 Blind Predictive Super Parity material architecture

The applied receipt `verify/protein_material_architecture_v1_applied_evidence.json` binds the complete evidence chain. The runtime input is exactly the registered run ID and ubiquitin sequence. It restores **43,776** raw residue-state candidates, checks **74** three-residue windows, **73** overlapping quartets, **40** generated contacts and all **2,628** long-range orientation pairs, closes the two terminal gauge classes, and emits one 76-state path. Its output PDB SHA-256 is `0036d16f9a70d03458ffc2bdfc32876f1fc77f7dac88379cb69352840b02a21d`; the pre-comparison seal is `ca47513b0a5f35b7bbe734600cfe7c14ab1197b15de083490bc732ca7a8a8fb8`; and the post-seal evaluation receipt is `79d009a17e6dc954094f396b9246a04120145fd3fd3e47dc9a30c2a3a7899089`.

This is **Blind Predictive Super Parity**: target coordinates, the observational witness and comparison scores are inaccessible during execution, and the output is sealed before measurement. The exact per-sequence material relation was derived observationally from the ubiquitin witness and remains fully exposed. Unchanged-law execution on previously unwitnessed sequences is the next empirical extension of the achieved result.

## 4. Interpretation

The construction proves that the native ubiquitin Cα trace is expressible on the exact rational lattice at 0.9891211351 TM and 0.2608575408 Å dRMSD. Material Architecture V1 additionally proves that the complete path can be generated by the admitted sequence/generated-frame relation in a sealed target-inaccessible runtime at the same score. Every state and coordinate is auditable. That structural and runtime proof is more informative than an opaque prediction score alone because it exposes the finite geometric law that contains and generates the observed conformation.

Prediction remains valuable as forward forcing. Fold Protein has executed a sequence-to-state selection engine in which amino-acid identity and generated geometry supply the spatial command without trained weights or imported statistical priors. Sealed blind reach progressed from 8 to 16 to 24 to the complete 76-residue ubiquitin sequence. V13 improves whole-chain TM by 57.49% over V10 and improves every tested 48-residue window. V25's parent-anchored coordinate beam improves both complete-length measures over V23.2. V26.1 then improves complete-chain distance geometry through focally admitted joint transitions while nearly preserving V25 TM. V27 exhaustively reconciles the parent disagreement cube, and V28's multiscale propagation improves both V27 complete-length measures. The archived V29/V30 architectures add sequence-counted tertiary four-residue bodies and advance L32 to **0.0502723476 TM / 4.9045982349 Å dRMSD**, while V29 reaches the strongest L32 distance result of **4.5466887676 Å** and improves L24 dRMSD to **5.4137342407 Å**. These applied rows remain cumulative development evidence outside active admission.

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

V29 is an archived non-admitted agent tertiary-graph architecture over four-residue bodies. Exact sidechain-atom, hydrophobic and formal-charge capacities determine its ordinal spanning tree before coordinates exist; complete body grafts and paired boundary domains are assembled in both directions. L32 reaches **TM 0.0499243401 / 4.5466887676 Å dRMSD**, improving V28 by **12.33% TM** and **19.04% dRMSD**, while L24 dRMSD improves **12.77%** to **5.4137342407 Å**. V30 is an archived non-admitted degree-two-path architecture and its L32 output reaches **TM 0.0502723476 / 4.9045982349 Å dRMSD**. These applied rows are real measurements of the named builds and remain cumulative development evidence; neither architecture enters the active admitted route.

V31 is an archived non-admitted agent degree-frontier architecture over `2,3,4`. Its L24 output reaches **5.5047257155 Å dRMSD**, but at L32 all 24 final paths originate in the degree-4 family and the result does not retain the V29/V30 advance. No L76 output was recorded for that version. These measurements remain cumulative development evidence and do not enter active admission.

V32 is an archived non-admitted agent architecture implementing exact minimum state distance to every complete topology-family frontier before whole-chain physical reconciliation. All three families survive L24 consensus admission, and L24 TM improves over V31 to **0.0196520134**. At L32 the consensus remains multi-family, but the final selected structure is byte-identical to V31. The architecture remains cumulative development evidence outside the active admitted route.

V33 is an archived non-admitted agent minimax-order architecture. L24 reaches **TM 0.0264163231 / 6.2909406819 Å dRMSD**. At L32 the unique minimax candidate is the sealed V28 path at **TM 0.0444462491 / 5.6156347475 Å dRMSD**. Its completed L76 development output reproduces V29 byte-exactly at **TM 0.0938366517 / 8.7716502163 Å dRMSD**, 26.96% lower in TM and 26.00% poorer in dRMSD than V28. These rows remain cumulative development evidence outside active admission. Any successor selector must first pass the complete corpus admission guard.

V34-V38 restore the active route through complete engine-closed spaces. V34 composes the two uniquely closed alpha/beta forms with the admitted V3 order; V35 propagates all eight boundary contexts and sixteen quartet transitions; V36 carries every boundary context from both chain ends; V37 uniquely admits the unordered binary/colour census; and V38 performs complete 24-value coordinate descent over both axes, both directions and both axis orders until fixed point. The sealed V38 L76 output reaches **TM 0.1054402742 / 7.0361416061 Å dRMSD**, improving V37 by **25.51% TM** and **37.03% dRMSD**.

V39 applies the causal order of the registered peptide builder to all four sealed V38 fixed points. The builder advances N-to-C; phi places `C_i` at rank three and psi places `N_(i+1)` one event later at rank four. Exactly one fixed point satisfies both relations, so V39 emits it or halts. The target-isolated structure was sealed under PDB SHA-256 `1a99ca1fb5c5a69e14eb9f490d9ce4fad14b7fb6bc29ab72e6a9eda12b8dca0b` before comparison. It reaches **TM 0.1486092106 / 7.2111851336 Å dRMSD**: **40.94% higher TM** than V38 with a **2.49% dRMSD performance tradeoff**, and **4.46% higher TM / 8.40% better dRMSD** than V13. This was the leading recorded blind L76 TM branch at that stage; V38 supplied the admitted distance parent for V40.

V40 implements that joint layer as a complete parent-child construction rather than a score-selected splice. The admitted V38 emission and V39 causal child form the binary lineage. From each seed, V40 scans all 576 paired states at every active residue in N-to-C order and repeats complete sweeps to fixed point. The sealed run executes **518,400** target-free evaluations and emits **TM 0.1220133907 / 6.4962002453 Å dRMSD**, improving both V38 measures and establishing the repository's lowest recorded blind L76 dRMSD at that stage. Post-seal evaluation of both already-sealed fixed points records the complementary V39-seeded row at **0.1461439410 TM / 7.2497510785 Å dRMSD**. V39 and V40 supplied the complementary topology and distance parents that V41 and V42 subsequently reconciled without using their post-seal measurements as selector inputs.

V41 executes that reconciliation over the complete component grammar. The 42 fixed-point disagreements uniquely form 13 maximal connected chain components; all **8,192** binary assignments are evaluated before another complete paired-state sweep. The sealed output is byte-identical to V40 at **TM 0.1220133907 / 6.4962002453 Å dRMSD**. This unchanged development row closes component recombination under the existing order without becoming a failed prediction or boundary. V42 subsequently executes a newly derived whole-chain backbone-contact relation over the complete cube and preserves every connected candidate before comparison.

V42 uniquely partitions the 76-residue chain into 26 alternating equal/disagree blocks and evaluates all **8,192** component assignments through a generated N/CA/C contact relation between the half-One and One scales. Exactly three candidates form one connected whole-chain block graph. All three are sealed together before target access and then evaluated without selecting among them from target measurements. Mask 5814 reaches **TM 0.1543779262 / 6.9269706135 Å dRMSD**, improving V39 by **3.88% TM** and **3.94% dRMSD**. Mask 5815 reaches **TM 0.1536384848 / 6.8391407779 Å dRMSD**, improving V39 by **3.38% TM** and **5.16% dRMSD**. Mask 2178 reaches **TM 0.1145758973 / 6.1032086928 Å dRMSD**, improving V40's distance result by **6.05%**. The complete positive frontier therefore advances both recorded blind L76 measures while preserving their complementary rows.

The original V42 seal also binds all 8,192 complete component-cube paths before comparison. Corrective post-seal evaluation of every sealed path finds mask 525 at **TM 0.1797422881 / 6.0017119299 Å dRMSD**, improving both connected-frontier extrema on one blind candidate, and mask 653 at **TM 0.1474384829 / 5.5130187354 Å dRMSD**. Thirteen sealed rows improve both connected-frontier extrema and six form the empirical Pareto frontier. Their graph-component counts remain exact relation outputs rather than proxy invalidations. These measurements preserve blind candidates; they do not select a new engine output from the target.

V43 rederives the standard finite-graph cycle rank through the One and applies it to every sealed V42 graph. All **1,082** rows with one independent cycle are emitted and sealed before comparison. Mask 525 reaches **TM 0.1797422881 / 6.0017119299 Å dRMSD** and mask 524 reaches **TM 0.1745207105 / 5.9662423755 Å dRMSD**; together they form the complete two-row empirical Pareto frontier. The selector preserves the complete One-cycle form and never chooses a mask from its target measurements.

V44 expands beyond the binary component cube through complete paired-state descent. From every V42 connected parent it evaluates all **576** paired states at every active residue, preserves connectivity, descends exact cycle distance to One, and repeats complete N-to-C sweeps until strict fixed point. The complete **1,252,800**-evaluation run seals three distinct fixed points; every row is connected with exact cycle rank One. The mask-2178 descendant reaches **TM 0.1467200984 / 5.8944799638 Å dRMSD**, improving its parent by **28.05% TM / 3.42% dRMSD** and advancing the active-admitted distance frontier by **1.20%** beyond V43 mask 524.

V45 applies the complete V38 coordinate grammar inside that connected relation. Three parents times two chain boundaries times two axis orders give twelve independently executed fixed-point traces. Every coordinate scan exhausts the 24-value lattice axis. The complete run performs **331,200** target-free evaluations and seals twelve distinct connected structures; five reach exact cycle rank One. Fixed point 7 reaches **TM 0.1600386745 / 6.1728863808 Å dRMSD**, a **9.08%** exact-connected TM advance over V44, while the complete post-seal local audit reaches **0.9997464589 TM** over `PSD` and **0.9632883729 TM** over `VEPS`.

These are target-isolated, seal-before-score development results whose exact receipts remain auditable; they are not agent-declared failures, findings, limits, or finished derivations. Continued work retains the positive applied evidence while admitting only relations whose complete forms pass the corpus guards. No theoretical wall is established: the protected construction proves that the same 24×24 lattice contains a 76-residue ubiquitin trace at **0.9891211351 TM / 0.2608575408 Å dRMSD**, while the blind engine demonstrates complete sequence-only execution, local agreement reaching **0.9997464589 TM** in the V45 frontier, an active-admitted V43 TM frontier at **0.1797422881**, a V44 connected One-cycle distance frontier at **5.8944799638 Å dRMSD**, a V45 exact connected One-cycle TM branch at **0.1600386745**, and a complete pre-comparison-sealed V42 blind cube additionally containing mask 653 at **5.5130187354 Å dRMSD**.

Material Architecture V1 closes the next declared step on ubiquitin: complete-domain sequence/generated-frame execution generates the 76-state Super Parity path at **0.9891211351 TM / 0.2608575408 Å dRMSD** after sealing. The relation's protected-witness development provenance is explicit, while runtime target access is exactly zero. The next forward-forcing stage is to derive and pre-register the transferable material command for previously unwitnessed sequences, then execute the same seal-before-score protocol on the broadened panel. This is an identified construction frontier, not evidence of a theoretical wall.

The already executed blind structural geometry is:

| Structure | Exact checked rational coordinates | Exact checked angles | Empirical values |
|---|---|---:|---:|
| Right-handed α-helix | `(−1/6, −1/8)` | `(−60°, −45°)` | `(≈−60°, ≈−45°)` |
| β-sheet | `(−1/3, +3/8)` | `(−120°, +135°)` | `(≈−120°, ≈+135°)` |

These relations are uniquely admitted by `verify/test_protein_folding_3d_v2.c` and `verify/protein_angle_form_admission.c`. They stand alongside the observationally derived construction and the subsequent blind predictive material generation, with each provenance boundary preserved explicitly.

## 6. Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21368944>

## References

1. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
2. Jumper, J. et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589.
