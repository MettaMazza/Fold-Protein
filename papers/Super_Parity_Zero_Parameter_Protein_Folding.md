# Super Parity in a Target-Assisted 24-Lattice Construction of the Ubiquitin Cα Backbone

**Maria Smith — Ernos Labs**
**Version 1.5 — 17 July 2026**

## Abstract

This paper reports a reproducible construction result in the Fold Protein computational-proof programme. A fixed 24×24 dihedral lattice—576 `(φ, ψ)` states at 15-degree spacing—is used with the repository's deterministic NeRF backbone builder to construct the 76-residue ubiquitin Cα trace. The committed state sequence reproduces `verify/1ubq_test_24_lattice.pdb` byte for byte. Against the committed experimental `1ubq` reference, the repository's Kabsch-aligned TM-like score is 0.9891211351 and the Cα distance-matrix RMSD is 0.2608575408 Å.

The native structure was used during the development search to select the state path. The result is therefore a **target-assisted proof by construction** and establishes **construction parity / structural parity** at this declared comparison boundary. “Parity” here does not mean predictive parity and does not depend on pretending that this was a blind sequence-to-structure run. The comparison with parameterised prediction is the demonstrated structural resolution, transparent derivation, and absence of trained weights; it is not a claim of an identical prediction protocol. Blind forward forcing from sequence is the next active extension.

## 1. Foundation and claim boundary

Smithian Fold Theory begins from one machine-checked, self-proven theorem—*there is no nothing*—with zero axioms. The theorem forces the One and fold used by the wider corpus. Fold Protein tests whether computational structures can be forward-forced or re-derived under that constitution.

This release establishes only the following empirical claim:

> The committed 76-state path on the declared 576-state lattice, passed through the committed backbone builder, reproduces the committed ubiquitin construction and its recorded comparison values.

The state path was not derived blindly from the amino-acid sequence in this run. All-atom construction, thermodynamic kinetics, uniqueness, multi-protein evaluation, and blind selection remain open development tracks. These are statements about the present evidence and implementation, not walls on what SFT may force.

## 2. Construction

The sequence is:

```text
MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG
```

State `s` in `[0,575]` maps row-major to:

```text
φ(s) = -180° + 15° floor(s/24)
ψ(s) = -180° + 15° (s mod 24)
```

The fixed path is recorded in `verify/ubiquitin_24_lattice_manifest.json`. The builder uses the bond lengths, bond angles, trans peptide bond, and floating-point NeRF implementation declared in `tools/predict_structure.py`. Calling this construction “zero trained parameters” means that it contains no learned weights and performs no gradient training. It does not mean every engineering or geometric constant in the current implementation has already been derived by the SFT engine; the manifest exposes the implementation boundary precisely.

The first residue's `φ` and final residue's `ψ` do not affect the generated chain under this builder. The numerical state labels are therefore not claimed to be a unique encoding of the structure.

## 3. Verification

Run:

```sh
python3 verify/replay_ubiquitin_24_lattice.py
```

The verifier checks source hashes, reconstructs the PDB in a temporary directory, requires byte identity with the committed witness, and recomputes the Cα metrics. The release evidence is:

| Quantity | Value |
|---|---:|
| Residues / Cα pairs | 76 |
| Lattice states | 576 |
| Kabsch TM-like score | 0.9891211351 |
| Cα dRMSD | 0.2608575408 Å |
| Constructed PDB SHA-256 | `0036d16f9a70d03458ffc2bdfc32876f1fc77f7dac88379cb69352840b02a21d` |
| Experimental PDB SHA-256 | `d4a6812d8951cf6594e6a0763f089e35f5a80b62acb3c117b2c5565228a7b161` |

The score is explicitly described as **TM-like** because `calculate_tm.py` performs a full-correspondence Kabsch alignment rather than the complete canonical TM-score search procedure.

## 4. Interpretation

The construction supports a finite-geometry research direction: a biologically observed Cα trace can be closely represented by the declared rational lattice and a transparent coordinate builder. This is a useful computational proof object because every state and coordinate can be audited.

Proof and prediction answer different questions. This result tests representational construction. A blind predictor must additionally force the correct path from sequence without reading native coordinates. Fold Protein now treats that as a forward-forcing problem: derive the missing sequence-to-state selection laws, halt on violations, and evaluate them on held-out structures.

## 5. Secured scope and next forward forcing

The producing 576-state target-assisted search that originally selected this path is not yet preserved as a complete executable provenance chain in the repository. The committed `beam_search_engine.py` is a different, smaller search and must not be described as the producer. This release therefore preserves the witness, exact replay, hashes, and metric boundary while marking the missing historical search provenance.

The next predictive result will use a blind protocol fixed before target inspection: registered sequence inputs, no native coordinates in selection, forced or constitutionally re-derived selection laws, and held-out evaluation with failures retained. This forward work extends the secured construction result; it is not a condition on the validity or parity already demonstrated.

## 6. Repositories and lineage

- Fold Protein: <https://github.com/MettaMazza/Fold-Protein>
- Main SFT corpus: <https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything>
- Zenodo concept DOI: <https://doi.org/10.5281/zenodo.21368944>

## References

1. Zhang, Y. & Skolnick, J. (2004). Scoring function for automated assessment of protein structure template quality. *Proteins*, 57, 702–710.
2. Jumper, J. et al. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature*, 596, 583–589.
