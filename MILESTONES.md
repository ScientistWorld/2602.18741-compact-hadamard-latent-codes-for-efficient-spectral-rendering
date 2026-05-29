# Reproduction Milestones

**Current: secondary_claims**

## Progress Log

### [2026-05-29 09:17] - core_claim
- Prior packaged run reproduced the core Hadamard-code claim on held-out broadband, narrowband, and three-bounce spectral-product tests.
- Current iteration tightens the procedural spectral grid to match the paper's zero-outside-400-700 nm preprocessing and submits a rerun before claiming a higher milestone.

### [2026-05-29 09:19] - core_claim
- Audit confirms the implementation is the paper's actual nonnegative linear Hadamard codec plus the secondary RGB-to-latent MLP, not a surrogate.
- Evaluation remains method-independent and reads method artifacts, but current score files are stale relative to the new spectral masking change; keeping the milestone at `core_claim` until the rerun completes.

### [2026-05-29 09:27] - secondary_claims
- Job `1269b0bc-79d` reran the packaged reproduction after enforcing the paper's 400-700 nm spectral masking and passed `python validate.py --compare` inside the container.
- Official `k=6` scores support the core claim across all reference-matched settings: broadband DeltaE94 2.016 vs RGB 2.522, narrowband 4.073 vs RGB 7.624, and three-bounce narrowband 3.030 vs RGB 10.940 with spectral MSE 9.68e-4.
- Secondary diagnostics also ran: `k=9` improved all three product settings at a three-pass cost, and the RGB-to-latent upsampler improved narrowband DeltaE94 to 6.334 vs RGB 7.624. These diagnostics are stored in `scoring/extra_scores.json` because the paper text available here does not provide exact reference targets for them.

## Stop Justification
- Stopping at `secondary_claims`. The reusable environment is packaged and validated; pushing to majority/full would require unprovided measured Munsell/LSPDD assets, Mitsuba scenes, and paper-reported quantitative targets for the secondary diagnostics.
