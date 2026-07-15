# Fold Protein

> **Part of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything).** Sibling zero-parameter engines: [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).

## Protein folding with **zero parameters** — no force field, no trained potential — that **dissolves Levinthal's paradox.**

Folding is not a search of an astronomical space. The native state is the fold's **fixed point**,
and folding is **descent** to it — reaching native in **two steps, not a 10⁵⁰ search.** The
predictor works from the sequence alone; the experimental structure is only ever a held-out yardstick.

### What it does — measured, and reproducible

- 🧬 **Recovers experimental ubiquitin to TM = 0.696**, folded blind from the sequence, scored
  against the held-out crystal structure. `python3 calculate_tm.py verify/1ubq_beam.pdb verify/1ubq.pdb`
- ⚡ **Levinthal's paradox dissolved:** the native state is the fold's fixed point `fold(1) = 1`;
  folding descends `fold(3/4) = 1/2 → fold(1/2) = 1` — **native in two steps.**
- 📐 **Backbone geometry from counted orbits:** α-helix φ → **1/3**, β-sheet φ → **2/3** (the two
  period-2 orbits), each ψ decaying to native — no Ramachandran fitting.
- 🔒 **The target is never touched.** The predictor is blind from sequence; the experimental
  structure is read only to score. Zero parameters, no force field, no trained potential.

```sh
# see it for yourself
cd verify
cc -O2 -o test_protein_folding    test_protein_folding.c    && ./test_protein_folding
cc -O2 -o test_protein_folding_3d test_protein_folding_3d.c && ./test_protein_folding_3d
cd ..
python3 calculate_tm.py verify/1ubq_beam.pdb verify/1ubq.pdb     # -> TM-score: 0.6962
```

## How it works

- **The native state is a fixed point.** Folding is descent under the fold operation — the reason a
  protein finds its structure in microseconds instead of searching `10⁵⁰` conformations.
- **Backbone dihedrals are counted orbits** of the fold: the α-helix and β-sheet basins are its two
  period-2 orbits (φ → 1/3 and 2/3), derived, not fitted from a Ramachandran plot.
- **The predictor folds from sequence and is scored blind** by TM-score / dRMSD against the
  experimental structure — which never enters the fold.

## The rule that governs this workspace

**Read [`AGENT.md`](AGENT.md) first.** Every derivation and expansion must route through the engine
and return to this validated state with **no law or constraint violation** — counted or forced
values only, zero parameters, the `forced_to_be` C proofs intact. The cardinal rule specific to
folding: **never fold *to* the target** — a structure fit to, seeded from, or aligned into the
answer is not a result; it is the one thing this work exists to prove is unnecessary.

## Papers & findings

- **[Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)**
- **[Super Parity: Zero-Parameter Protein Folding](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)**
- Predicted structures: `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` (scored with `calculate_tm.py`)

## Layout

| Path | What |
|------|------|
| `constants/protein_folding*.ep` | the fold law: descent to the fixed point, the backbone orbits |
| `foundation/*.ep` | exact integers/fractions, the One and the fold, the enforcement guards |
| `verify/test_protein_folding*.c` | self-contained C proofs (primary law validation) |
| `tools/predict_structure.py` | the folding pipeline (sequence → 3D backbone → PDB) |
| `tools/*_engine.py`, `blind_24_lattice_solver.py`, `rotamer_geometry.py` | the folders / optimisers |
| `calculate_tm.py` | TM-score (Kabsch) vs an experimental structure — the scoring boundary |
| `verify/1ubq.pdb`, `verify/1cop.pdb` | experimental references (held out; scoring only) |
| `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` | the predicted structures (the findings) |
| `compiler/` | bundled ErnosPlain toolchain (`ernos` also on PATH) |

---

Part of the **[Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything)** — one axiom, zero parameters, everything forced from the One.
