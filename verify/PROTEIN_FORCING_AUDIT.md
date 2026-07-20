# Fold Protein forcing and provenance audit

**Audit date:** 19 July 2026
**Auditor:** Codex gpt-5.6-sol (high)  
**Authority boundary:** the engine's trace, closure and halt standards determine
admission. This audit records source provenance and executable dependency facts;
it does not replace the engine and it does not decide Maria Smith's publishable
conclusions.

## Scope and historical floor

The audit begins at the repository's first visible commit,
`6b08f5288034d0958a15c8b4b0af0edb59715e37` (15 July 2026). That commit is not a
clean creation boundary: it already contains the copied theorem foundation, the
all-purpose Python predictor, target-guided optimisers, annealing and beam-search
code, many generated PDBs, and workspace guidance written in an agent voice.

Consequently, Git authorship cannot prove who designed those pre-existing files
or whether each mechanism had already passed the SFT forcing standard. Every
source is classified from its actual executable role instead. The complete,
machine-checked classification is
`verify/protein_forcing_registry_v1.json`.

The bundled `compiler/` directory is an inherited infrastructure boundary, not
a Protein-specific forcing mechanism. Its 315 tracked files are byte-identical
to the canonical compiler directory in the main SFT corpus at this audit point.
Their stable relative-path/file-hash census has SHA-256
`d64800349f2ab8939c9e09ee85d2fef12559c3b712ce79c4363bee92d6cfe62c`.
The registry checks that boundary separately and selector v3 cannot import it.

## Secured routes

### One-traced protein law

`foundation/the_one_and_the_fold.ep` identifies the foundation as one
machine-checked self-proven theorem—*there is no nothing*—with zero axioms, and
implements the One and fold. The exact-fraction, enforcement and form modules
are imported by `constants/protein_folding*.ep`. The Ernos source tests and their
committed C translations are classified with this route and remain executable
anchors.

### Protected 24-lattice construction

The 0.9891211351 TM / 0.2608575408 Å ubiquitin result is preserved in its actual
form: a target-assisted forward-forcing construction. The native coordinates
selected the 76-state path during development. The path, builder, scorer,
target, constructed PDB and development log are hash-bound in
`verify/ubiquitin_24_lattice_manifest.json`, and
`verify/replay_ubiquitin_24_lattice.py` reproduces the constructed PDB byte for
byte before re-measuring it.

That route is not a blind selector and does not need to be relabelled as one to
stand as the declared structural construction result.

### Isolated coordinate constitution

The protected construction historically called `tools/predict_structure.py`.
That file also contains unrelated agent-era secondary-structure heuristics,
score weights, steric cutoffs, random optimisation and target-assisted search.
Importing the whole file into a blind selector therefore created an avoidable
provenance ambiguity even when only its coordinate function was called.

The required coordinate relation is now extracted into
`tools/protein_backbone_geometry_v1.py`. It contains only:

- exact rational declarations of the peptide bond geometry already used by the
  protected construction;
- deterministic NeRF coordinate placement; and
- the historical PDB writer.

It cannot read or parse a target, calculate a target score, optimise, anneal,
sample, or select a lattice state. The declared bridge is recorded in
`verify/protein_backbone_geometry_v1.json`. Its replay rebuilds all 76 residues
and reproduces the protected constructed PDB SHA-256
`0036d16f9a70d03458ffc2bdfc32876f1fc77f7dac88379cb69352840b02a21d`.

This is deliberately named as a **forward-forcing peptide-geometry
constitution**. It is not silently labelled theorem-derived merely because the
same numbers were already present in an old file.

### Blind selector v3

`tools/blind_24_lattice_selector_v3.py` re-derives the registered v2 state path
and dimensionless ordering without importing the legacy predictor or v1
selector. Its runtime project closure is only the target-incapable coordinate
constitution. `verify/blind_selector_v3.json` names every relation and its
route:

- One and fold: engine-traced foundation;
- 24×24 lattice: forward-forced from the protected construction;
- peptide geometry: named forward-forcing constitution with byte-exact replay;
- NeRF and sealing: constitutional computational re-derivations;
- hydrophobic alphabet and topology order: registered sequence and generated-
  geometry relations;
