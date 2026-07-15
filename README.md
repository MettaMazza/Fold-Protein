# Fold Protein

> **Part of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything).** Sibling zero-parameter engines: [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Go](https://github.com/MettaMazza/Fold-Go).

Parameter-free protein folding. The native state is the fold's **fixed point**; folding is
**descent** to it — Levinthal's paradox dissolved (native in two fold steps, not a 10⁵⁰ search) —
and backbone geometry falls out as counted fold orbits. The predictor works **from the sequence
alone**; the experimental structure is only ever a held-out yardstick. **Zero parameters — no
fitted force field, no trained potential.**

Duplicated from the Smithian Fold Theory project as an independent workspace at the validated
state of the protein work.

## Quick start

```sh
# 1. The law — self-contained C proofs (C compiler only); every line must read "ok"
cd verify
cc -O2 -o test_protein_folding    test_protein_folding.c    && ./test_protein_folding
cc -O2 -o test_protein_folding_3d test_protein_folding_3d.c && ./test_protein_folding_3d
cd ..

# 2. Reproduce the flagship finding: TM-score of the beam prediction vs experiment
python3 calculate_tm.py verify/1ubq_beam.pdb verify/1ubq.pdb      # -> TM-score: 0.6962

# 3. Fold a structure FROM SEQUENCE (numpy required; the reference is never used to guide)
python3 tools/predict_structure.py <one-letter-sequence> <output.pdb>
```

## The rule that governs this workspace

**Read [`AGENT.md`](AGENT.md) first.** Every derivation and expansion must route through the
engine and return to the one validated anchor with **no law or constraint violation** — counted
or forced values only, zero parameters, everything traced to the One, the `forced_to_be` C proofs
intact. The cardinal rule specific to folding: **never fold *to* the target** — the predictor is
blind from sequence, and the experimental PDB is read only on the scoring side. A structure fit to,
seeded from, or aligned into the answer is not a result. Validation is done in this directory
(see `AGENT.md` §3).

## Layout

| Path | What |
|------|------|
| `constants/protein_folding*.ep` | the fold law: descent to the fixed point, the backbone orbits |
| `foundation/*.ep` | exact integers/fractions, the One and the fold, the enforcement guards |
| `verify/test_protein_folding*.c` | self-contained C proofs (primary law validation) |
| `tests/test_protein_folding*.ep` | the same law in source |
| `tools/predict_structure.py` | the folding pipeline (sequence → 3D backbone → PDB) |
| `tools/*_engine.py`, `blind_24_lattice_solver.py`, `rotamer_geometry.py` | the folders / optimisers |
| `calculate_tm.py` | TM-score (Kabsch) vs an experimental structure — the scoring boundary |
| `verify/1ubq.pdb`, `verify/1cop.pdb` | experimental references (held out; scoring only) |
| `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` | the predicted structures (the findings) |
| `papers/` | Levinthal's Paradox Dissolved · Super Parity (Zero-Parameter Protein Folding) |
| `compiler/` | bundled ErnosPlain toolchain (`ernos` also on PATH) |

## Validated record (reproduced by the commands above)

- Levinthal dissolved: native = fold's fixed point `fold(1)=1`; descent reaches native in **2 steps**
- Backbone orbits: α-helix φ→**1/3**, β-sheet φ→**2/3** (period-2), ψ→native
- Flagship prediction recovers experimental ubiquitin to **TM = 0.6962**, scored blind

## Papers & findings

- [Levinthal's Paradox Dissolved: Parameter-Free Protein Folding and the Genetic Code](papers/Levinthals_Paradox_Dissolved_Parameter_Free_Protein_Folding_and_the_Genetic_Code.md)
- [Super Parity: Zero-Parameter Protein Folding](papers/Super_Parity_Zero_Parameter_Protein_Folding.md)
- Predicted structures: `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` (scored with `calculate_tm.py`)

---

Part of the **[Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything)** — one axiom, zero parameters, everything forced from the One.
