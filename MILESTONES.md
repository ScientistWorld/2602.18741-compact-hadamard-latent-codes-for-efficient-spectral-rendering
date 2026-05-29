# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-05-29 09:17] - core_claim
- Prior packaged run reproduced the core Hadamard-code claim on held-out broadband, narrowband, and three-bounce spectral-product tests.
- Current iteration tightens the procedural spectral grid to match the paper's zero-outside-400-700 nm preprocessing and submits a rerun before claiming a higher milestone.

### [2026-05-29 09:19] - core_claim
- Audit confirms the implementation is the paper's actual nonnegative linear Hadamard codec plus the secondary RGB-to-latent MLP, not a surrogate.
- Evaluation remains method-independent and reads method artifacts, but current score files are stale relative to the new spectral masking change; keeping the milestone at `core_claim` until the rerun completes.

## Stop Justification
- Not stopped; submitting a verification run after data-generator and evaluator hardening.
