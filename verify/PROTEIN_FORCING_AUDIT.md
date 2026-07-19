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
All 60 tracked PDBs are also exhaustively classified: two experimental
references, one protected target-assisted construction, eleven sealed v2
development outputs, four sealed v3 blind predictions, one sealed v4 auxiliary
development output, two sealed v5 applied development outputs, and thirty-nine
legacy pre-project development artifacts.
Their complete path-and-content census is hash-bound by the registry; both v2
aggregate seals are reverified. Legacy filenames such as `predicted`,
`optimized`, or `autonomous` do not confer result or authorship status.
The remaining three non-JSON/non-source files outside the compiler and PDB
inventories are also bound: repository configuration, the historical compiled
3D-law artifact, and the protected construction development log.

## Remaining forward work

The audit removes silent inheritance; it does not declare development complete.
The secured v3 route remains the blind baseline and v5 is the active applied
inter-window development route.  New relations must be named in their own
immutable manifest, traced through the engine standard, source-bound, and tested
before a registered execution.  Maria decides when development evidence earns
an official run and what conclusion the data supports.