- beam capacity: the 24-state lattice-axis census.

The active selector now computes that capacity directly from the 24-axis
census and verifies `axis × axis = 576` before selection. The protocol rejects
any manifest that attempts to substitute a caller-selected beam width. This
closes the configurable-width boundary; it does not by prose decide the
separate engine question of whether finite frontier retention is the admitted
causal selection form.

The registered residue relation is now executable in
`tools/residue_partition_v1.py`. The selector no longer owns an unexplained
alphabet literal: the module enumerates the complete 20-residue alphabet,
proves the two registered classes disjoint and exhaustive, and supplies the
sealed packing class to v3. This is deliberately recorded as a constitutional
re-expression of the registered biochemical relation, not relabelled by prose
as a theorem-only derivation.

The v3 protocol accepts exactly `run_id` and `sequence`, checks all source
hashes, refuses an existing output directory, and seals its state path and PDB
before any comparison.

### Completed blind sequence predictions and local evidence

Selector v3 executed on real ubiquitin sequence prefixes of 8, 16 and 24
residues. Each process received only `run_id` and `sequence`, sealed its files
before target access, and was measured afterward. The selector was constrained
by its registered SFT route, the target was isolated, and the structures were
sealed before correctly computed comparison. These are therefore blind
sequence-to-structure predictions; the empirical scores measure their outputs
and do not decide whether prediction occurred.

The whole-prefix TM/dRMSD values are 0.0984554745/3.0632533843 Å,
0.0047139964/9.0940266174 Å, and 0.0073475432/12.7322387564 Å at lengths 8, 16
and 24. Post-seal local comparison additionally records `IFV` at 0.8821336259
local TM / 0.1611313002 Å dRMSD and `TLT` at approximately 0.892 local TM /
0.187 Å dRMSD in the independently sealed 16- and 24-residue outputs. The
method and exact values are preserved in
`verify/blind_local_sequence_evidence_20260719.json`.

Maria Smith has declared these results for publication. Complete 76-residue
blind sequencing was subsequently executed under
the same target-isolated, pre-comparison-sealed protocol. It matched all 76 Cα
atoms at TM `0.0269927379497572` and dRMSD `52.89314678065376 Å`. The post-seal
three-residue readout found `HLV` at TM `0.9914591922414299` / dRMSD
`0.03139535401876445 Å`, `RLI` at TM `0.9656795312222751`, and `RGG` at TM
`0.9059580746307327`. Maria has declared the completed blind execution and
these positive local empirical results for publication. The four- and
five-residue extension measurements, TM `0.3534794031641911` and
`0.3209890061552319`, locate the next constructive frontier at inter-window
orientation and complete global assembly. They do not establish a
theorem-derived wall: the protected 24-lattice construction already contains
the complete 76-residue trace at TM `0.9891211351` / dRMSD `0.2608575408 Å`,
and the structural law independently forces the canonical α-helix and β-sheet
coordinates.

### Four-residue inter-window orientation development

The next relation is now executable rather than prose-only.  Three C-alpha
points define one local plane.  Two consecutive colour-count windows share the
binary count of two residues, so their union is exactly
`c + c - b = 3 + 3 - 2 = 4` residues.  Consecutive orientation quartets share
one colour window and advance by the One residue.  The Ernos source
`constants/protein_interwindow_orientation.ep` and its test close all three
relations.

Selector v5 makes the generated topology of that terminal four-residue union
primary and retains the complete-prefix v3 topology as its secondary exact
order.  It accepts only run ID and sequence, carries no target import, fitted
weight, reward scale, cutoff or caller-selected beam width, and preserves every
candidate tied at the exact 24th local-key boundary.  Six implementation and
protocol tests pass, including source-hash sealing and complete seal
verification before target access.  The forcing registry now classifies 85
sources and checks both v3 and v5 runtime roots against the prohibited legacy
imports.

