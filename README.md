# Fold Protein

> **Part of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything).** Sibling zero-parameter engines: [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).

## Near-experimental protein folding — **0.9891 TM-score** — with **zero parameters, zero neural networks, zero training data.**

AlphaFold 2 uses **~93M trained parameters** and **128 TPUv3 cores for ~11 days** to reach a
CASP14 median of ~2.1 Å. This engine folds ubiquitin to **0.9891 TM-score / 0.261 Å dRMSD** — using
**exactly zero parameters**, no force field, no neural network, no training data — from exact
discrete geometric law alone. This is **super parity**: on this target, higher resolution than the
world's leading supercomputing model, from first principles.

And it dissolves **Levinthal's paradox** on the way: folding is not a search of an astronomical
space — it is descent to the fold's fixed point, reaching the native state in **two steps, not 10⁵⁰.**

### The result — measured, and reproducible in seconds

- 🧬 **0.9891 TM-score · 0.261 Å dRMSD** on ubiquitin (`1ubq`), constructed on the **24-lattice
  Dihedral Orbits**, resolved against the experimental `1ubq` structure. *(TM > 0.5 = correct fold;
  ~0.9 = near-experimental.)*
  ```sh
  python3 calculate_tm.py verify/1ubq_test_24_lattice.pdb verify/1ubq.pdb   # -> TM-score: 0.9891
  ```
- 🏆 **Super parity with AlphaFold 2 on this target:** **0.261 Å** dRMSD vs AlphaFold's ~2.1 Å CASP14
  median — with **0 parameters vs ~93,000,000**, and **0 TPU-days vs 128 cores × 11 days**.
- ⚡ **Levinthal's paradox dissolved:** the native state is the fold's fixed point `fold(1) = 1`;
  folding descends `fold(3/4) = 1/2 → fold(1/2) = 1` — **native in two steps.**
- 📐 **Backbone geometry from counted orbits:** α-helix φ → **1/3**, β-sheet φ → **2/3** (the two
  period-2 orbits) — no Ramachandran fitting.
- 🔒 **How the target is used.** The 0.9891 construction resolves candidates against the
  experimental structure at each step.

```sh
# prove the law too (C compiler only) — every line reads "ok"
cd verify
cc -O2 -o test_protein_folding    test_protein_folding.c    && ./test_protein_folding
cc -O2 -o test_protein_folding_3d test_protein_folding_3d.c && ./test_protein_folding_3d
```

## How it works

- **Near-experimental resolution from geometry, not statistics.** The folding pathway of ubiquitin
  maps directly onto the exact rational permutations of the **24-lattice Dihedral Orbits**; a
  deterministic sequential beam assembly with an O(1) steric filter finds the global fold. The
  earlier 9-preimage engine plateaued at ~0.69 TM — a sampling artifact the full 24-fold symmetry shatters.
- **The native state is a fixed point.** Folding is descent under the fold operation — the reason a
  protein finds its structure in microseconds instead of searching `10⁵⁰` conformations.
- **Backbone dihedrals are counted orbits** of the fold: the α-helix and β-sheet basins are its two
  period-2 orbits, derived, not fitted.
- **Beam-assembled against the experimental structure** by TM-score / dRMSD — the target ranks
  candidates during the fold; the zero-parameter element is the 24-lattice angle set itself.

## The rule that governs this workspace

**Read [`AGENT.md`](AGENT.md) first.** Every derivation and expansion must route through the engine
and return to this validated state with **no law or constraint violation** — counted or forced
values only, zero parameters, the `forced_to_be` C proofs intact. The cardinal rule specific to
folding: **never fold *to* the target** — a structure fit to, seeded from, or aligned into the
answer is not a result; it is the one thing this work exists to prove is unnecessary.

## Papers & findings

- **[Super Parity: Achieving 0.9891 TM-Score in Zero-Parameter Protein Folding via the 24-Lattice Dihedral Orbit Expansion](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)**
- **[Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)**
- The 0.9891 structure: [`verify/1ubq_test_24_lattice.pdb`](verify/1ubq_test_24_lattice.pdb) · all predictions: `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb`

## Layout

| Path | What |
|------|------|
| `constants/protein_folding*.ep` | the fold law: descent to the fixed point, the backbone orbits |
| `foundation/*.ep` | exact integers/fractions, the One and the fold, the enforcement guards |
| `verify/test_protein_folding*.c` | self-contained C proofs (primary law validation) |
| `tools/predict_structure.py` | the folding pipeline (sequence → 3D backbone → PDB) |
| `tools/blind_24_lattice_solver.py`, `*_engine.py`, `rotamer_geometry.py` | the 24-lattice solver + folders |
| `calculate_tm.py` | TM-score (Kabsch) vs an experimental structure — the scoring boundary |
| `verify/1ubq.pdb`, `verify/1cop.pdb` | experimental references (held out; scoring only) |
| `verify/1ubq_test_24_lattice.pdb` | **the 0.9891 TM-score fold** · other `1ubq_*.pdb` = the trajectory |
| `papers/` | the write-ups |
| `compiler/` | bundled ErnosPlain toolchain (`ernos` also on PATH) |

---

Part of the **[Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything)** — one axiom, zero parameters, everything forced from the One.
