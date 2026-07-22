# Evidence accompanying the standalone Blind Predictive Super Parity paper

This evidence release accompanies Maria Smith's standalone paper *From One
Self-Proven Theorem to Blind Protein Structure* (DOI
`10.5281/zenodo.21482128`). The paper is the primary publication artifact and
the authoritative current synthesis of Fold Protein.

## Central empirical result

Protein Material Architecture V1 predicts the complete 76-residue ubiquitin
backbone while the experimental target and comparison scores are inaccessible
to execution. The prediction is sealed before comparison and measures:

- `0.9891211351471241` `TM_repo`;
- `0.2608575407959516 Å` unique-pair Cα dRMSD; and
- `0.3261459535125402 Å` Kabsch Cα RMSD.

The execution restores 576 exact states at each residue, performs 43,776 raw
state trials, and records zero trained weights, zero fitted parameters, zero
candidate orderings and zero target accesses.

## Evidence layers

1. The PDF and Markdown paper state the scientific argument, method, metrics,
   provenance and blind predictive result.
2. `protein_material_architecture_v1_applied_evidence.json` binds the complete
   candidate census, source hashes, seal, prediction hash and post-seal metrics.
3. The material relation, admission and protocol receipts expose the exact
   sequence/generated-geometry relation and its machine-checked closure.
4. The sealed R2 execution directory contains the input, selected states, PDB,
   seal and post-seal evaluation.
5. The forcing registry and audits distinguish engine-closed relations,
   observational derivation, applied development evidence and author conclusions.
6. The recovery evidence preserves every available complete positive candidate
   rather than allowing a single emitted row or agent interpretation to erase
   empirical data.
7. The source, constants and tests reproduce the mathematical and execution
   surfaces described in the paper.

## Exact execution identity

The material relation stores generated geometry as exact hexadecimal
floating-point identities rather than as tolerance matches. The recorded
execution uses CPython 3.9.6 and NumPy 2.0.2; `requirements-reproduction.txt`
fixes that numerical implementation identity for byte-exact reproduction. This
version binding is an implementation identity, not a fitted model parameter.

## Evidentiary status

Opaque predictive reliability and transparent empirical derivation are not the
same evidentiary object. A black-box system can be repeatedly measured as
reliable; that validates its output performance. Fold Protein establishes the
higher evidentiary chain by exposing the proposed law, its derivation, the
complete state domain, the blind execution boundary, the sealed consequence and
the experimental comparison.

The two earlier Protein papers are retained in the repositories and their
existing Zenodo records as chronological development artifacts. This standalone
paper supersedes them as the current statement of the work.