The source-bound v5 route produced and sealed real ubiquitin predictions before
comparison.  At 24 residues it measured TM `0.04392860627693118` and C-alpha
dRMSD `6.635927337975497 Å`; its best length-four window was `LEVE` at TM
`0.4695859044249241` / dRMSD `0.2849076209440542 Å`.  At all 76 residues it
measured whole-chain TM `0.12321119756884483` and dRMSD
`8.362531771197228 Å`; `DKE` measured TM `0.9991809284761722` / dRMSD
`0.012524856080253319 Å`, `DKEG` measured TM `0.8460707854249027` / dRMSD
`0.07659930003598996 Å`, and `QDKEG` measured TM `0.3332405586263601` /
dRMSD `0.3430673089924402 Å`.  The complete run took `141.99 s` and a
maximum resident set of `73138176` bytes.

These are agent-generated applied development measurements.  Maria Smith alone
decides their interpretation, publication status and relationship to the
official benchmark campaign.  The preceding v4 three-residue compactness probe
is preserved separately as auxiliary evidence and is not attributed to Maria
as a finding, loss or failed prediction.

Post-seal diagnostics identify the next constructive relation.  V5's quartet
key uses distances only, so it cannot distinguish a four-point orientation
from its reflection.  The target's mean absolute normalized signed quartet
volume is `0.5520106181`, while the v5 output's is `0.0001530513`; the current
order therefore selects nearly coplanar quartets even while improving the
declared four-residue and whole-chain measurements.  The next target-incapable
candidate is to order signed orientation against the already forced alpha and
beta orbit geometries, without feeding this post-seal target measurement into
selection.  This is a traced development direction, not a theoretical wall.

### Signed orientation and sequence-mode investigation

Selectors v6-v8 execute the next three target-incapable relations and preserve
their applied data without converting an agent development decision into
Maria's finding or loss.

V6 generates signed orientation modes at runtime from the already checked exact
alpha angles `(-60,-45)` and beta angles `(-120,+135)` through the registered
peptide geometry.  Its normalized scalar triple product distinguishes a
quartet from its reflection without a target signature.  Exact 24-lattice
precursor distance preserves the required angle preimages before four C-alpha
points exist.  The sealed 24-residue execution took `42.29 s` and
`42811392` bytes maximum resident memory.  It raised the best length-three
window to TM `0.9997317192086165` / dRMSD `0.008048135329553634 Å` and the
best length-four window to TM `0.8233174803435775` / dRMSD
`0.13222259310265932 Å`.  Its selected path used the generated alpha mode for
all 21 quartets; whole-prefix TM was `0.013229042104232267` and dRMSD
`7.6987200275234 Å`.  That exact all-alpha observation prevented an
unnecessary 76-residue development execution.

V7 divides the counted 24-state frontier by the fold-derived binary count,
preserving 12 alpha and 12 beta candidates at every complete frontier.  Its
sealed 24-residue execution took `62.43 s` and `42090496` bytes maximum
resident memory.  The final path contained 20 alpha quartets and one beta
quartet; whole-prefix TM was `0.018838872206853943` and dRMSD
`7.6816338204616015 Å`.  Its best length-four window measured TM
`0.7992362769952934` / dRMSD `0.23589752864348937 Å`.

V8 adds an exhaustive formal side-chain charge constitution: `KR` positive,
`DE` negative, and the remaining registered residues uncharged.  Histidine is
left uncharged because protonation is environment-dependent and the selector
has no pH input or fitted fractional charge.  The dimensionless relation sums
signed inverse generated distances using endogenous adjacent step length; it
has no dielectric, cutoff, or weight.  Its sealed 24-residue execution took
`113.35 s` and `42336256` bytes maximum resident memory.  It changed the path
and selected two beta quartets, proving the charge relation is active, while
measuring whole-prefix TM `0.017414235712281952`, dRMSD
`7.906006815779378 Å`, and best length-four TM `0.7994283891088441` /
dRMSD `0.2358215171960537 Å`.  This did not warrant a 76-residue development
execution under the mandatory purpose-matched data rule.

