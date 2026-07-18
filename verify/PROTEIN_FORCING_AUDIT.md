# Fold Protein forcing and provenance audit

**Audit date:** 18 July 2026  
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

The v3 protocol accepts exactly `run_id` and `sequence`, checks all source
hashes, refuses an existing output directory, and seals its state path and PDB
before any comparison.

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
All 53 tracked PDBs are also exhaustively classified: two experimental
references, one protected target-assisted construction, eleven sealed v2
development outputs, and thirty-nine legacy pre-project development artifacts.
Their complete path-and-content census is hash-bound by the registry; both v2
aggregate seals are reverified. Legacy filenames such as `predicted`,
`optimized`, or `autonomous` do not confer result or authorship status.
The remaining three non-JSON/non-source files outside the compiler and PDB
inventories are also bound: repository configuration, the historical compiled
3D-law artifact, and the protected construction development log.

## Remaining forward work

The audit removes silent inheritance; it does not declare development complete.
The clean v3 route now provides the correct base for the active blind benchmark
campaign. New selector relations must be named in the v3 manifest, traced through
the engine standard, source-bound, and tested before a registered execution.
Maria decides when that development earns a real run and what conclusion the
result supports.
