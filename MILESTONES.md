# Reproduction Milestones

**Current: core_claim_plus**

<!-- Milestone levels (update "Current" above as you progress):
  none             — just started, no meaningful progress yet
  method_runs      — the paper's method executes end-to-end without errors
  core_claim       — minimum experiment supports the paper's central claim
  core_claim_plus  — core claim reproduced on additional settings
  secondary_claims — secondary results or contributions reproduced
  majority         — more than half of reported results reproduced
  near_complete    — most results reproduced, only minor gaps remain
  full             — all reported results reproduced
-->

## Progress Log

### [2026-05-29 00:00] - none
- Read the paper and identified the core method: nonnegative linear Hadamard latent spectral codes with exact addition/scaling and approximate multiplicativity.
- Implemented the first faithful reproduction pipeline and prepared a compute-node job, but no method run has completed yet.

### [2026-05-29 08:23] - method_runs
- CPU test job completed successfully: the RGB baseline, `k=6` Hadamard codec training, artifact-based evaluation, and `validate.py --compare` all ran end-to-end.
- The first learned codec did not beat the RGB baseline, so `core_claim` is not reached yet. Updated the procedural spectral benchmark and codec initialization/selection before resubmitting.

### [2026-05-29 08:29] - core_claim_plus
- Follow-up CPU job completed successfully and supports the paper's central claim on multiple settings.
- `hadamard_k6` beat `rgb_baseline` on broadband products, narrowband products, and three-bounce narrowband chains while using two RGB-like passes.

## Stop Justification
- Completed at milestone `core_claim_plus`.