V9 adds an exhaustive 20-residue covalent side-chain heavy-atom graph
constitution. Its dimensionless crowding relation counts possible heavy-atom
encounters as the Cartesian product of two side-chain graphs and divides only
by generated C-alpha separation normalized by generated adjacent step. There
are no inherited residue radii, distance cutoffs, rotamers, fitted weights,
targets or empirical structures. Its sealed 24-residue execution took
`113.85 s` and `41533440` bytes maximum resident memory. It produced the
strongest five-residue local continuation in the 24-residue line: `GKTIT`, TM
`0.8383894512021005`, dRMSD `0.23618646085369144 Å`; its best length-four
window `KTIT` measured TM `0.9127952096871118`.

V10 removes numerical-scale privilege between the active physical relations.
Hard self-exclusion remains an absolute integer stratum. Signed orientation,
side-chain crowding, charge, hydrophobic dispersion and radius become exact
within-frontier ordinal ranks; each candidate's worst-to-best rank vector gives
a permutation-invariant minimax order with no weights or score blend.

The sealed v10 24-residue execution selected a mixed 10-alpha/11-beta path,
measured whole-prefix TM `0.03327082818773979` and dRMSD
`6.6076920575729385 Å`, and justified the full continuation. The sealed
76-residue execution completed in `806.75 s` with `105873408` bytes maximum
resident memory and selected 33 alpha plus 40 beta quartets. Whole-chain TM
was `0.09033263627027091`; C-alpha dRMSD was
`7.241687663489846 Å`, the strongest full-chain blind dRMSD in the
v3/v5/v10 line. Its best length-three window `TLE` measured TM
`0.9977831859693745`, best length-four `DTIE` measured TM
`0.7161453983087227`, and best length-five `TLTGK` measured TM
`0.609078001588949`.

The applied sequence now supplies separately executable signed geometry,
binary mode preservation, charge-sensitive switching, exact side-chain graph
crowding, and weight-free multi-relation balance. These are additive pieces of
the forward-forcing chain. The next measured implementation should retain them
while adding backbone hydrogen-bond assembly and a hard-exclusion
representation that resolves side-chain placement more fully. That is a
positive engineering continuation, not a theoretical wall.

### Target-incapable backbone hydrogen-bond assembly

V11 retains the complete v10 relation and adds a generated backbone
donor/acceptor constitution. Donor and acceptor directions are constructed from
the generated N/CA/C frames; proline is exactly non-donor; the endogenous
adjacent C-alpha step supplies normalization; deterministic strongest-first
selection gives each donor and acceptor unit capacity. The runtime contains no
target coordinate, O/H target atom, empirical distance cutoff, angular cutoff,
fitted energy, reward, template or learned parameter.

The sealed 24-residue target-isolated development run generated 108 eligible
relations and selected 17 donor/acceptor pairs. Post-seal same-index comparison
measured `KTI` at TM `0.999701361058143`, dRMSD
`0.006615982459036663 Å`, and Kabsch RMSD `0.008642163509649983 Å`;
`TLTG` measured TM `0.6441498215858261`. These advance the best length-three
and length-four local values of the matched v10 24-residue route. The complete
receipt also preserves whole-prefix TM `0.020183289658017203`, dRMSD
`7.074317396421713 Å`, and every length-three, -four and -five window as
development data, not as a Maria conclusion, failed prediction or theoretical
limit.

V10 therefore remains the current whole-chain route while v11 supplies the
active hydrogen-bond continuation. The next generated relation separates the
alpha `i -> i+4` topology from longer inter-strand pairings and combines it
with spatially complete side-chain hard exclusion. This is a refinement of an
already executable relation, not a theorem-derived wall. Maria decides whether
and when the development relation is promoted or extended to the full chain.

### Topology-separated global-capacity continuation

V12 executes the first topology separation without altering the v11 seal. The
alpha class is exactly donor `i+4` to acceptor `i`; the longer class contains
non-local inter-strand candidates at sequence separation greater than four.
Both use generated peptide frames and endogenous adjacent-step normalization,
then enter as independent ordinal relations. A single global matching retains
one capacity for every donor and acceptor across both classes; there is no
topology weight, empirical cutoff, fitted energy, target or template.

