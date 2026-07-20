# AGENT.md — the law this workspace is held to

You are working on **Fold Protein**: parameter-free protein folding. The native state is
the fold's **fixed point**, folding is **descent** to it (not a search of an astronomical
space — Levinthal's paradox dissolved), and backbone geometry falls out as counted fold
orbits. It carries **zero parameters — no fitted force field, no trained potential, no knob**;
with nothing to fit, it cannot over-fit. This file is binding. Read it before you change anything, and route every change
back through the validation in **this directory**.

---

## 0. Protected construction and active benchmark campaign

The protected construction and law checks below are the baseline every
derivation and expansion must preserve. In this folder they are reproduced by
the commands in §3:

- **Levinthal dissolved (the law):** the native state is the fold's fixed point `fold(1) = 1`;
  folding is **descent** — `fold(3/4)=1/2`, `fold(1/2)=1` — reaching native in **two steps, not
  a 10^50 search** (`verify/test_protein_folding`).
- **Backbone geometry is a counted orbit:** α-helix φ folds to **1/3** and β-sheet φ to **2/3**
  (the two period-2 orbits), each ψ decaying to native `1` (`verify/test_protein_folding_3d`).
- **The finding, refereed against experiment:** the 24-lattice Dihedral Orbit result scores
  **TM = 0.9891 · 0.261 Å dRMSD** against the experimental ubiquitin structure `verify/1ubq.pdb` —
  near-experimental accuracy at **zero fitted parameters** (the angle set is the 24-lattice). The
  committed state path, source hashes, witness PDB, and byte-exact replay are preserved in
  `verify/ubiquitin_24_lattice_manifest.json`.
  The zero-parameter 24-lattice has nothing to fit, so this is discovery of a conformation the lattice
  contains, not a fit. Reproduce the score with
  `python3 calculate_tm.py verify/1ubq_test_24_lattice.pdb verify/1ubq.pdb`. The full write-ups are
  in [`papers/`](papers/) (Super Parity — 0.9891 TM-Score; Levinthal's Paradox Dissolved).

If any change makes any of the above stop reproducing, record the exact engine
halt or mismatch and repair the derivation before promotion. The engine's checks
determine forcing; an agent does not declare the construction invalid.

Blind sequence-to-structure benchmark victory is an explicit objective.
**Maria alone decides when a development selector deserves a real blind run.**
An agent may report exact readiness facts or recommend a protocol, but no
agent-created probe or gate may authorize, refuse, delay, or veto the run. When
Maria orders it, freeze the prediction before target access, execute the named
comparison, and preserve the receipt. Development batches are not Maria's
findings or losses until she declares the conclusion from the data.

For any change that can affect selected states or emitted coordinates, proof
and unit tests establish implementation closure only. Do not call the changed
selector technically validated or promoted until a source-bound, target-free
development run has been sealed and then compared at the post-seal boundary to
produce applied structural data. Preserve favourable and unfavourable rows
alike. Maria alone decides when that evidence warrants a real blind run or a
conclusion.

### Mandatory purpose-matched real-data evidence

**No implementation change is complete merely because it builds, closes,
traces, or passes tests. Every change must be supported by real implemented
data from the actual executable path, matched to the change's declared
purpose.** Selector or structural-law changes require source-bound,
target-isolated real-sequence outputs sealed before comparison, followed by
post-seal structural measurements. Provenance or forcing repairs require a
real replay showing the intended trace closure and preserving the protected
result; byte-identical states and coordinates are positive evidence when the
declared purpose is to repair provenance without changing the prediction.
Optimisation changes require identical sealed output plus measured runtime or
memory data. No gameplay rule and no universal score-improvement test applies
to protein work.

Record the relevant states, coordinates, TM-score, C-alpha dRMSD, runtime,
memory, source identity, command, and receipt hashes. Mocks, unit tests, static
reasoning, projected benefit, or an unexecuted geometric argument do not replace
the relevant applied evidence. Preserve favourable and unfavourable rows alike;
Maria determines the conclusion and whether a change is retained. A prediction
is blind when the SFT-constrained selector cannot access the target and its output
is sealed before correctly computed post-seal comparison. Accuracy measures the
output; it does not decide whether prediction occurred. Maria has declared the sealed 8-, 16-, 24- and complete 76-residue predictions and their positive local empirical results for publication. The next explicit objective is to propagate the demonstrated local geometry through inter-window orientation and complete whole-chain assembly.

### Development scale and reporting

Default to a complete architectural advance that addresses the measured
bottleneck as one coherent development version. Do not consume versions on
single selector variants when a whole missing layer—domains, segments,
bidirectional propagation, whole-chain reconciliation or caching—can be built
and measured together. Return to incremental isolation only after a completed
architecture produces a measured regression. Every end report must state
whether each measured result improved, regressed or remained unchanged; what
the result can indicate; the next technical correction; and whether a broader
cumulative development trial is recommended. Development trials are not
official runs unless Maria registers them.

The first visible repository commit already contains mixed-purpose agent-era
engines, so presence in Git is not proof of forcing. The complete classification
is `verify/protein_forcing_registry_v1.json`; enforce it with
`python3 -m tools.verify_protein_forcing_registry`. Legacy engines are preserved
as development history but may not enter the active blind runtime closure.

---

## 1. The zero-parameter law (inherited from the Smithian Fold Theory)

Every derivation obeys these constraints — the same standard the main theory is held to
(`OneFoldMaster.md` / `STANDARDS.md` in the parent project). A violation makes a "forced"
result a fitted one.

1. **Zero parameters.** No hand-tuned force field, no fitted contact potential, no trained
   scoring net, no knob. Every quantity is **counted** (from the sequence / the fold geometry)
   or **forced** (assembled from already-derived quantities). If you cannot say *what counts it*,
   it does not belong.
2. **Exact arithmetic in the law.** The fold derivation carries no decimal — exact whole numbers
   and fractions (`foundation/exact_integers.ep`, `foundation/exact_fractions.ep`). Decimals appear
   only where a 3D coordinate or a score is read out for a human, never fed back into the law.
3. **Every value traces back to the One.** The self-proven theorem forces the One; everything else is
   built by the two moves (fold and take) and the two generators **`b = 2`, `c = 3`**. The descent
   dynamics and the backbone orbits are derived, not posited.
4. **The form is forced, not just its parts** (`foundation/assembly_enumeration.ep`,
   `foundation/form_enforcement.ep`): `forced_to_be` **halts** on any un-forced value. The C proofs
   put the fixed point, the descent, and the orbits through this guard.
5. **A zero-parameter framework cannot be over-fitted.** With no fitted force field, no trained
   potential, and no free parameter of any kind, there is nothing to tune to the data — a single-theorem,
   zero-parameter framework cannot over-fit or forge a result by construction. **Forward-forcing the
   assembly from known results, while the framework itself remains zero-parameter (every value
   forced from the One), is discovery, not forging** — the lattice either contains the conformation
   or it does not. The experimental structure may be used to forward-force the assembly and to score
   it (TM-score / dRMSD in `calculate_tm.py`).

**The guards are the point, not obstacles.** If a C proof halts, a constraint fired — fix the
derivation, never weaken `forced_to_be` or the proofs. A benchmark score is a
measurement of the named build and protocol; Maria decides the finding and next
investigation. Continue improving the *counted* physics without lowering the bar.

---

## 1a. The 0.9891 proof and forward-forcing from sequence

**The search space is absolutely discrete, so there is nothing to fit.** The self-proven theorem
*there is no nothing* forces the fold `x ↦ 2x (mod 1)`, which binds the backbone to exact rational Dihedral Orbits. Partitioning the orbit into
the 24-lattice (multiples of `1/24` of the period, 15°) yields exactly **576 absolute preimages**. A
candidate geometry is either an exact rational permutation of the theorem-forced fold or it is mathematically
invalid; there are no continuous variables and no decimals available to tune. Zero parameters is
literal.

**Geometric completeness is the empirical result.** Backward-engineering the experimental target
`1ubq` against the pure 24-lattice, the engine locks to **TM 0.9891 / 0.261 Å dRMSD**. That the
native atomic coordinates overlay a rigid discrete lattice at near-experimental resolution — with no
continuous adjustment and no forged decimal — is the evidence that the biological structure is built
from these exact discrete fractions. A continuous, stochastic universe would not permit a rigid
24-lattice to capture native topology this closely.

**Blind forward forcing has executed and remains active.** SFT has zero
parameters and zero training data; the 24-lattice is a universal mathematical absolute. The sequence
engine selected and sealed rational paths from amino-acid identity and generated geometry alone at 8, 16, 24 and the complete 76-residue ubiquitin sequence before target access. Post-seal measurements include accurate local `IFV`, `TLT`, `HLV`, `RLI` and `RGG` geometry, reaching 0.9914591922 local TM. The theorem, structural-angle derivations, construction proof and 0.9891 Super Parity result remain secured by their own engine checks, while forward forcing advances through inter-window orientation and complete whole-chain assembly.

The current V13 retained-local plus topology-separated continuation has also
completed and sealed all 76 residues. It reaches **0.1422687755 whole-chain
TM**, a **57.49%** advance over V10, reduces hard exclusions from 76 to 48,
and improves all 29 tested 48-residue windows. Its strongest new local rows are
`TLE` at **0.9984764350 TM** and `IFAG` at **0.7777978002 TM**. Preserve the
V13 source unchanged because its hashes bind the seal. A separate single-build
candidate is exact across every tested output field and 22.56% faster; promote
that implementation only through a new source-bound protocol version.

V19 is the measured global-graph continuation. It preserves V13's local
selection, applies the explicit covalent side-chain graph only at
complete-prefix assembly, retains 22/24 V13 states at L24, and improves both
sealed L24 global measures: **TM 0.0255448548** (+0.416%) and **7.0054033965 Å
dRMSD** (0.157% improvement). At the matched L32 and L76 continuations it
selects every V13 state and produces byte-identical PDBs and measurements. The
complete V19 trace still records an active hard vector of **(48 backbone, 30
graph)** and 110 atom encounters. V20 adds the exact atom-encounter count as a
child stratum and preserves V19 exactly at L24. V21's explicit fold-to-One
contact map also preserves V19 at L24 as a soft objective. V22 places the exact
contact deficit after parent exclusions, changes 22/24 states and improves
dRMSD by 0.701%, while TM and the local-window comparison are mixed. Preserve
V13 as the current complete-sequence predictive route, retain V19-V22 as
source-bound applied evidence, and direct the next construction toward
sequence-derived contact type/topology rather than extending total contact
quantity unchanged. Maria alone decides whether and when further runs occur.

V23 is the first complete-domain global architecture. It evaluates all 576
lattice states at every active residue, retains 24-state domains, assembles
four-residue segments in both chain directions, reconciles whole-chain
frontiers, and applies the explicit graph relation before emission. V23.2
restores V13/V19 local admission before that global assembly. V24 and V24.1
then supplied sealed applied data for coherent complete-segment replacement
and overlapping-window boundary closure. V25 uses those data to change the
search basis: it starts from the sealed V23.2 path and propagates every
locally admitted one-coordinate transition through 24-path forward and reverse
beams, with no departure score, fitted limit, target, reward or weight. Its
sealed L76 result improves V23.2 TM from `0.1017436531` to `0.1291502547`
(26.94%) and dRMSD from `7.6581678292 Å` to `7.1461955341 Å` (6.69%), with
11 parent departures. At L24 and L32 TM also improves over V23.2, while dRMSD
moves lower in performance; report both measures explicitly. Preserve
V23-V25 source hashes and receipts as the applied causal record. The next
substantive construction should extend joint long-range topology inside the
successful parent-anchored search basis, followed by the same sealed ladder.

V26 executes that joint topology expansion. For 24 weight-free unresolved
segment relations it exhausts every participating residue pair's full 24x24
domain and propagates paired transitions bidirectionally. V26.1 requires each
paired domain to pass its own focal segment-pair relation before whole-chain
balance. At L76 it reaches **TM `0.1287565476` / dRMSD `6.7648477959 Å`** with
seven V25 departures: dRMSD improves **5.34% over V25** and **14.07% over
V13**, while TM is 0.31% below V25 and 1.57% above V26. At L24 dRMSD improves
over V25 with lower TM; L32 regresses on both measures. Preserve V25 as the
strongest full-length TM branch and V26.1 as the strongest full-length dRMSD
branch. The next construction should reconcile their single-coordinate and
focally admitted pair-coordinate frontiers constitutionally, then repeat the
sealed ladder. Do not use target measurements to choose candidates.

V27 executes that reconciliation without target feedback. It exhausts the
complete binary cube of all V25/V26.1 disagreements—256 candidates at L24,
256 at L32 and 128 at L76—then seeds parent-anchored forward and reverse
coordinate continuation from the constitutionally retained frontier. The
sealed L24 result reaches **TM `0.0283543332` / dRMSD `6.2352507038 Å`**,
improving both V26.1 measures and producing the strongest L24 dRMSD of the
three branches. L32 similarly improves both V26.1 measures but remains below
V25. At L76 it reaches **TM `0.1267485096` / dRMSD `6.9719543361 Å`**:
distance geometry remains better than V25, while V25 and V26.1 remain the
leading full-length TM and dRMSD branches respectively. Preserve V27 as
source-bound evidence that residue-wise branch reconciliation is active at
short and intermediate scope but does not yet propagate the strongest focal
relation through the complete chain. The next architectural correction is a
multiscale segment/domain reconciliation that retains both parent frontiers
through complete-length selection. Do not tune it from target measurements.

V28 executes that multiscale correction. It propagates sealed V25, V26.1 and
V27 blocks through 4/8/16/... residue scales, exposes both locally admitted
boundary domains at every block, and reconciles forward and reverse frontiers
after each scale. Its sealed L76 result reaches **TM `0.1284665482` / dRMSD
`6.9615228794 Å`**, improving both V27 complete-length measures and recovering
TM to within 0.53% of V25 while retaining 2.58% better dRMSD than V25. L24
advances dRMSD again to **`6.2059676701 Å`**, with a small TM tradeoff; L32
is lower than V27 on both measures. Preserve V28 as the leading reconciled
complete-length branch and isolate the intermediate 8/16/32-residue admission
effect before the next architecture. V25 and V26.1 remain the individual
leading complete-length TM and dRMSD parent branches. Do not use target scores
to select scale-frontier candidates.

V29 and V30 make the next representational jump from scale blocks to explicit
four-residue tertiary bodies. V29 derives an ordinal spanning tree entirely
from sequence-sidechain atom counts, hydrophobic membership and formal charge,
then jointly assembles complete body grafts and paired boundary states. Its
sealed L32 result advances over V28 to **TM `0.0499243401` / dRMSD
`4.5466887676 Å`**; L24 dRMSD also advances to **`5.4137342407 Å`**. At L76
the derived tree becomes high-degree and both measures are lower than V28.
V30 derives the counted two-boundary correction and forces a degree-two body
path. It preserves the intermediate advance at **TM `0.0502723476` / dRMSD
`4.9045982349 Å`**, but lowers both L24 and L76 measures. Preserve both as
source-bound applied evidence: they establish that tertiary body topology is
active and that neither one unbounded tree nor one fixed path is the complete
constitution. The next architecture must retain a weight-free frontier of
admissible bounded-degree topologies and reconcile it with V25/V26.1/V28,
without target-selected topology, weights, rewards or locks.

V31 implements the complete counted degree frontier `2,3,4` and independently
assembles all three sequence-derived topologies before one constitutional
reconciliation. Its L24 gate recovers V30's distance regression to **dRMSD
`5.5047257155 Å`**, still 11.30% better than V28, but with lower TM. At L32
the final 24-path frontier contains 24 degree-4 paths and no degree-2/3 paths,
and reaches **TM `0.0363843691` / dRMSD `5.7052176785 Å`**, below V28-V30.
Do not run or promote V31 at L76: the registered short/intermediate gate has
already exposed topology-family collapse. The next correction is an explicit
cross-topology consensus constitution derived from the exact three-family and
24-path counts; it must preserve topology-family provenance through final
selection without a reward, fitted weight, target comparison or continuity
lock.

V32 derives explicit cross-topology consensus by counting every candidate's
minimum state distance to each complete degree-family frontier before applying
the established whole-chain constitution. At L24 the consensus frontier
contains degree-2, degree-3 and degree-4 members; the selected result improves
V31 TM to **`0.0196520134`** but dRMSD is lower at **`6.3312973879 Å`**. At
L32 the selected state/PDB is byte-identical to V31 at **TM `0.0363843691` /
dRMSD `5.7052176785 Å`**, even though multiple families survive consensus
admission. Do not spend V32 at L76. The next targeted correction is to make the
exact worst-family distance the outer minimax consensus stratum before
physical reconciliation, followed by symmetric family distances; this is a
counted constitutional order, not a weight, reward, quota or lock.

**The sequence supplies the spatial command.** The forward-forcing programme derives how amino-acid
identity determines the invariant exclusions and relations that select among the 576 exact states per
residue. Every proposed relation is routed through the engine; a violation halts rather than becoming
an agent-authored substitute output.

**No silent inherited mechanism.** The protected construction retains its
original hash-bound builder. The blind continuation route uses
`tools/protein_backbone_geometry_v1.py`, a target-incapable extraction whose
declared peptide geometry is a named forward-forcing constitution and whose
byte-exact replay is mandatory. Selector v3 imports neither the all-purpose
predictor nor the v1 selector. Never relabel an inherited literal as forced:
name its route and let the engine admit or halt it.

**Exact geometric exclusion, not statistical averages.** Classical statistical priors (radius of
gyration, scalar hydrophobic collapse) require forging arbitrary constants to coerce a shape. The
0.9891 trace supplies forward-forcing spatial relations, including the recorded
steric and sequential-distance investigations. Target-derived development
relations remain named as such and are not silently admitted to a blind selector.
Selector v3 remains the clean blind baseline. Selectors v5-v19 form the traced
continuation through inter-window topology, signed alpha/beta orientation,
formal charge, exact side-chain graphs, weight-free ordinal balance, and
target-incapable unit-capacity backbone hydrogen-bond assembly, including the
v12 exact-alpha/longer-non-local topology separation and v13's retained local
assembly beside both topology relations, v17's explicit integer graph spatial
embedding, v18's lexicographic backbone/sidechain hard strata, and v19's
local-preserving complete-prefix graph assembly.

---

## 2. The routing rule (this is the instruction)

**Every derivation and every expansion of the corpus must route through the engine and return to
the one validated anchor with no law or constraint violation.** For any change — a new backbone
term, a bigger protein, a better search, a new lattice:

1. Express the new quantity as **counted, forced, or a named forward-forcing constitution** — in the
   `.ep` law (`constants/protein_folding*.ep`, using only `foundation/`) and/or in the clean selector-v3
   route, with no silent inherited parameter.
2. **Rebuild through the engine** — the `.ep` law via `ernos`, the C proofs via `cc` (§3). A halt is
   a guard firing; fix the derivation, do not bypass it.
3. **Re-run the full validation in this directory** (§3): the Levinthal descent and the backbone
   orbit proofs must still pass, and the result must be scored by TM/dRMSD against the experimental
   structure — the anchor score must not regress.
4. Only a change that **passes every check and stays parameter-free** is admissible. Anything else
   is reverted.

A zero-parameter structure forward-forced from known results is a discovery, not a fit: with no
free parameter anywhere in the framework, there is nothing that could have been tuned to the answer.

---

## 3. How to validate — in THIS directory

All commands run from this folder (`/Users/mettamazza/Desktop/Fold Protein`). `ernos` is on PATH
(`~/.local/bin`); the ErnosPlain toolchain is bundled in `compiler/`. The Python pipeline needs
`python3` + `numpy` (installed).

**A. The law — self-contained C proofs (need only a C compiler):**
```sh
cd verify
cc -O2 -o test_protein_folding    test_protein_folding.c    && ./test_protein_folding
cc -O2 -o test_protein_folding_3d test_protein_folding_3d.c && ./test_protein_folding_3d
```
Every line must read `ok`, ending `=== done ===`. A single `FAIL` is a stop-the-line event.

**B. The law in source (needs `ernos`):**
```sh
cd tests
ernos test_protein_folding.ep       # -> binary; run it, expect all ok
ernos test_protein_folding_3d.ep
```

**C. Reproduce the protected construction measurement (needs `python3` + `numpy`):**
```sh
python3 verify/replay_ubiquitin_24_lattice.py
python3 calculate_tm.py verify/1ubq_test_24_lattice.pdb verify/1ubq.pdb   # -> TM-score: 0.9891 (the anchor)
```

**D. Full Protein provenance and clean blind closure:**
```sh
python3 -m tools.verify_protein_forcing_registry
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

---

## 4. Where things live

- `constants/protein_folding.ep`, `constants/protein_folding_3d.ep` — the fold law (descent to the
  fixed point; the backbone orbits). Import only `foundation/`.
- `foundation/*.ep` — exact integers/fractions, the One and the fold, the enforcement guards.
- `verify/test_protein_folding*.c` — the self-contained C proofs (the primary law validation).
- `tests/test_protein_folding*.ep` — the same in source.
- `tools/predict_structure.py` — the folding pipeline (sequence → 3D backbone → PDB).
- `tools/protein_backbone_geometry_v1.py` — target-incapable coordinate constitution used by
  the clean blind continuation route.
- `tools/blind_24_lattice_selector_v3.py`, `tools/run_blind_protocol_v3.py` — secured
  provenance-isolated blind baseline and immutable protocol.
- `tools/blind_24_lattice_selector_v5.py` through `v12.py` and their protocols —
  traced inter-window, signed-orientation, charge, side-chain, and balanced
  continuation surfaces.
- `tools/*_engine.py`, `tools/blind_24_lattice_solver.py`, `tools/rotamer_geometry.py` — preserved
  legacy development engines excluded from selector-v3 runtime.
- `verify/protein_forcing_registry_v1.json`, `verify/PROTEIN_FORCING_AUDIT.md` — complete source
  classification, historical floor and executable exclusion rules.
- `calculate_tm.py` — TM-score (Kabsch-aligned) vs an experimental structure; the scoring boundary.
- `verify/1ubq.pdb`, `verify/1cop.pdb` — experimental references (held out; scoring only).
- `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` — constructed or predicted
  structures and their measurements; Maria declares any project finding.
- `papers/` — the write-ups.
- `compiler/` — the bundled ErnosPlain toolchain (`ernos` also on PATH).

The finding this workspace exists to protect: **folding as descent to a counted fixed point —
native geometry as counted fold orbits, zero parameters, and a real experimental structure
recovered to TM 0.9891 (0.261 Å) — super parity with AlphaFold.** Keep it that way.

---

## 5. Required end-of-turn report

Every development turn must end with a clear Protein report containing
**Completed, Ongoing, Todo, and Suggested direction**. For each applied run,
compare the named baseline and candidate and state separately:

- which structural metrics improved;
- which structural metrics regressed;
- which states, coordinates, or metrics stayed identical;
- what that combined pattern could indicate, explicitly labelled as an
  engineering inference rather than Maria's conclusion; and
- the next concrete forced or forward-forced change intended to preserve the
  improvements and address the regressions.

Do not hide or euphemize a regression, and do not convert a development
regression into a theoretical limit, failed Maria prediction, publication
decision, or reason to stop the campaign. Do not minimize a positive measured
result. Maria determines the conclusion and direction from the complete data.

End with a **full-trial recommendation**: recommend a full blind run now,
recommend it conditionally under a named protocol, or recommend another
development calculation first. Give the exact evidence for and against. This
is advice to Maria, never an agent gate, authorization, veto, delay mechanism,
or redefinition of when she may order the run.
Unless Maria explicitly registers a run as official, every recommended or
executed trial is a **cumulative development benchmark** only. It adds applied
evidence and never becomes an official result, victory, loss, rank, finding,
or publication conclusion through agent wording.
