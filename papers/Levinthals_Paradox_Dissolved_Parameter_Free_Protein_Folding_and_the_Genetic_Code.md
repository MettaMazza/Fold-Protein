# Fold Protein: A Forced-Geometry Programme for Protein Structure

## Levinthal's argument, finite construction, and the open blind-prediction problem

**Maria Smith — Ernos Labs**
**Version 3.3 — 17 July 2026**

## Abstract

Fold Protein is a computational-proof programme derived under Smithian Fold Theory (SFT). SFT begins with one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms; the theorem forces the One and fold. The protein project asks whether the laws needed for protein structure can be forced from that model, or whether established computational and structural laws can be re-derived as consequences of the same constitution.

The present empirical anchor is a target-assisted 24-lattice construction of the 76-residue ubiquitin Cα backbone. Exact replay gives a repository-defined Kabsch TM-like score of 0.9891211351 and Cα dRMSD of 0.2608575408 Å. This secures **construction parity / structural parity** at the declared comparison point. It was not a blind sequence-to-structure run; that is a separate forward-forcing extension, not a retrospective condition on the construction result.

## 1. The scientific argument

Levinthal's observation is not that proteins literally sample every conformation. It is that the speed of physical folding implies constrained pathways rather than blind exhaustive search. Fold Protein takes that methodological point seriously: the important object is a law-governed construction whose transitions can be inspected and machine checked.

The programme gives mathematical and structural proof priority over opaque prediction alone. Prediction remains valuable, but it is not allowed to erase provenance. A blind result will count only when its selection law is forced or constitutionally re-derived, its target remains unavailable to the selector, and its failures are retained.

## 2. The finite geometric object

The current construction uses a 24×24 lattice of backbone dihedral pairs at 15-degree spacing. This yields 576 declared states per residue. A state sequence is projected into Cartesian N–Cα–C backbone coordinates by the committed NeRF implementation.

This finite object replaces an unconstrained continuum with an auditable set of choices. That is a structural advance only if the claim is kept exact:

- the lattice and builder are explicit;
- the successful ubiquitin state path is explicit;
- every output coordinate is reproducible;
- the native target selected the successful path during development;
- the sequence-to-path law remains open.

The companion construction paper and `verify/replay_ubiquitin_24_lattice.py` provide the complete current evidence boundary.

## 3. What is forced, what is established, what remains engineering

The project uses three labels:

1. **Forced:** produced by the SFT engine and traceable to the theorem, with violation causing a halt.
2. **Constitutionally re-derived:** an established mathematical or computational method shown to satisfy the SFT constitution and used with that derivation recorded.
3. **Engineering:** an implementation choice not yet promoted to either category.

The present 24-lattice construction has zero trained weights. The repository also contains established peptide geometry constants, floating-point NeRF operations, search widths, steric thresholds, and experimental scoring tools. Their current provenance must be recorded honestly. An “engineering” label describes where the implementation stands today; it is not a declaration that the element cannot be forced or re-derived by SFT. The development objective is to derive, replace, or constitutionally retain each element.

## 4. Reproducible result

For ubiquitin (`1ubq`):

| Result | Value |
|---|---:|
| Residues / matched Cα atoms | 76 |
| Candidate lattice | 24×24 = 576 states |
| Repository Kabsch TM-like score | 0.9891211351 |
| Cα distance-matrix RMSD | 0.2608575408 Å |

These numbers compare the committed constructed trace with the committed experimental reference and establish the declared structural construction parity. Comparison with AlphaFold concerns resolution, parameter count, transparency, and method; the protocols and metrics are disclosed as different, so no claim of predictive-protocol identity is made.

## 5. Blind forward-forcing protocol

The next engine must satisfy all of the following before a blind claim is published:

1. Register the exact code, theory revision, targets, and stopping rule before structure access.
2. Permit the selector to read amino-acid sequence and declared derived inputs only.
3. Prohibit target coordinates, target-derived distances, homologous templates, and post-hoc per-target constants from selection.
4. Require every selection law to carry a forced, re-derived, or disclosed-engineering status.
5. Halt when a required forcing trace is absent or violated.
6. Score only after the output hash is sealed.
7. Publish the complete target set, failures, runtimes, and source hashes.

This protocol makes blind prediction an active forward-forcing test of the theory rather than a replacement for the theory's proof standard or a prerequisite for the already secured construction result.

## 6. Genetics and wider biological claims

Earlier drafts combined the construction with broad claims about codon redundancy, chirality, replicative limits, docking, and a complete dissolution of Levinthal's paradox. Those subjects may be investigated within SFT, but the present protein evidence does not by itself prove them. They are excluded from this release until each has its own derivation, executable witness, and bounded empirical claim.

## 7. Conclusion

Fold Protein has secured construction parity through a strong target-assisted result and replayable finite proof object. Blind sequence-to-structure prediction is the next active forward-forcing extension. The programme now advances from “the observed structure is constructed on this declared lattice” to “which forced laws select that structure from sequence?” The second objective expands the first; it does not weaken or redefine it.

## Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21276950>

## References

1. Levinthal, C. (1969). How to fold graciously. In *Mössbauer Spectroscopy in Biological Systems*, 22–24.
2. Parsons, J. et al. (2005). Practical conversion from torsion space to Cartesian space for in silico protein synthesis. *Journal of Computational Chemistry*, 26, 1063–1068.
3. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