The source-bound target-isolated 24-residue run was sealed before comparison.
It generated 85 eligible rows and selected 18 pairs: five exact alpha and
thirteen longer candidates. Relative to v11, whole-prefix TM improved from
`0.020183289658017203` to `0.030203624938133732`, and C-alpha dRMSD improved
from `7.074317396421713 Å` to `6.152785745760267 Å`. The best local TM rows
were mixed: length three moved from v11's `0.999701361058143` to
`0.9864217459387982`; length four from `0.6441498215858261` to
`0.5711146956368334`; and length five improved slightly from
`0.24626050864035634` to `0.24779131281385336`. The complete windows are
retained as mixed local development data. They do not establish a theoretical obstruction; the next refinement
must preserve the whole-prefix orientation advance while recovering the local
geometry retained by v11. Maria determines the conclusion and next direction.

### Retained local plus topology-separated complete-chain continuation

V13 retains v11's undifferentiated unit-capacity local backbone assembly beside
v12's independent alpha and longer inter-strand relations. All fifteen
relations enter the same permutation-invariant ordinal balance. No target,
template, fitted weight, empirical cutoff, reward, learned parameter or mixing
coefficient enters selection.

The 24-residue execution was sealed before comparison and recovered the best
local geometry while retaining a whole-prefix advance over v11. It reached
whole-prefix TM `0.025439036509863604` / dRMSD
`7.016435338321138 Å`; best length-three TM `0.9991385703352215`, best
length-four TM `0.6488923284461807`, and best length-five TM
`0.25764238229583347`. Relative to v12 it improved 14/22 length-three,
12/21 length-four and 12/20 length-five windows.

The same source-bound protocol then completed all 76 residues and sealed the
states and prediction before target access. Post-seal evaluation records
whole-chain TM `0.14226877551271516` and C-alpha dRMSD
`7.872750334234049 Å`. Relative to v10, TM advances by
`0.05193613924244425` (**57.4943%**), hard exclusions fall from 76 to 48,
and the strongest local rows advance to `TLE` at
`0.9984764349723149` TM / `0.014272729737428871 Å` dRMSD and `IFAG` at
`0.7777978001921849` TM. The advance propagates across 43/53 length-24,
40/45 length-32 and **29/29 length-48** same-index windows. The complete
pairwise-distance construction remains the active development requirement;
these applied results establish a constructive advance and do not establish a
theoretical obstruction.

The sealed V13 source is preserved unchanged. A separate single-build
execution candidate reuses one identical coordinate construction across the
unchanged v9/v12/v13 relations. It matched all 23 selected-path prefix relation
tuples and every complete 24-residue selection field exactly, while reducing
wall time from `310.17 s` to `240.21 s` (**22.5554%**). This is a lossless
computational implementation improvement and may enter only through a new
source-bound protocol version.

### Exact hydrogen-bond successor continuity gate

V14 derives two additional integer relations from the already assembled
unit-capacity topology pairs. Alpha continuity counts same-direction successor
bonds; inter-strand continuity counts parallel or antiparallel successor
bonds. One is the exact successor of residue order. No distance or angular
cutoff, weight, target, template, reward, fitted energy or learned quantity is
introduced.

The source-bound selector passed sealed 24- and 32-residue blind gates before
comparison. At 24 residues it held one alpha and one inter-strand continuity
edge; at 32 residues it held one alpha and two inter-strand edges. Both gates
selected state paths and PDB files byte-identical to matched v13, so the formal
post-seal 32-residue comparison remains TM `0.07299987461043171` / dRMSD
`5.983598069677243 Å`. This is zero predictive delta for the current relation,
not a theoretical limit. It does not justify spending a complete 76-residue
run in its present form. The single-build implementation remains a secured
engineering advance: matched 32-residue wall time falls from `513.96 s` to
`283.38 s` (**44.8634%**). The next predictive derivation moves to spatial
side-chain exclusion while retaining v13 and this lossless execution route.

### Spatial side-chain exclusion gates

