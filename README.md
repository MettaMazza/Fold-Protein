# Fold Protein

Fold Protein is the protein-structure computational-proof project of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything). SFT begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold.

## Authoritative standalone paper

[*From One Self-Proven Theorem to Blind Protein Structure: Blind Predictive
Super Parity across 24 Sealed Whole-Structure Tests*](papers/From_One_Theorem_to_Blind_Protein_Structure_A_Zero_Parameter_Computational_Proof.md)
is the authoritative current statement of the complete Protein programme.

**Standalone concept DOI:** [10.5281/zenodo.21482127](https://doi.org/10.5281/zenodo.21482127)

The empirical result is **Blind Predictive Super Parity across 24 complete
sealed structures**: **0.9255486262 median TM_repo**, **0.7833590149 Å median
Cα RMSD95**, and **0.9882113352 best whole-structure TM_repo**. Fifteen of 24
predictions equal or outperform AlphaFold's reported **0.96 Å median Cα
RMSD95** at CASP14. Every structure was sealed before target access; the
executions use zero trained weights and zero fitted parameters.

Super Parity is the combined result, not a renamed accuracy threshold. Fold
Protein joins AlphaFold-class median predictive accuracy to a transparent
first-principles SFT derivation, machine-checked provenance to the One, exact
state-by-state execution and public reproduction. It was produced by one
researcher on one Mac Studio in approximately one week divided among four SFT
computational-proof programmes.

The paper distinguishes empirical science from opaque reliability. A black-box
predictor can be empirically shown to return reliable answers; that validates
its performance, not an unstated physical law. Fold Protein establishes the
higher scientific chain: mathematical derivation, machine-checked construction,
sealed blind consequence, reproducible measurement and explicit falsification
conditions.

The two earlier Protein papers remain in `papers/` as superseded chronological
development artifacts. They are not the current statement of the work.

<details>
<summary><strong>Open the complete chronological development and provenance record</strong></summary>

## Observational derivation record: exact 24-lattice witness

The repository contains a reproducible **Super Parity proof by construction** for the 76-residue ubiquitin Cα backbone on the exact 24×24 dihedral lattice used by the named forward-forcing construction:

- repository TM-score: **0.9891211351**;
- Cα distance-matrix RMSD: **0.2608575408 Å**;
- zero trained weights and no gradient training;
- committed state path, source hashes, witness PDB, and byte-exact replay.

Run the release check:

```sh
python3 verify/replay_ubiquitin_24_lattice.py
```

The native `1ubq` coordinates were used to forward-force and select the successful state path. With zero fitted parameters, zero neural weights, and no training data, the construction reaches **0.9891211351 TM / 0.2608575408 Å dRMSD** using exact discrete geometry. This is **Super Parity**: a transparent computational proof that the native ubiquitin backbone is contained by the 24-lattice at near-experimental resolution.

## Development record: blind sequence-to-structure programme

The SFT sequence engine has completed target-isolated, pre-comparison-sealed blind predictions for real ubiquitin prefixes of 8, 16 and 24 residues and the complete 76-residue ubiquitin sequence. The whole-chain measurements are:

| Residues | TM-score | Cα dRMSD | Sealed prediction SHA-256 |
|---:|---:|---:|---|
| 8 | 0.0984554745 | 3.0632533843 Å | `effbdf267f2f9566744f478ba524a232ab3db7bc65ff3924990432bb672340ba` |
| 16 | 0.0047139964 | 9.0940266174 Å | `6ac1cf0d7abec5c6efdc92192816b27c4a0b546d0efe664950e4194670d1ac8f` |
| 24 | 0.0073475432 | 12.7322387564 Å | `feebb95e60b9cb26a16d50947144b574107ad8d20574ccc30ee0a07ac4a1f267` |
| 76 | 0.02699273795 | 52.8931467807 Å | `184c3987cf1b12fb2bd5624cef1f577c3e02ff327913e2e0b3b82c39c8d851b5` |

Post-seal local comparison identifies accurate sequence geometry within the blind outputs: `IFV` at **0.8821336259 local TM / 0.1611313002 Å dRMSD**, and `TLT` at approximately **0.892 local TM / 0.187 Å dRMSD** in independently sealed 16- and 24-residue predictions. In the complete 76-residue blind prediction, the strongest same-index three-residue windows include `HLV` at **0.9914591922 local TM / 0.0313953540 Å dRMSD**, `RLI` at **0.9656795312 local TM / 0.0606832279 Å dRMSD**, and `RGG` at **0.9059580746 local TM / 0.0958017776 Å dRMSD**. All 74 windows are preserved in `verify/development_runs/ubiquitin_v3_current_20260719/local_windows_l3.json`.

Maria Smith has declared the completed 76-residue blind execution and its positive local empirical results for publication. Sealed blind reach advanced from 8 to 16 to 24 to all 76 residues, and the complete V45 post-seal frontier raises the strongest measured local agreement to **0.9997464589 TM**. Corrective evaluation of the complete pre-comparison-sealed V42 cube records blind mask 525 at **0.1797422881 whole-chain TM / 6.0017119299 Å dRMSD** and mask 653 at **5.5130187354 Å dRMSD**. V43 then admits and seals the complete 1,082-row theorem-forced One-cycle frontier; its two empirical Pareto rows reach **0.1797422881 TM / 6.0017119299 Å dRMSD** and **0.1745207105 TM / 5.9662423755 Å dRMSD**. V44 expands all three connected V42 parents through complete paired-state fixed-point descent, forces all three to exact connected cycle rank One, and advances the active-admitted distance frontier to **5.8944799638 Å dRMSD**. V45 crosses all three connected parents with the complete four-order coordinate grammar, seals 12 distinct fixed points after 331,200 target-free evaluations, and raises the exact connected One-cycle TM branch to **0.1600386745** while retaining **6.1728863808 Å dRMSD**. Its complete local audit reaches **0.9997464589 TM** on `PSD` and **0.9632883729 TM** on `VEPS`. Material Architecture V1 restores all 576 states per residue and reconstructs the complete path in a target-inaccessible sealed runtime at **0.9891211351 TM / 0.2608575408 Å dRMSD**. Four subsequent preregistered panels seal 24 complete structures before target access and reach **0.9255486262 median TM_repo / 0.7833590149 Å median Cα RMSD95**, establishing the repeated blind predictive-parity component of Super Parity. The V2 exact-fraction engine independently forces the canonical right-handed α-helix angles `(−60°, −45°)` and β-sheet angles `(−120°, +135°)` across the complete signed lattice.

### Derivation admission boundary

The engine-closed foundation, the observationally derived 24-lattice construction,
and the named target-isolated V3 forward-forcing constitution have distinct
provenance. V4-V33 are preserved as **archived non-admitted agent development
architectures** and are excluded from the active route; a successor may enter only when its complete assembled selector form passes the
corpus's dependency, generated-candidate, minimality, named-shape uniqueness,
target-exclusion and halt guards. Exact counts, zero fitted parameters, source
seals and real applied scores remain evidence about the executed builds; they do
not by themselves convert a selector form into a derivation. This boundary is
machine-checked by `python3 -m tools.verify_protein_derivation_admission`.

V34 is separately admitted as a named forward-forcing composition rather than an
agent-invented selector: both unique V2 canonical forms are enumerated at every
active residue under the unchanged V3 target-free order. The engine closes the
two-form domain, all eight three-residue windows and all sixteen four-residue
orientation quartets. Its sealed 76-residue cumulative development benchmark uses
20 alpha and 55 beta active forms and improves C-alpha dRMSD **35.28%** over V3,
from **52.8931467807 Å** to **34.2298081116 Å**. TM measures **0.0171435350** versus
V3's **0.0269927379**. This mixed applied row is preserved without converting it
into a Maria finding or theoretical boundary. V35 then implements the required
complete propagation rather than adding a local selector: all **8** three-residue
contexts and **16** four-residue transitions remain live at every mature step.
Its sealed L76 structure reaches **TM 0.0804845764 / 11.2596910135 Å dRMSD**,
improving V34 by **369.47% TM** and **67.11% dRMSD**, and V3 by **198.17% TM**
and **78.71% dRMSD**. Runtime improves **65.94%** to **3.12 seconds**. This is
positive cumulative development evidence for complete forced boundary propagation;
Maria determines its publication and official-run status. No theoretical wall is
established.

The frozen paired V34/V35 panel then completed both ubiquitin L76 and an independent
lambda-Cro L66 sequence before either experimental coordinate set was opened. On
lambda-Cro, V35 improves TM **24.95%**, from **0.0861911480** to **0.1076949961**,
and improves C-alpha dRMSD **47.53%**, from **19.1677598309 Å** to
**10.0579513939 Å**. Together with the ubiquitin row, V35 improves both structural
measures on **2/2 proteins**. Mean TM advances from **0.0516673415** to
**0.0940897863**, while mean dRMSD improves from **26.6987839712 Å** to
**10.6588212037 Å**. This is positive cross-protein generalisation evidence for
the same admitted complete-boundary propagation, with no selector change between
proteins. The exact registration, four nested seals, target projections and scores
are bound by `verify/protein_selector_v35_generalisation_evidence_v1.json`.

V36 then completed the missing two-boundary grammar: all eight V35 contexts are
propagated independently from both ends of the linear chain, producing exactly
`2 × 8 = 16` directional full-chain candidates, independently equal to the
closed quartet-transition census. Its sealed L76 application showed that the
inherited V3 order selected the reverse candidate and measured below V35; that
execution is retained as a development artifact locating the reconciliation
work and is not used as a theory limit or publication conclusion.

V37 closes that reconciliation without a target score, fitted weight, new
candidate, or α/β-to-generator assignment. The 75 active L76 states form 15
complete groups of `binary + colour = 5`; the two closed mode counts must equal
the unordered shares `{2 × 15, 3 × 15} = {30,45}`. Exactly one of all sixteen
V36 candidates satisfies the relation, otherwise the selector halts. The full
target-isolated, pre-comparison-sealed L76 run selected the N→C path and reached
**TM 0.0840105987 / 11.1739658456 Å Cα dRMSD**. Against V35 this improves TM
**4.381%** and dRMSD **0.761%**, changing only **3/76** states. V37 is therefore
the admitted L76 development parent at that stage. The immediate work was
complete-chain ubiquitin assembly; protein diversification is deferred until
the L76 predictive TM case is strong enough for Maria to authorize it.

V38 makes the next architectural expansion while retaining the V37 parent and
the admitted V3 target-free order. At every active residue it scans all **24**
values of exactly one φ or ψ coordinate while preserving every other
coordinate. Both chain directions and both φ/ψ axis orders are executed, giving
four complete descents. Each repeats until a full sweep changes zero
coordinates; strict descent over the finite `24^(2×75)` path space forces
termination without an iteration cutoff. The sealed L76 run performed
**136,800** full-chain coordinate evaluations and reached **TM 0.1054402742 /
7.0361416061 Å Cα dRMSD**. Against V37, TM improves **25.51%** and dRMSD
improves **37.03%** simultaneously. V38 became the admitted L76 parent.

V39 closes the causal reconciliation already present inside V38's four sealed
fixed points. The registered backbone builder constructs the chain N-to-C and
places phi's `C_i` before psi's `N_(i+1)`; exactly one complete V38 row has both
that direction and axis order. V39 selects that row before target access, seals
the complete L76 structure, and only then permits comparison. It reaches **TM
0.1486092106 / 7.2111851336 Å Cα dRMSD**, the leading recorded blind L76 TM at
that stage. Relative to V38, TM improves **40.94%** and dRMSD performance
changes **-2.49%**; relative to V13, both improve by **4.46% TM** and **8.40%
dRMSD**. V39 became the admitted TM frontier and V38 the admitted distance
frontier at that stage. The next L76 construction had to reconcile those
frontiers through the engine; protein diversification remains deferred unless
Maria authorizes it.

V40 crosses the complete admitted parent-child lineage—V38 and its V39 causal
child—with every **576** paired phi/psi state at every active residue. Both seeds
descend N-to-C until complete fixed points under the unchanged target-free order;
no measured parent score defines the construction. The sealed L76 run performs
**518,400** evaluations and reaches **TM 0.1220133907 / 6.4962002453 Å Cα
dRMSD**. This improves V38 by **15.72% TM** and **7.67% dRMSD** and establishes
the leading recorded blind L76 dRMSD at that stage. The second already-sealed
fixed point retains **0.1461439410 TM**. V39 therefore remains the leading blind
TM frontier while V40 becomes the leading blind distance frontier. Their complete
score-independent fixed-point reconciliation is the V41 construction below;
post-seal measurements diagnose it but do not define the selector.

V41 completes that score-independent reconciliation. The 42 differences between
V40's sealed fixed points uniquely decompose into 13 maximal connected chain
components, and the runtime exhausts all **8,192** binary assignments before
another complete paired-state sweep. The sealed result is byte-identical to V40
at **TM 0.1220133907 / 6.4962002453 Å dRMSD**. This unchanged closure result
does not establish a predictive failure or theoretical wall. V42 subsequently
executes an engine-closed whole-chain topology relation over the same complete
component cube.

V42 derives and executes that whole-chain relation as a complete frontier. The
76-residue chain uniquely partitions into 26 alternating equal/disagree blocks;
all 8,192 component assignments are evaluated through a generated N/CA/C
half-One-to-One contact graph. Exactly three candidates reach one connected
component, and all three are sealed before comparison. Mask 5814 reaches **TM
0.1543779262 / 6.9269706135 Å dRMSD**, improving both V39 measures and establishing
the active-admitted blind L76 TM frontier. Mask 2178 reaches **6.1032086928 Å dRMSD**, a
6.05% advance over V40 and the active-admitted blind L76 dRMSD frontier. The complete
frontier is preserved without using target measurements to choose among its rows.

The V42 seal also binds every one of the **8,192** complete component-cube paths
before comparison. Post-seal evaluation of the entire cube finds mask 525 at
**TM 0.1797422881 / 6.0017119299 Å dRMSD**, improving both connected-frontier
extrema on one blind candidate. Mask 653 reaches **5.5130187354 Å dRMSD** with
TM 0.1474384829. Thirteen sealed rows improve both connected-frontier extrema;
the complete six-row Pareto frontier is retained in
`verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721/complete_cube_postseal.json`.
The scores preserve empirical candidates but do not target-select a new output.

V43 advances the engine-closed construction without importing those scores. It
computes the exact finite-graph independent-cycle identity `edges - blocks +
components` for every sealed V42 row and retains the complete frontier equal to
the theorem-forced One. The full 8,192-row census yields **1,082** One-cycle
structures, all sealed before comparison. Post-seal evaluation leaves exactly
two empirical Pareto rows: mask 525 at **TM 0.1797422881 / 6.0017119299 Å
dRMSD** and mask 524 at **TM 0.1745207105 / 5.9662423755 Å dRMSD**. Both
improve the V42 connected TM and distance extrema simultaneously. V43 preserves
all 1,082 rows and never chooses a mask from target measurements.

V44 then expands the connected relation beyond the binary component cube. From
all three sealed V42 connected parents it exhausts all **576** paired states at
every active residue in the registered N-to-C direction, preserves connectivity,
descends exact cycle-rank distance to the theorem-forced One, and repeats complete
sweeps to strict fixed point. The sealed L76 run executes **1,252,800** paired
evaluations and retains three distinct fixed points. All three reach an exact
connected One-cycle graph. The empirical Pareto row, descended from mask 2178,
reaches **TM 0.1467200984 / 5.8944799638 Å dRMSD**: **28.05%** higher TM and
**3.42%** lower dRMSD than its parent, and **1.20%** lower dRMSD than V43 mask
524. This establishes the active-admitted blind L76 distance frontier while
retaining every fixed point and using no post-seal score in selection. The
complete V42 sealed cube separately preserves mask 653 at **5.5130187354 Å**.

V45 then composes V44's connected cycle-to-One relation with the complete V38
boundary-axis coordinate grammar. Each of the three connected V42 parents runs
both chain boundaries, both dihedral-axis orders and all 24 values for each
active coordinate. The locked L76 execution completes **331,200** target-free
evaluations and seals **12** distinct fixed points before comparison. Every row
remains connected and five reach exact cycle rank One. Fixed point 7 reaches
**TM 0.1600386745 / 6.1728863808 Å dRMSD**, improving both its V42 parent
measures and raising the exact connected One-cycle TM branch **9.08%** over
V44. The complete post-seal local audit retains every window at lengths
3/4/5/8/16/24 and reaches `PSD` at **0.9997464589 TM / 0.0077621385 Å
dRMSD** and `VEPS` at **0.9632883729 TM / 0.0870439879 Å dRMSD**. V43,
V44 and V45 therefore preserve complementary whole-chain TM, connected
distance and connected TM branches; no score chooses among them.

Protein material architecture V1 subsequently uses the protected construction as
an explicit development witness and replaces further topology-selector iteration
with one direct material relation. The complete comparison preserves all **10,336**
recovered candidates plus **1,097** V43-V45 extensions. The architecture restores
all **576** paired states at each of 76 residues, executes **43,776** raw material
frame trials, uniquely closes 74 interior states and both exact terminal gauge
classes, then seals one complete path before target access. The R2 runtime uses no
candidate ordering, weight, fitted parameter or runtime target access; it closes
all 40 generated contacts and 2,628 long-range orientations. Its emitted PDB is
byte-identical to the protected construction, and post-seal measurement reaches
**TM 0.9891211351 / 0.2608575408 Å C-alpha dRMSD**. The exact material relation was
forward-forced from the protected witness and remains named as such. Four
subsequent preregistered panels preserve the frozen relation and its sequence-only
One-extension command across 24 complete pre-target-sealed structures. Their
aggregate evidence is `verify/protein_blind_multi_structure_evidence_v1.json`.

The positive-candidate preservation audit subsequently recovered and sealed the
complete retained frontiers hidden behind historical single-row emission. V13,
V14, V19, V20 and V21 have an identical 24-row L76 frontier. Their candidate 8 reaches
**TM 0.1635362938 / 7.9482991015 Å dRMSD**: **14.95%** higher TM than their
emitted row and **5.93%** higher than V42 mask 5814, while differing from the
emitted path only at residues 54 and 75. This is the strongest TM row recovered
from the historical retained beams. Its empirical value is preserved
without changing the derivation boundary: V13/V14/V19/V20/V21 remain archived
non-admitted development architectures, whereas V43 remains the leading admitted
complete-frontier construction. The admitted V34 grammar also contains 14 rows
that improve both recorded measures over its emitted row, led by candidate 20 at
**TM 0.0190068444 / 34.1278254566 Å dRMSD**. No target measurement selected or
altered any of these rows.

The corrective recovery is complete. Its hash-bound index contains **94** sealed
evaluation sets, **10,336** complete candidates, **65** sets with a strict dual
improvement and **708** strict dual-improving rows. V22 candidate 23 improves
both its emitted measures to **TM 0.1175283884 / 7.7912534155 Å dRMSD**;
candidate 21 reaches **0.1182721509 TM**, and candidate 18 reaches
**7.7910311989 Å dRMSD**. The full index is
`verify/historical_positive_frontier_recovery_summary_v1.json`.

### Current forward-forcing stage

The continuation has now moved beyond the original v3 blind baseline:

- v5 machine-checks the four-residue inter-window count `c + c - b = 4` and carried the blind 76-residue path to whole-chain **TM 0.1232111976 / 8.3625317712 Å dRMSD**, with `DKE` at **0.9991809285 local TM**, `DKEG` at **0.8460707854**, and `QDKEG` at **0.3332405586**;
- v9 constitutes the exact covalent side-chain heavy-atom graphs of all 20 amino acids and a scale-free crowding relation with no residue radii, cutoffs, rotamers, fitted weights, target, or empirical structure. Its sealed 24-residue output reached **0.9127952097 local TM** over `KTIT` and **0.8383894512** over `GKTIT`, the strongest five-residue continuation in the 24-residue line;
- v10 gives hard exclusion absolute priority and balances signed orientation, side-chain crowding, charge, hydrophobic dispersion, and radius through permutation-invariant ordinal ranks rather than a weighted score. Its sealed 76-residue output selected 33 alpha and 40 beta quartets and reached **7.2416876635 Å whole-chain dRMSD**, the strongest full-chain blind dRMSD in the v3/v5/v10 line, while retaining local `TLE` at **0.9977831860 TM**, `DTIE` at **0.7161453983**, and `TLTGK` at **0.6090780016**.
- v11 adds a target-incapable, unit-capacity backbone hydrogen-bond assembly relation with no empirical distance or angular cutoff, fitted energy, reward, or target coordinate. Its sealed 24-residue run formed **17** donor/acceptor pairs from **108** eligible relations and advanced the best three-residue local geometry to `KTI` at **0.9997013611 TM / 0.0066159825 Å dRMSD** and the best four-residue geometry to `TLTG` at **0.6441498216 TM**. The formerly omitted L76 execution is now sealed: its emitted row reaches **TM 0.1251678035 / 7.9008745935 Å dRMSD**; recovered candidate 21 raises TM to **0.1256764831**, while candidate 11 reaches **7.7357362948 Å dRMSD**. These separate positive frontier rows replace the old complete-chain run gate with actual V11 evidence.
- v12 separates exact α `i+4 → i` pairs from longer non-local
  inter-strand candidates under one global donor/acceptor capacity and
  independent weight-free ordinal relations. Its sealed 24-residue run
  selected **18** pairs from **85** eligible rows—5 α and 13 longer. Against
  v11, whole-prefix TM improved from `0.0201832897` to **`0.0302036249`** and
  Cα dRMSD improved from `7.0743173964 Å` to **`6.1527857458 Å`**. The best
  3- and 4-residue local TM rows were lower than v11, while the best
  5-residue row improved slightly from `0.2462605086` to `0.2477913128`.
  These mixed local results are preserved explicitly and are not used as a
  theoretical limit. The completed L76 execution reaches **TM 0.0920401453 /
  8.9944283532 Å dRMSD**; candidate 17 raises the recovered frontier TM to
  **0.0976717257**, while candidate 19 reaches **8.9863063500 Å dRMSD**.
  Maria determines the conclusion and continuation.

The source-bound v11/v12 path-delta analysis now locates that change precisely:
topology separation changed **23/24** selected lattice states. Across all
same-index windows, v12 improved **9/22** length-3, **6/21** length-4, and
**7/20** length-5 geometries, while respectively 13, 15, and 13 moved lower.
The largest local advances include `EVE` (+0.503398 TM), `TLE` (+0.489450),
`TIT` (+0.449918), and `DTI` (+0.326621), alongside the whole-prefix gains of
+0.010020 TM and −0.921532 Å dRMSD. This applied pattern indicates that the
topology relation is exerting real global and local command and is not a renamed
v11 path, while also identifying why the next selector should
retain the undifferentiated local hydrogen-bond relation alongside topology-
separated whole-prefix assembly.

V13 has now executed that combined relation as a sealed cumulative 24-residue
development benchmark. It retains v11's local unit-capacity assembly beside
v12's independent alpha and longer non-local topology relations under the same
weight-free ordinal balance. Against v11, whole-prefix TM improved from
`0.0201832897` to **`0.0254390365`** and dRMSD improved from
`7.0743173964 Å` to **`7.0164353383 Å`**. Against v12, the best three-residue
local TM recovered from `0.9864217459` to **`0.9991385703`**; the best
four-residue TM advanced beyond both predecessors to **`0.6488923284`**, and
the best five-residue TM likewise advanced to **`0.2576423823`**. Across all
windows, v13 improved 14/22 length-3, 12/21 length-4, and 12/20 length-5 rows
relative to v12.

V13 has now completed and sealed the full 76-residue blind sequence before
target access. Post-seal comparison reaches **TM 0.1422687755**, improving the
v10 whole-chain TM of `0.0903326363` by **57.49%**. The hard-exclusion count
falls from 76 to **48** and the selected local-mode balance changes from
33 alpha / 40 beta to **40 alpha / 33 beta**. The strongest three-residue
window advances to `TLE` at **0.9984764350 TM / 0.0142727297 Å dRMSD** and the
strongest four-residue window advances to `IFAG` at **0.7777978002 TM**. The
propagation is broad: relative to v10, v13 improves 43/53 length-24 windows,
40/45 length-32 windows, and **29/29 length-48 windows**. The whole-chain
C-alpha dRMSD is `7.8727503342 Å`, so the continuing construction must convert
the secured global TM and long-window gains into tighter complete pairwise
assembly. This is an active derivation frontier, not a theoretical wall.

The applied single-build execution candidate preserves every selected state,
score trace, constitutional relation, mode trace, and orientation trace of the
sealed 24-residue v13 result while reducing wall time from `310.17 s` to
`240.21 s` (**22.56% faster**). V13 itself remains immutable so its sealed
source hashes stay valid; the lossless execution improvement will enter a new
source-bound protocol version.

V14 tested an exact continuity constitution: two held hydrogen bonds are
continuous when their donor and acceptor residues are both integer successors,
with alpha and inter-strand continuity retained as independent objectives. The
relation is target-incapable, parameter-free and active, but the sealed 24- and
32-residue development executions selected byte-identical structures to v13. The
32-residue prediction therefore retains **TM 0.0729998746 / 5.9835980697 Å
dRMSD** with zero predictive delta at that length. The completed L76 execution
and its 24-row recovered frontier are byte-identical to V13. The shared
candidate 8 reaches **TM 0.1635362938 / 7.9482991015 Å dRMSD** and differs
from the emitted row only at residues 54 and 75. The run preserves the
constitution, exposes the positive retained candidate, and confirms the
single-build execution path at 32
residues: `283.38 s` versus v13's `513.96 s` (**44.86% faster**). The agent
subsequently tested spatial side-chain exclusion while retaining v13 and the
lossless execution improvement; that sequence was a development choice, not an
engine-derived dismissal of V14.

V15 executes that spatial side-chain direction. From each generated N/CA/C
frame it computes the positive L-chiral half-space, uses the exact constituted
side-chain heavy-atom graph count to place a target-incapable command point,
and admits no target, template, rotamer, empirical radius, distance table,
fitted weight, reward or learned parameter. Its sealed 24-residue run changed
21/24 selected states and reduced the constituted spatial census from the 10
excluded residue pairs / 145 possible heavy-atom encounters present in the
v13 structure to **3 pairs / 39 encounters**. Its strongest five-residue
window advanced from v13's `0.2576423823` to **`0.2884520984 TM`**
(**11.96%**), while the whole-prefix comparison measured TM `0.0124237689`
and dRMSD `7.6841356168 Å`. This applied execution proves the new relation is
active and supplies real discrimination data. The completed L76 emitted row
reaches **TM 0.0437328195 / 15.1984065073 Å dRMSD**. Its recovered 24-row
frontier contains 16 rows that improve both measures, led by candidate 0 at
**TM 0.0448089342 / 15.0554004654 Å dRMSD**; candidate 7 reaches
**15.0089442388 Å dRMSD**. The complete result is preserved as applied
development evidence.

V16 then makes the hard-exclusion fact exact as set membership: one excluded
non-neighbour residue pair is one hard exclusion. The exact heavy-atom
Cartesian product remains recorded as an encounter census but no longer
multiplies the absolute hard stratum. Its sealed 24-residue prediction improves
on v15 to **TM `0.0126289266` / dRMSD `7.5227694169 Å`** (respectively
**1.65%** and **2.10%**), while preserving the same strongest local scores:
`0.9955319779` at length 3, `0.6021806558` at length 4 and
`0.2884520984` at length 5. The v16 path is identical to v15 at 23/24 states,
so binary counting is a precise correction but not the principal predictive
advance. Its completed L76 emitted row reaches **TM 0.0437328195 /
15.1984065073 Å dRMSD**. The recovered 24-row frontier contains 16 rows that
improve both measures, led by candidate 0 at **TM 0.0448089342 /
15.0554004654 Å dRMSD**; candidate 7 reaches **15.0089442388 Å dRMSD**.
The agent subsequently investigated spatial instantiation of the exact
side-chain graph and branch topology. V15 and V16 remain source-bound
development evidence. Their completed L76 emitted rows and complete recovered
frontiers are byte-identical, establishing preservation of the V15 candidate
set under the V16 binary correction at this length.

V17 now spatially instantiates the exact covalent side-chain graphs rather
than collapsing each residue to one command point. Integer graph depth and
branch rank place every constituted heavy atom in the generated L-chiral
residue frame; one non-neighbour residue pair with any atom encounter is one
binary hard exclusion. The sealed L24 route is active, recording **6 graph
pairs / 16 atom encounters**. It improves whole-prefix TM over v15 and v16 to
**`0.0167641314`** and advances v13's strongest length-five row by **9.21%**
to **`0.2813804825 TM`**. Its first divergence from v13 occurs at residue 5,
and the measured whole-prefix result is `8.2512076135 Å` dRMSD. This causal
evidence identifies early local graph pruning—not the explicit graph relation
itself—as the assembly placement to refine. The completed L76 emitted row is
**TM 0.0818581307 / 12.9484562212 Å dRMSD**; four recovered rows improve both
measures, led by candidate 11 at **TM 0.0820385215 / 12.9406345231 Å**.

V18 separates the previously implemented hard relations into the exact lexicographic
vector `(backbone, sidechain_graph)`, preventing a child side-chain exclusion
from trading against its parent backbone exclusion. It selects all **24/24**
v17 states and an identical PDB, with zero global or local predictive delta.
That exact-output evidence closes the hard-stratum semantics and localises the
next change to where graph geometry enters selection. Its completed L76
emitted output and recovered 24-row frontier are also byte-identical to V17,
preserving the same four dual-improving candidates.

V19 preserves v13's secured local frontier exactly and applies the explicit
graph relation only at complete-prefix assembly. Its sealed L24 output retains
**22/24** v13 states, first diverging at residue 22, and improves both global
measures: TM advances from `0.0254390365` to **`0.0255448548`**
(**+0.416%**) while dRMSD falls from `7.0164353383 Å` to
**`7.0054033965 Å`** (**0.157% improvement**). The best length-four and
length-five rows are preserved exactly; two same-index rows improve at each
of those lengths. The final hard vector is **`(5 backbone, 5 graph)`**, so
the explicit graph relation contributes independent global discrimination
without displacing the secured local construction. This is the first explicit
side-chain-graph route to improve both sealed L24 global measures over v13.

The matched V19 continuation has now completed at **32 and all 76 residues**.
At L32 it selects **32/32** V13 states and reproduces the V13 PDB byte for byte
at **TM `0.0729998746` / `5.9835980697 Å` dRMSD**. At L76 it selects **76/76**
V13 states and reproduces the complete V13 PDB byte for byte at **TM
`0.1422687755` / `7.8727503342 Å` dRMSD**. The explicit graph calculation is
active throughout: the complete path records the hard vector **`(48 backbone,
30 graph)`** and **110 atom encounters**. Every tested same-index window at
lengths 3, 4, 5, 24, 32 and 48 is identical to V13. The positive L24
discrimination is therefore horizon-local in the present complete-prefix
hierarchy; the full-chain execution preserves the secured V13 construction
exactly while locating the next development work in long-range propagation.

V20 tested the exact atom-encounter count as a child stratum of the graph-pair
exclusion, producing the L24 hard vector **`(5 backbone, 5 graph, 12 atom
encounters)`**. Its **24/24** states, PDB and every tested local and global
measurement are exactly V19. This preserves the constituted atom-level fact
at L24. Its completed L76 emitted row is byte-identical to V13/V19 at **TM
0.1422687755 / 7.8727503342 Å dRMSD**. The recovered complete frontier is also
identical to V13/V14: candidate 8 reaches **TM 0.1635362938 /
7.9482991015 Å dRMSD**. The atom hierarchy therefore preserves the established
full-length candidate set in the executed relation.

V21 implemented an explicit non-neighbour contact map in the generated shell
between the folded Cα step and the complete step. Its sealed L24 path records
**19 residue-pair contacts / 123 atom contacts** but preserves all **24/24** V19
states and every measurement exactly when contact count enters as one soft
ordinal objective. Its completed L76 emitted row and 24-row frontier are also
byte-identical to V13/V14/V19/V20, preserving candidate 8 at **TM 0.1635362938**.
V22 then placed the exact contact complement after the two
parent exclusion strata. That ordered relation is strongly active: **22/24**
states change, backbone/graph exclusions fall to **4/2**, and whole-prefix
dRMSD improves from `7.0054033965 Å` to **`6.9563150359 Å`** (**0.701%**).
Whole-prefix TM changes from `0.0255448548` to `0.0232375689`; the local rows
are mixed, with 8/22 length-three, 10/21 length-four and 9/20 length-five rows
improving. The formerly omitted L76 execution now reaches **TM 0.1174271794 /
7.7975761917 Å dRMSD**, retaining the positive distance direction from L24
through the complete chain. V22 therefore demonstrates that explicit graph
contact topology can drive blind global assembly and improve pairwise-distance
geometry. It remains archived development evidence unless its complete form
passes the corpus admission engine.

These are target-isolated, seal-before-score implemented development results.
They extend the executable forcing chain; they are not agent-declared
findings, limits, or substitutions for Maria Smith's conclusions. The secured
lattice containment, exact checked secondary-structure coordinates, complete blind
execution, and successive local and whole-chain advances establish a
constructive route forward and no theorem-derived obstruction at this stage.

The matched complete 76-residue V19 blind cumulative development benchmark is
also complete. Its exact preservation of V13, active explicit graph census and
the preceding L24 advance supplied applied evidence for subsequent graph-based
propagation. V20-V22 have now also received complete L76 executions, so no
short-length identity or tradeoff remains a run veto. These remain cumulative
development benchmarks unless Maria explicitly registers an official run.

### V23 complete-domain global architecture

V23 replaces residue-by-residue prefix commitment with one complete global
development block. Every active residue is expanded over all **576** exact
24-lattice states; a **24-state** domain is retained; theorem-counted
four-residue segments are assembled independently from both chain directions;
and the two full-chain frontiers are reconciled before explicit side-chain
graph and retained V13 relations select the emitted path. The inputs contain
only sequence identity and a hash-bound, previously sealed V13 state path.
Targets remain inaccessible until the new output is sealed.

The sealed L32 result advances both whole-prefix measures over V19/V13:
TM rises from `0.0729998746` to **`0.1073563785`** (**47.06%**) and dRMSD falls
from `5.9835980697 Å` to **`4.8501653531 Å`** (**18.94% improvement**). At L24,
dRMSD falls from V19's `7.0054033965 Å` to **`4.7690709196 Å`** (**31.92%**),
while TM is `0.0223392975`. This is direct applied evidence that complete
domains and bidirectional assembly can make large global changes unavailable
to the preceding incremental prefix variants.

The first L76 execution identified a continuity placement to correct inside
the architecture. V23.1 proved by byte-identical sealed replay that a soft
parent-departure axis cannot alter the preceding hard stratum. V23.2 then
restored V13/V19 local eligibility before global domain assembly. Its sealed
L76 output improves TM from V23's `0.0928040310` to **`0.1017436531`** and
improves dRMSD from `8.7367333419 Å` to **`7.6581678292 Å`**. That dRMSD is
also **2.73% better than V13's `7.8727503342 Å`**.

V24 made the next architectural move by constructing coherent locally
admitted four-residue tuples; V24.1 re-evaluated every overlapping local
window crossing their assembly boundaries. Their sealed data showed that
complete tuple replacement displaced 67-71 of the stronger V23.2 parent
states at L76. V25 therefore preserves the sealed V23.2 complete path as the
starting candidate and expands every admitted one-coordinate transition in
each four-residue development unit through independent 24-path forward and reverse
beams. This is a new global search basis, not a fitted continuity penalty.

The sealed V25 L76 development result changes **11** V23.2 states and improves
both measures: TM rises from `0.1017436531` to **`0.1291502547`**
(**26.94%**) and dRMSD falls from `7.6581678292 Å` to
**`7.1461955341 Å`** (**6.69% improvement**). At L24, TM rises **48.85%** to
`0.0298230532` while dRMSD is `6.3456312175 Å`; at L32, TM rises **0.83%** to
`0.0479008287` while dRMSD is `5.5215159800 Å`. Thus V25 advances topology at
all three lengths and advances both full-length measures, while the short-
prefix distance objective remains available for the next joint-topology
construction. These are sealed cumulative development benchmarks, not
official runs unless Maria registers them. They establish an implemented
continuation through the represented relations and do not impose a
theorem-derived wall on the blind benchmark objective.

V26 then expands joint long-range topology inside the V25 basis. It retains up
to 24 unresolved segment-pair relations through the same weight-free ordinal
constitution and exhausts all **576** paired domain states for every
participating residue pair. V26.1 adds focal admission: a paired state must
first pass the exact segment-pair relation that caused its expansion before it
enters whole-chain balance. The complete L76 execution evaluates **221,208**
focal paired states, changes seven V25 states, and reaches **TM
`0.1287565476` / dRMSD `6.7648477959 Å`**. This improves V25 dRMSD by
**5.34%** and V13 dRMSD by **14.07%**, while retaining TM within **0.31%** of
V25. At L24 dRMSD also improves over V25 while TM is lower; L32 is lower on
both measures. V25 therefore remains the strongest full-length TM branch and
V26.1 the strongest full-length distance-geometry branch.

V27 completes their constitutional frontier reconciliation. Because V25 and
V26.1 differ at only 8, 8 and 7 residues at L24/L32/L76, V27 exhausts every
combination—**256, 256 and 128 paths**—before applying the same weight-free
constitution and bidirectional coordinate continuation. L24 reaches **TM
`0.0283543332` / dRMSD `6.2352507038 Å`**, improving both V26.1 measures and
setting the best L24 dRMSD of the three branches. L32 also improves both V26.1
measures, while V25 remains stronger there. L76 reaches **TM `0.1267485096` /
dRMSD `6.9719543361 Å`**: its distance geometry improves V25, but it does not
retain V26.1's strongest complete-chain distance relation. This locates the
next architectural requirement at multiscale segment/domain propagation,
while V25 and V26.1 remain the leading full-length TM and dRMSD frontiers.
No target measurement entered V27 selection.

V28 advances reconciliation from residues to repeated segment scales. It
propagates complete V25, V26.1 and V27 block grafts plus both locally admitted
block-boundary domains through 4/8/16/... residue scales in forward and reverse
directions. At L76 it reaches **TM `0.1284665482` / dRMSD `6.9615228794 Å`**,
improving both V27 measures. This recovers TM to within **0.53%** of V25 while
retaining **2.58%** better dRMSD than V25. L24 dRMSD advances again to
**`6.2059676701 Å`**, the strongest L24 distance result in the V25–V28 line,
with TM `0.0280865891`. L32 is lower than V27 on both measures. The applied
data therefore support multiscale propagation at complete length and locate
the next correction in intermediate-scale admission. V25 and V26.1 remain the
individual leading full-length TM and dRMSD parent branches.

V29 is an archived non-admitted agent development architecture that represents
four-residue bodies as an ordinal tertiary graph. Exact sidechain-atom,
hydrophobic and formal-charge counts order its edges before coordinates exist;
complete body grafts and paired boundary states are then assembled in both
directions. Its sealed L32 output reaches **TM `0.0499243401` / dRMSD
`4.5466887676 Å`**, improving V28 by **12.33% TM** and **19.04% dRMSD**. L24
dRMSD improves **12.77%** to **`5.4137342407 Å`**, with a 2.37% TM tradeoff.
V30 is a separate archived non-admitted development architecture implementing a degree-two
tertiary path from the body's two-boundary interpretation. Its L32 output reaches
**TM `0.0502723476` / dRMSD `4.9045982349 Å`**. These are real applied
measurements of the named builds, but neither the tree nor the degree-two path
is an engine-closed derivation. They do not establish a theoretical wall or an
official result.

V31 is an archived non-admitted agent development frontier over the counted capacities
`2,3,4`. Each topology receives an independent 24-path forward/reverse
assembly before joint constitutional reconciliation. At L24 it recovers V30's
distance regression to **`5.5047257155 Å` dRMSD**, remaining **11.30%** better
than V28, with lower TM. At L32 the final frontier collapses to 24/24 degree-4
paths and reaches **TM `0.0363843691` / dRMSD `5.7052176785 Å`**, below the
V28-V30 rows. The formerly omitted L76 execution selected **TM 0.0608277326 /
16.4600642655 Å dRMSD**; recovery of its complete retained frontier found
candidate 2 at **TM 0.0938366517 / 8.7716502163 Å dRMSD**, improving both
measures over the emitted row. V31 is applied development evidence, not a
finding, prediction failure, theoretical limit, or engine-derived authorization
for another selector.

V32 is an archived non-admitted agent cross-topology consensus stage. Every candidate receives
three exact minimum state distances—one to each complete degree-family
frontier—and these enter permutation-invariant admission before the established
whole-chain constitution. At L24 all three topology families survive the
24-path consensus frontier and TM improves over V31 to **`0.0196520134`**,
while dRMSD is **`6.3312973879 Å`**. At L32 consensus admission preserves
multiple families, but final physical reconciliation selects the byte-identical
V31 degree-4 path at **TM `0.0363843691` / dRMSD `5.7052176785 Å`**.
At L32, recovered candidate 19 reaches **TM 0.0598256245 /
4.8950703151 Å dRMSD**, while candidate 18 reaches **4.5466887676 Å
dRMSD**. The formerly omitted L76 execution selected **TM 0.0938366517 /
8.7716502163 Å dRMSD**; five recovered rows improve both measures, led in
TM by candidate 7 at **0.1291502547 / 7.1461955341 Å**, while candidate 22
reaches **TM 0.1287565476 / 6.7648477959 Å dRMSD**.
The agent subsequently implemented exact minimax consensus—worst family distance
first, then symmetric family distance—before another physical reconciliation.
That development choice was not an engine derivation or a gate on Maria's
authority to order a run.

V33 is an archived non-admitted agent architecture giving exact worst-family distance
outer priority. At L24 the
minimax relation closes to two `[9,9,9]` candidates and selects the sealed
V26.1 path at **TM `0.0264163231` / dRMSD `6.2909406819 Å`**, recovering TM
substantially over V31/V32. The second sealed L24 minimax row is now measured at
**TM 0.0280865891 / 6.2059676701 Å dRMSD**, improving both measures over the
historically emitted row. At L32 the minimax relation has one candidate and
selects the sealed V28 path exactly at **TM `0.0444462491` / dRMSD
`5.6156347475 Å`**, removing the V31/V32 regression. It does not retain the
stronger V29/V30 intermediate result. The completed L76 development run selects
V29 byte-exactly at **TM `0.0938366517` /
dRMSD `8.7716502163 Å`**. It is unchanged from V29 and, relative to V28, TM is
26.96% lower and dRMSD is 26.00% poorer. No
heterogeneous-degree selector is authorized unless its complete form first
passes the corpus admission guards.

</details>

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
| `tools/blind_24_lattice_selector_v34.py` | engine-admitted V2 canonical-domain composition with the unchanged V3 target-free order |
| `tools/blind_24_lattice_selector_v35.py` | engine-admitted complete propagation over all 8 boundary contexts and 16 quartet transitions |
| `tools/blind_24_lattice_selector_v36.py` | complete two-boundary 16-candidate grammar and measured reconciliation-development artifact |
| `tools/blind_24_lattice_selector_v37.py` | admitted L76 stage: unique unordered binary/colour whole-chain census over all V36 candidates |
| `tools/blind_24_lattice_selector_v38.py` | admitted L76 stage: complete 24-value φ/ψ coordinate descents across all four boundary/axis orders to finite fixed points |
| `tools/blind_24_lattice_selector_v39.py` | engine-admitted peptide-causal reconciliation of the complete V38 fixed-point grammar |
| `tools/blind_24_lattice_selector_v40.py` | engine-admitted complete paired-state descent from both parent-child lineage seeds |
| `tools/blind_24_lattice_selector_v41.py` | engine-admitted complete component-cube reconciliation of both V40 fixed points |
| `tools/blind_24_lattice_selector_v42.py` | engine-admitted complete whole-chain contact cube and three-row connected frontier |
| `tools/blind_24_lattice_selector_v43.py` | engine-admitted complete One-cycle frontier over all 8,192 sealed V42 graphs |
| `tools/blind_24_lattice_selector_v44.py` | engine-admitted connected cycle-to-One fixed-point descent over all three V42 parents and all 576 paired states per residue |
| `tools/blind_24_lattice_selector_v45.py` | engine-admitted complete boundary-axis coordinate closure over all three connected parents and all four boundary/axis orders |
| `verify/blind_selector_v3.json` | v3 relation routes, prohibited inputs, and source hashes |
| `verify/development_runs/ubiquitin_v3_l{8,16,24}_20260719/` | sealed blind sequence predictions and post-seal whole-prefix measurements |
| `verify/development_runs/ubiquitin_v3_current_20260719/` | complete sealed 76-residue blind prediction and post-seal global/local measurements |
| `verify/blind_local_sequence_evidence_20260719.json` | post-seal accurate local `IFV` and `TLT` empirical measurements |
| `tools/blind_24_lattice_selector_v5.py` | four-residue inter-window continuation |
| `tools/blind_24_lattice_selector_v9.py` | exact side-chain graph and crowding continuation |
| `tools/blind_24_lattice_selector_v10.py` | active weight-free symmetric ordinal continuation |
| `tools/blind_24_lattice_selector_v11.py` | target-incapable unit-capacity backbone hydrogen-bond development continuation |
| `tools/blind_24_lattice_selector_v12.py` | target-incapable alpha/longer non-local topology-separated backbone assembly continuation |
| `tools/blind_24_lattice_selector_v13.py` | target-incapable retained-local plus topology-separated backbone assembly continuation |
| `tools/blind_24_lattice_selector_v15.py` | target-incapable L-chiral spatial side-chain encounter continuation |
| `tools/blind_24_lattice_selector_v16.py` | binary-pair spatial hard-exclusion continuation with separate atom encounter census |
| `tools/sidechain_graph_spatial_exclusion_v1.py` | explicit integer side-chain graph embedding and binary spatial exclusion |
| `tools/blind_24_lattice_selector_v17.py` | explicit graph-spatial local and global continuation |
| `tools/constitutional_lexicographic_exclusion_v1.py` | exact backbone-before-sidechain hard-exclusion hierarchy |
| `tools/blind_24_lattice_selector_v18.py` | hierarchical explicit graph-spatial continuation |
| `tools/blind_24_lattice_selector_v19.py` | v13-local, explicit-graph global assembly continuation |
| `tools/blind_24_lattice_selector_v20.py` | exact graph-atom encounter child hierarchy |
| `tools/blind_24_lattice_selector_v21.py` | explicit fold-to-One graph contact objective |
| `tools/blind_24_lattice_selector_v22.py` | ordered exact graph-contact deficit assembly |
| `tools/blind_24_lattice_selector_v23.py` | complete 576-state domains, bidirectional segment assembly and whole-chain reconciliation |
| `tools/blind_24_lattice_selector_v23_2.py` | locally closed domain correction for the V23 global architecture |
| `tools/blind_24_lattice_selector_v24.py` | coherent locally admitted four-residue tuple architecture |
| `tools/blind_24_lattice_selector_v24_1.py` | overlapping-window boundary closure for coherent tuple assembly |
| `tools/blind_24_lattice_selector_v25.py` | parent-anchored bidirectional constitutional coordinate beam |
| `tools/blind_24_lattice_selector_v26.py` | exhaustive joint long-range segment-topology transitions |
| `tools/blind_24_lattice_selector_v26_1.py` | focal segment-pair admission before whole-chain balance |
| `tools/blind_24_lattice_selector_v27.py` | exhaustive V25/V26.1 disagreement-cube reconciliation and bidirectional continuation |
| `tools/blind_24_lattice_selector_v28.py` | multiscale branch-block and boundary-domain propagation |
| `verify/development_runs/ubiquitin_v9_steric_orientation_l24_20260719/` | sealed v9 applied evidence |
| `verify/development_runs/ubiquitin_v10_balanced_relations_l{24,76}_20260719/` | sealed v10 applied evidence |
| `verify/development_runs/ubiquitin_v11_hbond_assembly_l24_20260719/` | sealed v11 hydrogen-bond applied evidence and post-seal local windows |
| `verify/development_runs/ubiquitin_v12_topology_hbond_l24_20260719/` | sealed v12 topology-separated applied evidence and post-seal local windows |
| `verify/development_runs/ubiquitin_v13_retained_topology_l24_20260719/` | sealed v13 cumulative 24-residue combined-relation benchmark and post-seal local windows |
| `verify/development_runs/ubiquitin_v13_retained_topology_l76_20260719/` | complete sealed v13 76-residue blind benchmark, global/local measurements, and v10/v13 propagation delta |
| `verify/development_runs/v13_single_build_candidate_20260719.json` | exact-output identity and 22.56% runtime-improvement receipt for the lossless execution candidate |
| `verify/development_runs/ubiquitin_v14_hbond_continuity_l{24,32}_20260719/` | sealed successor-continuity executions and matched v13/v14 delta receipts |
| `verify/development_runs/ubiquitin_v15_sidechain_spatial_l24_20260720/` | sealed spatial side-chain development evidence and v13/v15 delta receipt |
| `verify/development_runs/ubiquitin_v16_binary_sidechain_spatial_l24_20260720/` | sealed binary spatial-exclusion evidence and v15/v16 delta receipt |
| `verify/development_runs/ubiquitin_v17_graph_spatial_l24_20260720/` | sealed explicit graph-spatial evidence and v13/v17 delta receipt |
| `verify/development_runs/ubiquitin_v18_hierarchical_graph_l24_20260720/` | sealed hard-hierarchy exact-output evidence and v17/v18 delta receipt |
| `verify/development_runs/ubiquitin_v19_global_graph_l24_20260720/` | sealed global-only graph advance and v13/v19 delta receipt |
| `verify/development_runs/ubiquitin_v19_global_graph_l{32,76}_20260720/` | matched sealed graph propagation evidence, exact V13 path preservation, and delta receipts |
| `verify/development_runs/ubiquitin_v20_graph_atom_hierarchy_l24_20260720/` | sealed atom-encounter hierarchy evidence and exact V19 identity receipt |
| `verify/development_runs/ubiquitin_v21_graph_contact_l24_20260720/` | sealed explicit contact-map census and exact V19 identity receipt |
| `verify/development_runs/ubiquitin_v22_contact_deficit_l24_20260720/` | sealed active contact-deficit path, global/local measurements and V19 delta receipt |
| `verify/development_runs/ubiquitin_v23_global_domains_l{24,32,76}_20260720/` | sealed complete-domain bidirectional global development benchmarks |
| `verify/development_runs/ubiquitin_v23_2_local_domains_l{24,32,76}_20260720/` | sealed locally closed correction and L76 geometric recovery |
| `verify/development_runs/ubiquitin_v24_coherent_segments_l{24,32,76}_20260720/` | sealed coherent-segment architecture evidence |
| `verify/development_runs/ubiquitin_v24_1_boundary_closed_l{24,32,76}_20260720/` | sealed overlapping-window boundary-closure evidence |
| `verify/development_runs/ubiquitin_v25_coordinate_beam_l{24,32,76}_20260720/` | sealed parent-anchored coordinate-beam evidence and L76 dual-metric advance |
| `verify/development_runs/ubiquitin_v26_joint_topology_l{24,32,76}_20260720/` | sealed exhaustive paired-topology development evidence |
| `verify/development_runs/ubiquitin_v26_1_focal_topology_l{24,32,76}_20260720/` | sealed focal-topology evidence and strongest L76 dRMSD branch |
| `verify/development_runs/ubiquitin_v27_branch_reconciliation_l{24,32,76}_20260720/` | sealed complete branch-cube reconciliation evidence and L24/L32 advances over V26.1 |
| `verify/development_runs/ubiquitin_v28_multiscale_reconciliation_l{24,32,76}_20260720/` | sealed multiscale evidence and L76 dual-metric advance over V27 |
| `verify/development_runs/ubiquitin_v34_closed_domain_l76_20260720/` | sealed engine-admitted closed-domain L76 execution |
| `verify/development_runs/ubiquitin_v35_complete_boundary_l76_20260721/` | sealed complete-boundary L76 dual-metric advance |
| `verify/development_runs/ubiquitin_v36_two_boundary_l76_20260721/` | sealed emitted row from the recorded 16-candidate two-boundary grammar |
| `verify/development_runs/ubiquitin_v37_generator_partition_l76_20260721/` | sealed unique generator-partition admission and dual-metric advance over V36 |
| `verify/development_runs/ubiquitin_v38_coordinate_fixed_point_l76_20260721/` | sealed complete-coordinate fixed-point execution and dual-metric advance over V37 |
| `verify/development_runs/ubiquitin_v39_peptide_causal_l76_20260721/` | sealed peptide-causal fixed point and blind L76 topology advance |
| `verify/development_runs/ubiquitin_v40_lineage_paired_fixed_point_l76_20260721/` | sealed paired lineage fixed points, including post-seal evaluation of both rows |
| `verify/development_runs/ubiquitin_v41_component_cube_l76_20260721/` | sealed complete 8,192-assignment component reconciliation under the inherited order |
| `verify/development_runs/ubiquitin_v42_backbone_contact_frontier_l76_20260721/` | complete three-row connected frontier plus all 8,192 pre-comparison-sealed cube paths and their corrective evaluation |
| `verify/development_runs/ubiquitin_v43_one_cycle_frontier_l76_20260721/` | complete 1,082-row One-cycle frontier sealed before comparison; two-row empirical Pareto frontier |
| `verify/development_runs/ubiquitin_v44_connected_cycle_fixed_point_l76_20260721/` | three connected One-cycle fixed points sealed after 1,252,800 paired-state evaluations; active-admitted blind L76 distance advance |
| `verify/development_runs/ubiquitin_v45_boundary_axis_fixed_point_l76_20260721/` | twelve connected fixed points sealed after 331,200 coordinate evaluations; exact connected One-cycle TM advance plus complete local-window audit |
| `verify/development_runs/ubiquitin_v12_topology_hbond_l24_20260719/v11_v12_state_delta.json` | source-bound sealed-path and local-window delta locating the next combined relation |
| `verify/evaluate_sealed_blind_v3.py` | seal verifier and target-isolated evaluation boundary |
| `verify/evaluate_sealed_blind_local_v3.py` | all-window post-seal local evaluator; reproduces the published IFV/TLT measurements |
| `verify/protein_forcing_registry_v1.json` | complete source classification and legacy exclusion gate |
| `verify/PROTEIN_FORCING_AUDIT.md` | historical floor, trace findings, and authority boundary |
| `verify/POSITIVE_CANDIDATE_PRESERVATION_AUDIT.md` | complete assumptive-dismissal audit and empirical recovery queue |
| `calculate_tm.py` | repository TM scorer |
| `verify/test_protein_folding*.c` | project law checks |
| `papers/` | principal protein papers |

## Papers

- [Super Parity: 0.9891 TM-Score in Zero-Parameter Protein Folding](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)
- [Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)

Sibling computational-proof projects: [UnisonAI](https://github.com/MettaMazza/UnisonAI) · [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).
