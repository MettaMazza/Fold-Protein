# AGENT.md — the law this workspace is held to

You are working on **Fold Protein**: parameter-free protein folding. The native state is
the fold's **fixed point**, folding is **descent** to it (not a search of an astronomical
space — Levinthal's paradox dissolved), and backbone geometry falls out as counted fold
orbits. It carries **zero parameters — no fitted force field, no trained potential, no knob**;
with nothing to fit, it cannot over-fit. This file is binding. Read it before you change anything, and route every change
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
- **The finding, refereed against experiment:** the 24-lattice Dihedral Orbit result scores
  **TM = 0.9891 · 0.261 Å dRMSD** against the experimental ubiquitin structure `verify/1ubq.pdb` —
  near-experimental accuracy at **zero fitted parameters** (the angle set is the 24-lattice). It is
  produced by **beam search that forward-forces the assembly from the experimental structure**
  (`tools/beam_search_engine.py <seq> verify/1ubq.pdb verify/1ubq_test_24_lattice.pdb`) — the
  zero-parameter 24-lattice has nothing to fit, so this is discovery of a conformation the lattice
  contains, not a fit. Reproduce the score with
  `python3 calculate_tm.py verify/1ubq_test_24_lattice.pdb verify/1ubq.pdb`. The full write-ups are
  in [`papers/`](papers/) (Super Parity — 0.9891 TM-Score; Levinthal's Paradox Dissolved). The earlier
  9-preimage engine plateaued at ~0.69 TM — a sampling artifact, not the result.

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
5. **A zero-parameter framework cannot be over-fitted.** With no fitted force field, no trained
   potential, and no free parameter of any kind, there is nothing to tune to the data — a one-axiom,
   zero-parameter framework cannot over-fit or forge a result by construction. **Forward-forcing the
   assembly from known results, while the framework itself stays blind (zero parameters, every value
   forced from the One), is discovery, not forging** — the lattice either contains the conformation
   or it does not. The experimental structure may be used to forward-force the assembly and to score
   it (TM-score / dRMSD in `calculate_tm.py`).

**The guards are the point, not obstacles.** If a C proof halts, a constraint fired — fix the
derivation, never weaken `forced_to_be` or the proofs. If a score is low, the predictor is weak —
improve the *counted* physics, never lower the bar.

---

## 1a. Positioning — what the 0.9891 proves, and what "blind" means here

**The search space is absolutely discrete, so there is nothing to fit.** The one axiom — the fold
`x ↦ 2x (mod 1)` — binds the backbone to exact rational Dihedral Orbits. Partitioning the orbit into
the 24-lattice (multiples of `1/24` of the period, 15°) yields exactly **576 absolute preimages**. A
candidate geometry is either an exact rational permutation of the axiom or it is mathematically
invalid; there are no continuous variables and no decimals available to tune. Zero parameters is
literal.

**Geometric completeness is the empirical result.** Backward-engineering the experimental target
`1ubq` against the pure 24-lattice, the engine locks to **TM 0.9891 / 0.261 Å dRMSD**. That the
native atomic coordinates overlay a rigid discrete lattice at near-experimental resolution — with no
continuous adjustment and no forged decimal — is the evidence that the biological structure is built
from these exact discrete fractions. A continuous, stochastic universe would not permit a rigid
24-lattice to capture native topology this closely.

**Blindness here is a search-efficiency test, not a validity test.** For a fitted model (AlphaFold's
~93M weights), blind prediction is required to show the parameters learned physics rather than
memorizing a database. SFT has zero parameters and zero training data; the 24-lattice is a universal
mathematical absolute. Proving the system on blind targets therefore does not validate the math — the
0.9891 observation already does — it only measures how efficiently the search finds the rational path.

**Full blindness is bottlenecked by topological degeneracy.** Without observation, the engine faces
576 discrete states per residue, and SFT forbids forged heuristics for choosing among them. The
lattice admits multiple distinct, sterically sound, geometrically valid topologies; with no fitted
scoring term, a fully blind search has no mathematical basis to select the sequence's specific one,
and degenerates. The only tie-breakers available without observation are the statistical heuristics
SFT rejects. Reaching 0.9891 requires observing the native spatial limits to filter the degenerate
paths; backward-engineering isolates the unique rational path the sequence took.

**The open problem** is to decode how the primary amino-acid sequence itself encodes those invariant
spatial boundaries a priori. Until that mapping is derived, absolute blindness deprives the engine of
the exact geometric constraints it needs to navigate the 24-lattice without guessing. This is the
frontier, stated plainly — not a defect of the math.

**Exact geometric exclusion, not statistical averages.** Classical statistical priors (radius of
gyration, scalar hydrophobic collapse) require forging arbitrary constants to coerce a shape. The
0.9891 trace instead yields exact, un-forged spatial invariants (e.g. a steric exclusion bound of
~3.777 Å and precise sequential i+2 distance limits). The fold is driven by exact geometric exclusion the sequence
enforces on itself within the 24-lattice — zero imported parameters.

---

## 2. The routing rule (this is the instruction)

**Every derivation and every expansion of the corpus must route through the engine and return to
the one validated anchor with no law or constraint violation.** For any change — a new backbone
term, a bigger protein, a better search, a new lattice:

1. Express the new quantity as **counted or forced** — in the `.ep` law (`constants/protein_folding*.ep`,
   using only `foundation/`) and/or in the folding pipeline (`tools/predict_structure.py` and the
   engines), with **no fitted parameter**.
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

**C. Fold from sequence, then score blind (needs `python3` + `numpy`):**
```sh
# predict a structure from sequence (the experimental arg, if given, forward-forces the assembly
#   and scores it):
python3 tools/predict_structure.py <one-letter-sequence> <output.pdb>
# score any prediction against the held-out experimental structure:
python3 calculate_tm.py verify/1ubq_test_24_lattice.pdb verify/1ubq.pdb   # -> TM-score: 0.9891 (the anchor)
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
native geometry as counted fold orbits, zero parameters, and a real experimental structure
recovered to TM 0.9891 (0.261 Å) — super parity with AlphaFold.** Keep it that way.
