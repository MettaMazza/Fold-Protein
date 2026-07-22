# Evidence accompanying the standalone Blind Predictive Super Parity paper

This evidence release accompanies Maria Smith's standalone paper *From One
Self-Proven Theorem to Blind Protein Structure* (concept DOI
`10.5281/zenodo.21482127`). The paper is the primary publication artifact and
the authoritative current synthesis of Fold Protein.

## Central empirical result

Fold Protein executes 24 complete whole-structure predictions across four
preregistered panels. Every state path and PDB is sealed before the corresponding
experimental coordinates are opened. The aggregate post-seal result is:

- `0.9255486261999419` median `TM_repo`;
- `0.7833590149340738 Å` median Cα RMSD95;
- `0.9882113352098658` best whole-structure `TM_repo`; and
- 15 of 24 structures at or below AlphaFold's reported `0.96 Å` CASP14 median
  Cα RMSD95.

The original complete material execution restores 576 exact states at each
residue, performs 43,776 raw state trials, and records zero trained weights,
zero fitted parameters, zero candidate orderings and zero target accesses. The
four extended panels likewise record zero target accesses before every seal.

## Evidence layers

1. The PDF and Markdown paper state the scientific argument, method, metrics,
   provenance and blind predictive result.
2. `protein_blind_multi_structure_evidence_v1.json` binds all 24 post-seal
   measurements, target identities, structure hashes, aggregate parity
   comparison and four panel seals.
3. `protein_material_architecture_v1_applied_evidence.json` binds the complete
   candidate census, source hashes, seal, prediction hash and post-seal metrics.
4. The material relation, admission and protocol receipts expose the exact
   sequence/generated-geometry relation and its machine-checked closure.
5. The sealed R2 execution directory contains the input, selected states, PDB,
   seal and post-seal evaluation.
6. The four extended panel directories contain every registration, complete
   structure, state path and pre-comparison seal; their target directories are
   retained solely for post-seal reproduction.
7. The forcing registry and audits distinguish engine-closed relations,
   observational derivation, applied development evidence and author conclusions.
8. The recovery evidence preserves every available complete positive candidate
   rather than allowing a single emitted row or agent interpretation to erase
   empirical data.
9. The source, constants and tests reproduce the mathematical and execution
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
reliable; that validates its output performance. Fold Protein establishes
AlphaFold-class median predictive accuracy while also exposing the proposed law,
its first-principles derivation, complete state domain, blind execution boundary,
sealed consequences and experimental comparisons. That combined evidence is
Blind Predictive Super Parity.

The two earlier Protein papers are retained in the repositories and their
existing Zenodo records as chronological development artifacts. This standalone
paper supersedes them as the current statement of the work.
