# AGENT.md — the law this workspace is held to

You are working on **Fold Protein**: parameter-free protein folding. The native state is
the fold's **fixed point**, folding is **descent** to it (not a search of an astronomical
space — Levinthal's paradox dissolved), and backbone geometry falls out as counted fold
orbits. The predictor works **from sequence alone**; the experimental structure is only ever
a held-out yardstick. It carries **zero parameters — no fitted force field, no trained
potential**. This file is binding. Read it before you change anything, and route every change
back through the validation in **this directory**.

---

## 0. The one validated anchor (do not regress it)

There is exactly one validated state, and it is the baseline every derivation and expansion
must return to. In this folder it is **proven, reproducibly, by the commands in §3**:

- **Levinthal dissolved (the law):** the native state is the fold's fixed point `fold(1) = 1`;
  folding is **descent** — `fold(3/4)=1/2`, `fold(1/2)=1` — reaching native in **two steps, not
  a 10^50 search** (`verify/test_protein_folding`).
- **Backbone geometry is a counted orbit:** α-helix φ folds to **1/3** and β-sheet φ to **2/3**
  (the two period-2 orbits), each ψ decaying to native `1` (`verify/test_protein_folding_3d`).
- **The finding, refereed against experiment:** the flagship prediction scores **TM = 0.6962**
  against the experimental ubiquitin structure `verify/1ubq.pdb` — reproduce with
  `python3 calculate_tm.py verify/1ubq_beam.pdb verify/1ubq.pdb`. The full write-ups are in
  [`papers/`](papers/) (Levinthal's Paradox Dissolved; Super Parity — Zero-Parameter Protein Folding).

If any change makes any of the above stop reproducing, the change is wrong until proven
otherwise. **The anchor is the arbiter, not your intent.**

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
3. **Every value traces back to the One.** The only assumed thing is the One; everything else is
   built by the two moves (fold and take) and the two generators **`b = 2`, `c = 3`**. The descent
   dynamics and the backbone orbits are derived, not posited.
4. **The form is forced, not just its parts** (`foundation/assembly_enumeration.ep`,
   `foundation/form_enforcement.ep`): `forced_to_be` **halts** on any un-forced value. The C proofs
   put the fixed point, the descent, and the orbits through this guard.
5. **The target is sealed — never fold *to* the experimental structure.** This is the protein
   form of "measured values are sealed." The predictor runs **blind from the sequence**; the
   experimental PDB is read **only** on the scoring side (TM-score / dRMSD in `calculate_tm.py`)
   to take a difference. Using the reference coordinates to guide, seed, align-into, or select the
   prediction is the cardinal violation — it forges the result. (The project already retracted an
   invalid target-informed "blind" section for exactly this reason; do not reintroduce it.)

**The guards are the point, not obstacles.** If a C proof halts, a constraint fired — fix the
derivation, never weaken `forced_to_be` or the proofs. If a score is low, the predictor is weak —
improve the *counted* physics, never lower the bar or peek at the target.

---

## 2. The routing rule (this is the instruction)

**Every derivation and every expansion of the corpus must route through the engine and return to
the one validated anchor with no law or constraint violation.** For any change — a new backbone
term, a bigger protein, a better search, a new lattice:

1. Express the new quantity as **counted or forced** — in the `.ep` law (`constants/protein_folding*.ep`,
   using only `foundation/`) and/or in the folding pipeline (`tools/predict_structure.py` and the
   engines), with **no fitted parameter and no read of the target structure**.
2. **Rebuild through the engine** — the `.ep` law via `ernos`, the C proofs via `cc` (§3). A halt is
   a guard firing; fix the derivation, do not bypass it.
3. **Re-run the full validation in this directory** (§3): the Levinthal descent and the backbone
   orbit proofs must still pass, and the prediction must be scored **blind** by TM/dRMSD against the
   held-out experimental structure — the anchor score must not regress.
4. Only a change that **passes every check, stays parameter-free, and never touches the target**
   is admissible. Anything else is reverted.

A structure that scores well because it was fit to, seeded from, or aligned into the answer is not
a result — it is the one thing this work exists to disprove is necessary.

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

**C. Fold from sequence, then score blind (needs `python3` + `numpy`):**
```sh
# predict a structure FROM SEQUENCE ONLY (the experimental arg, if given, is for scoring/logging
#   — never to guide the fold):
python3 tools/predict_structure.py <one-letter-sequence> <output.pdb>
# score any prediction against the held-out experimental structure:
python3 calculate_tm.py verify/1ubq_beam.pdb verify/1ubq.pdb     # -> TM-score: 0.6962 (the anchor)
```
The engines (`tools/sft_integer_engine.py`, `tools/sft_positive_integer_engine.py`,
`tools/blind_24_lattice_solver.py`, `tools/discrete_assembly_engine.py`, `tools/rotamer_geometry.py`)
import `predict_structure` and read `verify/*.pdb` relative to this folder — run them from the folder
root (`python3 tools/<engine>.py ...`).

---

## 4. Where things live

- `constants/protein_folding.ep`, `constants/protein_folding_3d.ep` — the fold law (descent to the
  fixed point; the backbone orbits). Import only `foundation/`.
- `foundation/*.ep` — exact integers/fractions, the One and the fold, the enforcement guards.
- `verify/test_protein_folding*.c` — the self-contained C proofs (the primary law validation).
- `tests/test_protein_folding*.ep` — the same in source.
- `tools/predict_structure.py` — the folding pipeline (sequence → 3D backbone → PDB).
- `tools/*_engine.py`, `tools/blind_24_lattice_solver.py`, `tools/rotamer_geometry.py` — the folders/optimisers.
- `calculate_tm.py` — TM-score (Kabsch-aligned) vs an experimental structure; the scoring boundary.
- `verify/1ubq.pdb`, `verify/1cop.pdb` — experimental references (held out; scoring only).
- `verify/1ubq_*.pdb`, `./1ubq_autonomous*.pdb` — the predicted structures (the findings).
- `papers/` — the write-ups.
- `compiler/` — the bundled ErnosPlain toolchain (`ernos` also on PATH).

The finding this workspace exists to protect: **folding as descent to a counted fixed point —
native geometry from the sequence alone, zero parameters, the target never touched, and a real
experimental structure recovered to TM 0.696.** Keep it that way.
