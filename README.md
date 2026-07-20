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
  3- and 4-residue local TM rows were lower than v11, while the best
  5-residue row improved slightly from `0.2462605086` to `0.2477913128`.
  These mixed local results are preserved explicitly and are not used as a
  theoretical limit. Maria determines the conclusion and continuation.

The source-bound v11/v12 path-delta analysis now locates that change precisely:
topology separation changed **23/24** selected lattice states. Across all
same-index windows, v12 improved **9/22** length-3, **6/21** length-4, and
**7/20** length-5 geometries, while respectively 13, 15, and 13 moved lower.
The largest local advances include `EVE` (+0.503398 TM), `TLE` (+0.489450),
`TIT` (+0.449918), and `DTI` (+0.326621), alongside the whole-prefix gains of
+0.010020 TM and −0.921532 Å dRMSD. This applied pattern indicates that the
topology relation is exerting real global and local command rather than merely
renaming the v11 path, while also identifying why the next selector should
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

V14 tested the next exact continuity constitution: two held hydrogen bonds are
continuous when their donor and acceptor residues are both integer successors,
with alpha and inter-strand continuity retained as independent objectives. The
relation is target-incapable, parameter-free and active, but the sealed 24- and
32-residue development gates selected byte-identical structures to v13. The
32-residue prediction therefore retains **TM 0.0729998746 / 5.9835980697 Å
dRMSD** with zero predictive delta. This applied gate does not justify a
76-residue v14 run in its present form. It does preserve the constitution for
future assembly work and confirms the single-build execution path at 32
residues: `283.38 s` versus v13's `513.96 s` (**44.86% faster**). The active
predictive direction is now spatial side-chain exclusion, retaining v13 and
the lossless execution improvement.

V15 executes that spatial side-chain direction. From each generated N/CA/C
frame it derives the positive L-chiral half-space, uses the exact constituted
side-chain heavy-atom graph count to place a target-incapable command point,
and admits no target, template, rotamer, empirical radius, distance table,
fitted weight, reward or learned parameter. Its sealed 24-residue run changed
21/24 selected states and reduced the constituted spatial census from the 10
excluded residue pairs / 145 possible heavy-atom encounters present in the
v13 structure to **3 pairs / 39 encounters**. Its strongest five-residue
window advanced from v13's `0.2576423823` to **`0.2884520984 TM`**
(**11.96%**), while the whole-prefix comparison measured TM `0.0124237689`
and dRMSD `7.6841356168 Å`. This applied gate proves the new relation is
active and supplies real discrimination data; it does not replace v13 as the
current complete-sequence route.

V16 then makes the hard-exclusion fact exact as set membership: one excluded
non-neighbour residue pair is one hard exclusion. The exact heavy-atom
Cartesian product remains recorded as an encounter census but no longer
multiplies the absolute hard stratum. Its sealed 24-residue prediction improves
on v15 to **TM `0.0126289266` / dRMSD `7.5227694169 Å`** (respectively
**1.65%** and **2.10%**), while preserving the same strongest local scores:
`0.9955319779` at length 3, `0.6021806558` at length 4 and
`0.2884520984` at length 5. The v16 path is identical to v15 at 23/24 states,
so binary counting is a precise correction but not the principal predictive
advance. The next state is a spatial instantiation of the exact side-chain
graph and branch topology rather than a single command point. V15 and v16 are
therefore retained as source-bound development evidence, while a 76-residue
trial waits for that graph-spatial continuation to pass the 24-residue gate.
This is a resource-directed development decision, not a theoretical wall.

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
itself—as the assembly placement to refine.

V18 separates the already-forced hard facts into the exact lexicographic
vector `(backbone, sidechain_graph)`, preventing a child side-chain exclusion
from trading against its parent backbone exclusion. It selects all **24/24**
v17 states and an identical PDB, with zero global or local predictive delta.
That exact-output evidence closes the hard-stratum semantics and localises the
next change to where graph geometry enters selection.

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
and shows that encounter multiplicity alone does not supply the next
discriminator in this hierarchy. It is retained as source-bound development
evidence rather than extended unchanged.

V21 re-derived an explicit non-neighbour contact map in the generated shell
between the folded Cα step and the complete step. Its sealed L24 path records
**19 residue-pair contacts / 123 atom contacts** but preserves all **24/24** V19
states and every measurement exactly when contact count enters as one soft
ordinal objective. V22 then placed the exact contact complement after the two
parent exclusion strata. That ordered relation is strongly active: **22/24**
states change, backbone/graph exclusions fall to **4/2**, and whole-prefix
dRMSD improves from `7.0054033965 Å` to **`6.9563150359 Å`** (**0.701%**).
Whole-prefix TM changes from `0.0255448548` to `0.0232375689`; the local rows
are mixed, with 8/22 length-three, 10/21 length-four and 9/20 length-five rows
improving. V22 therefore demonstrates that explicit graph contact topology can
drive blind global assembly and improve pairwise-distance geometry, while its
undifferentiated total-contact constitution is retained as development
evidence rather than promoted or extended unchanged.

These are target-isolated, seal-before-score implemented development results.
They extend the executable forcing chain; they are not agent-declared
findings, limits, or substitutions for Maria Smith's conclusions. The current
next state is to separate sequence-derived contact type or contact topology
inside inter-window assembly while retaining v13's secured local relations and
lossless single-build execution. The secured
lattice containment, forced secondary-structure coordinates, complete blind
execution, and successive local and whole-chain advances establish a
constructive route forward and no theorem-derived obstruction at this stage.

The matched complete 76-residue V19 blind cumulative development benchmark is
also complete. Its exact preservation of V13, active explicit graph census and
the preceding L24 advance support proceeding to a new graph-derived
propagation relation rather than repeating V19 or extending V20-V22 unchanged. It
remains a cumulative development benchmark unless Maria explicitly registers
it as an official run.

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
each derived four-residue unit through independent 24-path forward and reverse
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

V29 changes the represented object to a sequence-forced tertiary graph of
four-residue bodies. Exact sidechain-atom, hydrophobic and formal-charge counts
order the body edges before coordinates exist; complete body grafts and paired
boundary states are then assembled in both directions. This produces a large
intermediate-length advance: L32 reaches **TM `0.0499243401` / dRMSD
`4.5466887676 Å`**, improving V28 by **12.33% TM** and **19.04% dRMSD**. L24
dRMSD improves **12.77%** to **`5.4137342407 Å`**, with a 2.37% TM tradeoff.
The 76-residue tree exposes an unbounded hub and is lower than V28 on both
measures. V30 replaces that hub with the body's counted two-boundary relation,
forcing a connected degree-two tertiary path. It retains the L32 advance at
**TM `0.0502723476` / dRMSD `4.9045982349 Å`**, but its L24 and L76 rows are
lower. These cumulative development benchmarks establish active tertiary
topology discrimination and locate the next architecture at a retained
frontier of admissible bounded-degree topologies, rather than one fixed tree
or path. They do not establish a theoretical wall or an official result.

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
| `verify/development_runs/ubiquitin_v14_hbond_continuity_l{24,32}_20260719/` | sealed successor-continuity activation gates and matched v13/v14 delta receipts |
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
| `verify/development_runs/ubiquitin_v12_topology_hbond_l24_20260719/v11_v12_state_delta.json` | source-bound sealed-path and local-window delta locating the next combined relation |
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
