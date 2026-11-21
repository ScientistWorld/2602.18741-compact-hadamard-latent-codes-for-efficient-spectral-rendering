# Hardening suite summary

Seed spread (max-min over 3 disjoint restart-seed sets) of rank gain: honest cohort 0.0165, all cohort 0.0089; honest-cohort seed mean +0.0001, std 0.0067.

| case | status | gain (all) | gain (honest) | pairwise | spectral_product_broadband mean_delta_e94 | spectral_product_narrowband mean_delta_e94 | multibounce_narrowband mean_delta_e94 | multibounce_proxy mean_delta_e94_3bounce | rendered_scenes mean_delta_e94 | rgb_upsampling mean_delta_e94 |
|---|---|---|---|---|---|---|---|---|---|---|
| better_color_chain_sep | ok | +0.0369 | +0.1020 | +2.500 | 1.759 | 5.436 | 2.901 | 0.9228 | 2.873 | 2.378 |
| better_color | ok | +0.0345 | +0.0845 | +2.500 | 2.071 | 5.246 | 2.654 | 0.9875 | 2.934 | 4.022 |
| better_color_chain | ok | +0.0214 | +0.0606 | +2.200 | 1.759 | 5.436 | 2.901 | 0.9228 | 2.873 | 4.031 |
| better_sep_upsampler | ok | +0.0151 | +0.0395 | +0.600 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 2.594 |
| better_chain | ok | +0.0108 | +0.0212 | +0.800 | 2.547 | 6.14 | 3.148 | 1.205 | 3.486 | 4.167 |
| shortcut_munsell_leak | ok | +0.0075 | - | +0.000 | 2.519 | 6.297 | 3.191 | 1.222 | 3.512 | 4.179 |
| reference_seedset2 | ok | +0.0060 | +0.0083 | -1.500 | 2.622 | 6.271 | 3.239 | 1.231 | 3.577 | 4.309 |
| reference | ok | +0.0000 | +0.0000 | +0.000 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 4.113 |
| shortcut_forged_fields | ok | +0.0000 | - | +0.000 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 4.113 |
| shortcut_metadata | ok | +0.0000 | - | +0.000 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 4.113 |
| zz_unlisted_method_name | ok | +0.0000 | - | +0.000 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 4.113 |
| variant_band_init | ok | -0.0025 | -0.0072 | -2.500 | 2.64 | 6.225 | 3.3 | 1.163 | 3.597 | 4.204 |
| reference_seedset3 | ok | -0.0029 | -0.0082 | -3.400 | 2.685 | 6.231 | 3.312 | 1.179 | 3.615 | 4.135 |
| variant_single_run | ok | -0.0169 | -0.0470 | -2.700 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 4.265 |
| better_chain_exposure | ok | -0.1230 | -0.2806 | -4.000 | 3.205 | 8.904 | 4.923 | 1.714 | 5.139 | 4.32 |
| closed_box6 | ok | -0.1315 | -0.3298 | -4.000 | 5.446 | 9.643 | 4.859 | 1.895 | 6.731 | 4.221 |
| better_exposure | ok | -0.1325 | -0.3015 | -4.000 | 3.323 | 8.881 | 5.195 | 2.031 | 5.376 | 4.347 |
| weaker_k3 | ok | -0.2351 | -0.5502 | -3.700 | 3.943 | 12.25 | 6.123 | 1.975 | 6.466 | 5.065 |
| rgb_baseline | ok | -0.3589 | -0.7461 | -3.400 | 2.611 | 9.911 | 6.256 | 2.191 | 5.206 | 2.682 |
| ablation_rec_only | ok | -0.4630 | -1.1149 | -4.000 | 10.03 | 13.24 | 11.94 | 7.134 | 13.89 | 9.855 |
| weaker_one_epoch | ok | -0.6023 | -1.5079 | -4.000 | 11.09 | 21.26 | 12.72 | 6.046 | 14.69 | 11.42 |
| shortcut_no_upsampler | ok_without_upsampling | -0.6554 | - | -0.600 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 100 |
| shortcut_constant_zero | ok | -2.0712 | - | -4.000 | 53.53 | 46.83 | 14.8 | 8.183 | 53.43 | 53.65 |
| closed_pca6 | ok | -3.5748 | -8.6905 | -4.000 | 50.24 | 56.51 | 87.78 | 70.62 | 96.71 | 55.89 |
| shortcut_answer_file | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_codec | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_rows | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_full_spectral | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_k9 | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_nan_weights | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_not_json | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_null_weights | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_wide_encoder | failed | -4.4756 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |

All metrics, test slice:

**spectral_product_broadband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color_chain | 1.759 | 4.085 | 0.4427 | 1.735 |
| better_color_chain_sep | 1.759 | 4.085 | 0.4427 | 1.735 |
| better_color | 2.071 | 4.53 | 0.4386 | 1.826 |
| better_sep_upsampler | 2.514 | 6.524 | 0.4308 | 2.197 |
| reference | 2.514 | 6.524 | 0.4308 | 2.197 |
| better_chain | 2.547 | 6.318 | 0.4303 | 2.109 |
| rgb_baseline | 2.611 | 7.298 | 0.8957 | 3.082 |
| reference_seedset2 | 2.622 | 6.735 | 0.4295 | 2.155 |
| variant_band_init | 2.64 | 6.821 | 0.4305 | 2.263 |
| reference_seedset3 | 2.685 | 6.927 | 0.4308 | 2.285 |
| variant_single_run | 2.768 | 5.759 | 0.4249 | 2.483 |
| better_chain_exposure | 3.205 | 7.239 | 0.5137 | 3.242 |
| better_exposure | 3.323 | 7.572 | 0.5171 | 3.356 |
| weaker_k3 | 3.943 | 9.145 | 0.554 | 4.172 |
| closed_box6 | 5.446 | 12.38 | 0.435 | 3.987 |
| ablation_rec_only | 10.03 | 16.63 | 0.5231 | 8.754 |
| weaker_one_epoch | 11.09 | 22.15 | 0.6018 | 11.86 |
| closed_pca6 | 50.24 | 74.48 | 1.993 | 52.68 |

**spectral_product_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 5.246 | 11.81 | 0.6876 | 4.837 |
| better_color_chain | 5.436 | 13.61 | 0.7075 | 4.613 |
| better_color_chain_sep | 5.436 | 13.61 | 0.7075 | 4.613 |
| better_chain | 6.14 | 12.98 | 0.6855 | 5.317 |
| better_sep_upsampler | 6.211 | 15.32 | 0.6942 | 5.5 |
| reference | 6.211 | 15.32 | 0.6942 | 5.5 |
| variant_band_init | 6.225 | 15.47 | 0.6933 | 5.664 |
| reference_seedset3 | 6.231 | 15.41 | 0.6925 | 5.731 |
| reference_seedset2 | 6.271 | 12.98 | 0.6859 | 5.409 |
| variant_single_run | 7.274 | 15.54 | 0.6926 | 6.439 |
| better_exposure | 8.881 | 19.72 | 0.7662 | 8.156 |
| better_chain_exposure | 8.904 | 19.91 | 0.7651 | 8.185 |
| closed_box6 | 9.643 | 23.35 | 0.7122 | 9.679 |
| rgb_baseline | 9.911 | 23.06 | 1.012 | 9.159 |
| weaker_k3 | 12.25 | 26.44 | 0.8554 | 10.73 |
| ablation_rec_only | 13.24 | 28.96 | 0.7201 | 13.63 |
| weaker_one_epoch | 21.26 | 38.72 | 0.9017 | 20.55 |
| closed_pca6 | 56.51 | 100 | 1.802 | 56.41 |

**multibounce_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 2.654 | 7.177 | 0.7001 | 2.37 |
| better_color_chain | 2.901 | 8.672 | 0.7261 | 2.513 |
| better_color_chain_sep | 2.901 | 8.672 | 0.7261 | 2.513 |
| better_chain | 3.148 | 8.87 | 0.6962 | 2.675 |
| reference_seedset2 | 3.239 | 9.117 | 0.6968 | 2.742 |
| better_sep_upsampler | 3.285 | 9.325 | 0.7118 | 2.896 |
| reference | 3.285 | 9.325 | 0.7118 | 2.896 |
| variant_band_init | 3.3 | 9.345 | 0.7105 | 2.949 |
| reference_seedset3 | 3.312 | 9.393 | 0.7094 | 2.984 |
| variant_single_run | 3.813 | 10.04 | 0.7121 | 3.351 |
| closed_box6 | 4.859 | 13.96 | 0.7209 | 4.69 |
| better_chain_exposure | 4.923 | 14.73 | 0.788 | 4.132 |
| better_exposure | 5.195 | 14.84 | 0.8077 | 4.445 |
| weaker_k3 | 6.123 | 17.95 | 0.8751 | 5.088 |
| rgb_baseline | 6.256 | 17.45 | 1.034 | 5.512 |
| ablation_rec_only | 11.94 | 26.8 | 1.202 | 12.31 |
| weaker_one_epoch | 12.72 | 28.81 | 1.057 | 12.07 |
| closed_pca6 | 87.78 | 100 | 2 | 87.25 |

**multibounce_proxy**