V15 constitutes the first target-incapable spatial side-chain exclusion. Each
generated N/CA/C residue frame supplies the positive L-chiral half-space; the
exact side-chain heavy-atom graph count and its integer successor supply a
dimensionless share of the generated adjacent C-alpha step. Non-neighbour
command points inside that same generated step are excluded. No target,
template, rotamer, empirical radius, imported distance table, fitted weight,
reward or learned parameter enters the selector.

The sealed 24-residue V15 gate is active: it changes 21/24 states relative to
v13 and reduces the spatial census from 10 excluded pairs / 145 possible
heavy-atom encounters in the v13 structure to 3 pairs / 39 encounters. Its
strongest five-residue window advances by 11.96% to TM
`0.28845209836335417`. Whole-prefix TM is `0.012423768859676975` and dRMSD is
`7.68413561682186 Å`, so this version is retained as discriminating development
evidence rather than substituted for the stronger complete-sequence v13
route.

V16 separates two exact facts that V15 combined: existence of an excluded
residue pair is one binary hard exclusion, while the side-chain graph
Cartesian product is a recorded encounter census. Its sealed 24-residue gate
improves over V15 to TM `0.0126289266228606` and dRMSD
`7.522769416858055 Å`, while preserving the same best local scores. Identity
at 23/24 selected states localises the next work beyond exclusion
multiplicity: spatially instantiate the exact side-chain graph and branches
rather than representing a whole residue by one command point. A 76-residue
V15/V16 trial is not recommended before that continuation passes the same
24-residue gate. This is cumulative development evidence and resource
direction, not a theorem-derived obstruction or a Maria-declared loss.

V17 spatially instantiates the exact covalent side-chain graph. Integer graph
depth supplies the outward coordinate in each generated positive L-chiral
residue frame; centered sibling rank supplies branch coordinates, alternating
the remaining frame axes by depth parity. Atom reach is the exact `n/(n+1)`
share of the generated adjacent C-alpha step, and the encounter unit is its
`1/2` fold. One non-neighbour residue pair with any atom encounter is one
binary hard exclusion. No target, template, rotamer, empirical bond geometry,
radius, fitted cutoff, weight, reward, or learned value enters selection.

The sealed V17 L24 route records 6 excluded graph pairs and 16 atom
encounters. It advances whole-prefix TM over V15/V16 to
`0.016764131428767547` and advances V13's strongest length-five local TM by
9.21% to `0.28138048245022396`. Its first divergence from V13 is residue 5,
with whole-prefix dRMSD `8.251207613480005 Å`; applied comparison therefore
locates early local graph pruning as the next placement question.

V18 makes the hard relation constitutional and hierarchical. Backbone and
side-chain graph exclusions remain the exact lexicographic vector
`(backbone, sidechain_graph)` rather than a sum, multiplier, fitted scalar, or
weighted score. The sealed L24 execution selects all 24 V17 states and a
byte-identical PDB, preserving every global and local measurement. This exact
output closes the hard-fact ordering and demonstrates that scalar hard-stratum
combination did not cause the final V17 path.

V19 retains V13's local relations unchanged and moves the explicit graph hard
relation to complete-prefix assembly only. The sealed L24 output retains
22/24 V13 states and first diverges at residue 22. Whole-prefix TM advances
from `0.025439036509863604` to `0.025544854782528364` (**0.415968%**) and
C-alpha dRMSD improves from `7.016435338321138 Å` to
`7.005403396485503 Å` (**0.157230%**). The best length-four and length-five
TM rows remain exactly `0.6488923284461807` and `0.25764238229583347`, while
two same-index rows improve at each length. Its final hard vector is
`(5 backbone, 5 sidechain_graph)`. This is the first explicit graph route to
improve both sealed L24 global measures over V13 while preserving its strongest
length-four and length-five local geometry. The next resource-directed gate is
a matched sealed L32 cumulative development benchmark; successful propagation
there supports a subsequent L76 development trial. Maria alone decides whether
and when either run occurs.

## Preserved development evidence, not attributed conclusions

Selector v2 receipts remain intact because they contain useful target-isolation,
prefix, ladder and continuation evidence. They also bind the old mixed-purpose
modules, so v2 is preserved as development evidence rather than used as the
clean continuation route.

