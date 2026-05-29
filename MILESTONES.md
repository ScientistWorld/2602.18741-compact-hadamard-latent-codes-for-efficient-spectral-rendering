# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-29 08:22] - method_runs
- Implemented the paper's nonnegative linear encoder/decoder with softplus-constrained weights.
- Ran the k=6 blockwise Hadamard product pipeline end-to-end and wrote prediction artifacts.

### [2026-05-29 08:49] - core_claim
- Fixed the procedural spectral benchmark and training initialization after the first run did not beat RGB.
- Reproduced the central claim on the narrowband product setting: k=6 Hadamard codes reduced mean DeltaE94 versus the RGB baseline while using two RGB-equivalent passes.

### [2026-05-29 08:49] - core_claim_plus
- Extended the reproduced result to broadband product and three-bounce narrowband chain settings.
- Current scores: broadband mean DeltaE94 2.136 vs RGB 2.488, narrowband 3.929 vs RGB 7.661, multibounce 2.721 vs RGB 11.013.

### [2026-05-29 09:20] - core_claim
- Continuing audit found the evaluator trusted candidate-provided target spectra and used an unclear compactness field.
- Fixed evaluation to regenerate held-out targets independently from `data/`, added the paper's RGB-to-latent upsampler implementation, and submitted a hardened reproduction job before restoring higher milestones.
