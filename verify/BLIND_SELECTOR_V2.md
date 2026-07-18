# Blind selector v2 — sequence forward-forcing execution

Selector v2 is the target-isolated sequence forward-forcing engine. It extends
the secured Super Parity construction by selecting a 24-lattice path from amino-
acid sequence and generated geometry without target coordinates in the selector.

Compared with selector v1, v2 removes the 8 Å contact cutoff, 3.2 Å clash
cutoff, and contact-reward scale. Candidate geometry is ordered by quantities
normalised to the generated chain's own mean adjacent Cα step:

1. the number of non-neighbour pairs closer than that endogenous step;
2. hydrophobic-pair dispersion relative to all non-neighbour dispersion;
3. radius-of-gyration squared relative to the adjacent-step scale.

The engine tests a One-normalised self-exclusion relation together with
hydrophobic dispersion, compaction, lexicographic ordering, and a registered
24-path capacity. The engine, not an agent label, determines whether each route
is forced or halts. The selector reads only `run_id` and amino-
acid `sequence`; native coordinates and target-derived quantities remain outside
the process. Evaluation may occur only after the prediction directory is sealed.

## Sequence-only diagnostic panel

`blind_selector_v2_panel.json` preregisters five eight-residue controls spanning
mixed, hydrophobic, charged, glycine/proline, and alternating compositions. The
panel runner accepts no target or structural score, executes each sequence through
the sealed v2 runner, and hash-binds every individual seal into one panel seal.

The 2026-07-18 execution in `blind_selector_v2_panel_run_20260718/` completed all
five registered sequences with deterministic sequence-only outputs and hash-bound
receipts. The registered ubiquitin length ladder subsequently completed all six
prefixes through the full 76-residue sequence.

## Target-free prefix continuation receipt

`blind_selector_v2_prefix_consistency_20260718.json` hash-binds the verified
length-ladder registration, ladder seal, and every selected-state file. It
compares only Cα-active state decisions in each shorter prefix with the next
registered prefix and never opens a target. The exact identical-state counts are
6/7, 14/15, 16/23, 30/31, and 46/47 for the 8→16, 16→24, 24→32, 32→48, and
48→76 comparisons. This is a measured implementation result only. The engine
determines forcing or halt; Maria Smith assigns any project conclusion and
decides when the selector receives a real blind run.

`tools/trace_blind_ladder_decisions_v2.py` continues that audit entirely inside
the selector. For every changed active state it records the two exact lattice
states, their dihedral angles, each chosen prefix's dimensionless topology key,
and their lexicographic relation. It also checks whether the shared beam-frontier
trace is byte-for-byte identical before the shorter sequence ends. The trace
binds the verified ladder, consistency receipt, analyzer source, and every state
file; it reads no target and assigns no project conclusion.

The sealed 2026-07-18 trace records changed-state counts of 1, 1, 7, 1, and 1
across the five consecutive length comparisons. In all five comparisons the
shared beam-frontier trace is byte-for-byte identical through the shorter
active range. Each later final path therefore remains traceable to the same
registered frontier construction and the selector's explicit continuation and
lexicographic ordering, with the complete per-state relations preserved in
`blind_selector_v2_decision_trace_20260718.json`.

The next target-free relation is continuation lineage: a longer candidate is a
descendant exactly when its active-state tuple begins with the registered
shorter winner. `tools/trace_selector_continuation_lineage_v2.py` replays the
same 24-path frontier and records the exact descendant count, best rank, first
displacement, and first extinction at every added active state. It halts if the
registered shorter winner is not reproduced at its own frontier and binds the
selector source, analyzer source, verified ladder, and every selected-state
file.