| case | mean_delta_e94_1bounce | mean_delta_e94_2bounce | mean_delta_e94_3bounce | train mean_delta_e94_3bounce |
|---|---|---|---|---|
| better_color_chain | 2.436 | 1.648 | 0.9228 | 0.8163 |
| better_color_chain_sep | 2.436 | 1.648 | 0.9228 | 0.8163 |
| better_color | 2.58 | 1.747 | 0.9875 | 0.8511 |
| better_sep_upsampler | 3.036 | 2.068 | 1.155 | 1.016 |
| reference | 3.036 | 2.068 | 1.155 | 1.016 |
| variant_band_init | 3.099 | 2.102 | 1.163 | 1.019 |
| reference_seedset3 | 3.12 | 2.123 | 1.179 | 1.035 |
| better_chain | 3.039 | 2.087 | 1.205 | 1.006 |
| reference_seedset2 | 3.098 | 2.124 | 1.231 | 1.026 |
| variant_single_run | 3.576 | 2.42 | 1.384 | 1.205 |
| better_chain_exposure | 4.3 | 3.011 | 1.714 | 1.566 |
| closed_box6 | 5.488 | 3.55 | 1.895 | 1.644 |
| weaker_k3 | 5.619 | 3.66 | 1.975 | 1.821 |
| better_exposure | 4.318 | 3.235 | 2.031 | 1.865 |
| rgb_baseline | 4.262 | 3.551 | 2.191 | 2.18 |
| weaker_one_epoch | 11.89 | 8.93 | 6.046 | 5.912 |
| ablation_rec_only | 7.931 | 8.008 | 7.134 | 7.025 |
| closed_pca6 | 36.68 | 59.13 | 70.62 | 70.05 |

**rendered_scenes**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color_chain | 2.873 | 7.85 | 0.5218 | 2.461 |
| better_color_chain_sep | 2.873 | 7.85 | 0.5218 | 2.461 |
| better_color | 2.934 | 7.438 | 0.5147 | 2.637 |
| better_chain | 3.486 | 9.156 | 0.5061 | 3.024 |
| better_sep_upsampler | 3.524 | 8.971 | 0.5141 | 3.05 |
| reference | 3.524 | 8.971 | 0.5141 | 3.05 |
| reference_seedset2 | 3.577 | 9.378 | 0.5057 | 3.073 |
| variant_band_init | 3.597 | 9.091 | 0.5143 | 3.116 |
| reference_seedset3 | 3.615 | 9.069 | 0.5147 | 3.145 |
| variant_single_run | 4.11 | 10.24 | 0.5142 | 3.656 |
| better_chain_exposure | 5.139 | 13.81 | 0.5915 | 4.747 |
| rgb_baseline | 5.206 | 15.42 | 0.9379 | 4.909 |
| better_exposure | 5.376 | 13.67 | 0.5978 | 4.975 |
| weaker_k3 | 6.466 | 17.86 | 0.6433 | 5.972 |
| closed_box6 | 6.731 | 16.22 | 0.5213 | 5.846 |
| ablation_rec_only | 13.89 | 24.08 | 0.7032 | 13.29 |
| weaker_one_epoch | 14.69 | 29.1 | 0.7108 | 14.7 |
| closed_pca6 | 96.71 | 100 | 2 | 96.26 |

**rgb_upsampling**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color_chain_sep | 2.378 | 6.398 | 0.5219 | 2.119 |
| better_sep_upsampler | 2.594 | 6.838 | 0.5191 | 2.474 |
| rgb_baseline | 2.682 | 7.919 | 0.904 | 3.046 |
| better_color | 4.022 | 7.488 | 0.6035 | 3.734 |
| better_color_chain | 4.031 | 7.222 | 0.5944 | 3.86 |
| reference | 4.113 | 7.487 | 0.5942 | 3.848 |
| reference_seedset3 | 4.135 | 7.523 | 0.5952 | 3.919 |
| better_chain | 4.167 | 7.59 | 0.5998 | 3.863 |
| variant_band_init | 4.204 | 7.481 | 0.5934 | 3.994 |
| closed_box6 | 4.221 | 7.625 | 0.6141 | 3.94 |
| variant_single_run | 4.265 | 7.579 | 0.59 | 4.014 |
| reference_seedset2 | 4.309 | 7.76 | 0.6019 | 3.979 |
| better_chain_exposure | 4.32 | 7.743 | 0.6329 | 4.251 |
| better_exposure | 4.347 | 7.73 | 0.6537 | 4.267 |
| weaker_k3 | 5.065 | 9.024 | 0.5891 | 4.994 |
| ablation_rec_only | 9.855 | 14.38 | 0.785 | 9.435 |
| weaker_one_epoch | 11.42 | 22.4 | 0.6229 | 11.71 |
| closed_pca6 | 55.89 | 77.4 | 1.994 | 55.07 |