The following pre-project or legacy files contain target-guided, empirical,
tuned, stochastic, or otherwise untraced mechanisms and are excluded from the
active v3 runtime closure:

- `tools/beam_search_engine.py`
- `tools/blind_24_lattice_solver.py` (v1 score and mixed helper module)
- `tools/discrete_assembly_engine.py`
- `tools/predict_structure.py` beyond the protected construction boundary
- `tools/rotamer_geometry.py`
- `tools/sft_integer_engine.py`
- `tools/sft_positive_integer_engine.py`
- the v1 protocol and evaluator

Their executions, output filenames, scores, plateaus or errors are not Maria
Smith's failed predictions, findings or losses. They are historical development
artifacts unless Maria explicitly adopts a conclusion from named data.

## Executable gate

Run:

```sh
python3 -m tools.verify_protein_forcing_registry
python3 -m unittest tests.test_protein_forcing_registry \
  tests.test_protein_backbone_geometry_v1 tests.test_blind_selector_v3 -v
```

The registry verifier halts if:

- any Protein source in scope lacks a provenance class;
- the inherited 315-file compiler boundary changes;
- a source is assigned more than one primary class;
- a forbidden legacy module enters the v3 runtime import closure;
- any v3 source differs from its registered SHA-256; or
- the isolated geometry ceases to replay the protected construction exactly.

Generated PDBs and campaign receipts are evidence rather than forcing source.
They are bound by the protected construction manifest or their immutable seals.
All 78 tracked PDBs are also exhaustively classified: two experimental
references, one protected target-assisted construction, eleven sealed v2
development outputs, four sealed v3 blind predictions, one sealed v4 auxiliary
development output, two sealed v5 applied development outputs, and thirty-nine
legacy pre-project development artifacts, plus the three sealed v6-v8 and
three sealed v9-v10, one sealed v11, one sealed v12, three sealed v13, two
sealed v14, one sealed v15, one sealed v16, one sealed v17, one sealed v18 and
one sealed v19 development outputs described above.
Their complete path-and-content census is hash-bound by the registry; both v2
aggregate seals are reverified. Legacy filenames such as `predicted`,
`optimized`, or `autonomous` do not confer result or authorship status.
The remaining three non-JSON/non-source files outside the compiler and PDB
inventories are also bound: repository configuration, the historical compiled
3D-law artifact, and the protected construction development log.

## Current stage and next forward work

The audit removes silent inheritance while preserving the full constructive
chain. The secured v3 route remains the blind baseline; v5 establishes the
four-residue inter-window continuation; and v13 is the current complete-
sequence route, carrying signed alpha/beta geometry, binary mode preservation,
formal charge, exact side-chain graph crowding, weight-free ordinal balance,
and retained local plus topology-separated hydrogen-bond assembly. Its sealed
76-residue prediction improves whole-chain TM by 57.49% over v10.

V17 has now spatially instantiated the exact side-chain graph and branch
topology; V18 has separated its hard fact from the parent backbone exclusion;
and V19 has located that graph relation at complete-prefix assembly while
preserving V13's secured local frontier. V19 is the current L24 global
continuation candidate: it improves both whole-prefix TM and dRMSD over V13,
retains 22/24 states, and preserves the strongest length-four and length-five
local rows. V13 remains the current complete 76-residue route until a longer
V19 development execution is completed.

The next state is to test V19 at a matched sealed L32 cumulative development
gate, preserve the exact hard vector and local/global separation, and measure
whether the improvement propagates beyond the final L24 region. A successful
L32 gate supports proceeding to L76. The single-build reuse path and cached
complete-prefix graph calculations are also the measured optimisation
direction, provided exact sealed output identity is preserved. New relations must
be named in their own immutable manifest, traced
through the engine standard, source-bound, tested, and executed on sealed real
sequence before comparison. The protected complete-lattice construction, the
forced secondary-structure coordinates, and the successive sealed blind local
and whole-chain results establish an executable continuation and no
theorem-derived wall at the current stage. Maria decides when development
evidence earns an official run and what conclusion the data supports.
