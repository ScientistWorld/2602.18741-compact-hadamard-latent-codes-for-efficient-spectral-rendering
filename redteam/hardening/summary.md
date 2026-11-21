# Hardening suite summary

Seed spread of rank gain: honest cohort 0.0296, all cohort 0.0143.

| case | status | gain (all) | gain (honest) | pairwise | spectral_product_broadband mean_delta_e94 | spectral_product_narrowband mean_delta_e94 | multibounce_narrowband mean_delta_e94 | multibounce_proxy mean_delta_e94_3bounce | rendered_scenes mean_delta_e94 | rgb_upsampling mean_delta_e94 |
|---|---|---|---|---|---|---|---|---|---|---|
| better_color | ok | +0.0235 | +0.0624 | +2.500 | 1.734 | 5.32 | 2.921 | 0.9327 | 2.807 | 6.791 |
| better_chain | ok | +0.0212 | +0.0466 | +3.600 | 2.362 | 6.038 | 2.963 | 1.143 | 3.302 | 6.528 |
| reference_seed3 | ok | +0.0143 | +0.0296 | +2.100 | 2.449 | 6.149 | 3.079 | 1.193 | 3.401 | 6.821 |
| reference_seed2 | ok | +0.0116 | +0.0283 | +3.000 | 2.324 | 6.067 | 3.191 | 1.105 | 3.343 | 6.55 |
| shortcut_munsell_leak | ok | +0.0066 | - | +1.400 | 2.466 | 6.155 | 3.249 | 1.186 | 3.434 | 7.232 |
| variant_band_init | ok | +0.0022 | +0.0057 | +2.900 | 2.459 | 6.091 | 3.24 | 1.126 | 3.48 | 6.901 |
| reference | ok | +0.0000 | +0.0000 | +0.000 | 2.482 | 6.107 | 3.249 | 1.132 | 3.498 | 7.086 |
| shortcut_forged_fields | ok | +0.0000 | - | +0.000 | 2.482 | 6.107 | 3.249 | 1.132 | 3.498 | 7.086 |
| shortcut_metadata | ok | +0.0000 | - | +0.000 | 2.482 | 6.107 | 3.249 | 1.132 | 3.498 | 7.086 |
| zz_unlisted_method_name | ok | +0.0000 | - | +0.000 | 2.482 | 6.107 | 3.249 | 1.132 | 3.498 | 7.086 |
| better_long | ok | -0.0039 | -0.0109 | -2.600 | 2.756 | 6.158 | 3.273 | 1.174 | 3.651 | 7.12 |
| better_chain_exposure | ok | -0.1187 | -0.2595 | -4.000 | 3.284 | 8.918 | 4.894 | 1.719 | 5.262 | 7.316 |
| better_exposure | ok | -0.1216 | -0.2642 | -4.000 | 3.202 | 8.839 | 5.11 | 1.875 | 5.238 | 7.439 |
| closed_box6 | ok | -0.1320 | -0.3146 | -4.000 | 5.446 | 9.643 | 4.859 | 1.895 | 6.731 | 7.41 |
| weaker_k3 | ok | -0.2289 | -0.5071 | -3.700 | 3.885 | 12.1 | 6.044 | 1.966 | 6.391 | 8.237 |
| rgb_baseline | ok | -0.3495 | -0.6974 | -3.400 | 2.611 | 9.911 | 6.256 | 2.191 | 5.206 | 6.485 |
| ablation_rec_only | ok | -0.4215 | -0.9559 | -4.000 | 9.294 | 12.66 | 11.58 | 6.927 | 13.35 | 12.09 |
| weaker_one_epoch | ok | -0.6103 | -1.4405 | -4.000 | 11.2 | 21.38 | 13.22 | 6.409 | 15 | 16.34 |
| shortcut_no_upsampler | ok_without_upsampling | -0.6438 | - | -0.600 | 2.482 | 6.107 | 3.249 | 1.132 | 3.498 | 100 |
| shortcut_constant_zero | ok | -1.9974 | - | -4.000 | 53.53 | 46.83 | 14.8 | 8.183 | 53.43 | 50.09 |
| closed_pca6 | ok | -3.5227 | -8.0591 | -4.000 | 50.24 | 56.51 | 87.78 | 70.62 | 96.71 | 57.48 |
| shortcut_answer_file | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_codec | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_rows | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_full_spectral | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_k9 | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_nan_weights | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_not_json | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_null_weights | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_wide_encoder | failed | -4.3884 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |

All metrics, test slice:

**spectral_product_broadband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 1.734 | 3.999 | 0.4433 | 1.72 |
| reference_seed2 | 2.324 | 5.732 | 0.4293 | 2.102 |
| better_chain | 2.362 | 5.166 | 0.4298 | 2.023 |
| reference_seed3 | 2.449 | 5.463 | 0.4296 | 2.074 |
| variant_band_init | 2.459 | 6.524 | 0.4305 | 2.142 |
| reference | 2.482 | 6.594 | 0.4305 | 2.152 |
| rgb_baseline | 2.611 | 7.298 | 0.8957 | 3.082 |
| better_long | 2.756 | 7.214 | 0.4298 | 2.278 |
| better_exposure | 3.202 | 7.087 | 0.5037 | 3.185 |
| better_chain_exposure | 3.284 | 7.464 | 0.5024 | 3.322 |
| weaker_k3 | 3.885 | 8.884 | 0.5501 | 4.135 |
| closed_box6 | 5.446 | 12.38 | 0.435 | 3.987 |
| ablation_rec_only | 9.294 | 15.22 | 0.5276 | 8.39 |
| weaker_one_epoch | 11.2 | 22.37 | 0.5996 | 11.99 |
| closed_pca6 | 50.24 | 74.48 | 1.993 | 52.68 |

**spectral_product_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 5.32 | 13.24 | 0.7071 | 4.532 |
| better_chain | 6.038 | 13.94 | 0.683 | 5.346 |
| reference_seed2 | 6.067 | 15.06 | 0.6962 | 5.17 |
| variant_band_init | 6.091 | 14.67 | 0.696 | 5.341 |
| reference | 6.107 | 14.83 | 0.6958 | 5.379 |
| reference_seed3 | 6.149 | 13.93 | 0.6832 | 5.462 |
| better_long | 6.158 | 15.32 | 0.6932 | 5.766 |
| better_exposure | 8.839 | 19.77 | 0.7571 | 8.188 |
| better_chain_exposure | 8.918 | 20.02 | 0.7546 | 8.257 |
| closed_box6 | 9.643 | 23.35 | 0.7122 | 9.679 |
| rgb_baseline | 9.911 | 23.06 | 1.012 | 9.159 |
| weaker_k3 | 12.1 | 26.21 | 0.8547 | 10.61 |
| ablation_rec_only | 12.66 | 26.09 | 0.7168 | 13.23 |
| weaker_one_epoch | 21.38 | 38.64 | 0.9022 | 20.72 |
| closed_pca6 | 56.51 | 100 | 1.802 | 56.41 |

**multibounce_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 2.921 | 8.432 | 0.7318 | 2.587 |
| better_chain | 2.963 | 8.292 | 0.6928 | 2.602 |
| reference_seed3 | 3.079 | 8.594 | 0.6936 | 2.698 |
| reference_seed2 | 3.191 | 9.325 | 0.7138 | 2.769 |
| variant_band_init | 3.24 | 9.525 | 0.7128 | 2.831 |
| reference | 3.249 | 9.464 | 0.7126 | 2.845 |
| better_long | 3.273 | 9.332 | 0.7099 | 2.988 |
| closed_box6 | 4.859 | 13.96 | 0.7209 | 4.69 |
| better_chain_exposure | 4.894 | 14.5 | 0.7772 | 4.145 |
| better_exposure | 5.11 | 14.83 | 0.7998 | 4.376 |
| weaker_k3 | 6.044 | 17.72 | 0.8729 | 5.002 |
| rgb_baseline | 6.256 | 17.45 | 1.034 | 5.512 |
| ablation_rec_only | 11.58 | 26.31 | 1.167 | 12.01 |
| weaker_one_epoch | 13.22 | 29.38 | 1.08 | 12.57 |
| closed_pca6 | 87.78 | 100 | 2 | 87.25 |

**multibounce_proxy**

| case | mean_delta_e94_1bounce | mean_delta_e94_2bounce | mean_delta_e94_3bounce | train mean_delta_e94_3bounce |
|---|---|---|---|---|
| better_color | 2.402 | 1.63 | 0.9327 | 0.8377 |
| reference_seed2 | 2.867 | 1.959 | 1.105 | 0.9843 |
| variant_band_init | 2.978 | 2.022 | 1.126 | 0.9958 |
| reference | 2.994 | 2.032 | 1.132 | 1 |
| better_chain | 2.95 | 2.006 | 1.143 | 0.9677 |
| better_long | 3.135 | 2.128 | 1.174 | 1.038 |
| reference_seed3 | 3.012 | 2.064 | 1.193 | 1.005 |
| better_chain_exposure | 4.365 | 3.043 | 1.719 | 1.559 |
| better_exposure | 4.293 | 3.092 | 1.875 | 1.725 |
| closed_box6 | 5.488 | 3.55 | 1.895 | 1.644 |
| weaker_k3 | 5.551 | 3.62 | 1.966 | 1.818 |
| rgb_baseline | 4.262 | 3.551 | 2.191 | 2.18 |
| weaker_one_epoch | 11.97 | 9.185 | 6.409 | 6.267 |
| ablation_rec_only | 7.702 | 7.774 | 6.927 | 6.847 |
| closed_pca6 | 36.68 | 59.13 | 70.62 | 70.05 |

**rendered_scenes**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 2.807 | 7.673 | 0.5245 | 2.432 |
| better_chain | 3.302 | 8.339 | 0.5069 | 2.88 |
| reference_seed2 | 3.343 | 8.573 | 0.5119 | 2.882 |
| reference_seed3 | 3.401 | 8.681 | 0.5063 | 2.977 |
| variant_band_init | 3.48 | 8.99 | 0.5136 | 2.978 |
| reference | 3.498 | 9.017 | 0.5137 | 2.996 |
| better_long | 3.651 | 9.215 | 0.5143 | 3.139 |
| rgb_baseline | 5.206 | 15.42 | 0.9379 | 4.909 |
| better_exposure | 5.238 | 13.97 | 0.5864 | 4.844 |
| better_chain_exposure | 5.262 | 14.26 | 0.5807 | 4.84 |
| weaker_k3 | 6.391 | 17.48 | 0.6405 | 5.862 |
| closed_box6 | 6.731 | 16.22 | 0.5213 | 5.846 |
| ablation_rec_only | 13.35 | 23.67 | 0.708 | 12.81 |
| weaker_one_epoch | 15 | 29.29 | 0.7149 | 15.03 |
| closed_pca6 | 96.71 | 100 | 2 | 96.26 |

**rgb_upsampling**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| rgb_baseline | 6.485 | 19.17 | 0.9599 | 6.003 |
| better_chain | 6.528 | 17.72 | 0.735 | 5.687 |
| reference_seed2 | 6.55 | 17.71 | 0.7187 | 5.782 |
| better_color | 6.791 | 18.17 | 0.7332 | 6.11 |
| reference_seed3 | 6.821 | 18.56 | 0.7368 | 5.882 |
| variant_band_init | 6.901 | 18.59 | 0.7348 | 6.142 |
| reference | 7.086 | 18.95 | 0.7352 | 6.234 |
| better_long | 7.12 | 18.32 | 0.7361 | 6.369 |
| better_chain_exposure | 7.316 | 19.46 | 0.7609 | 6.528 |
| closed_box6 | 7.41 | 20.03 | 0.744 | 6.814 |
| better_exposure | 7.439 | 19.65 | 0.763 | 6.669 |
| weaker_k3 | 8.237 | 21.64 | 0.7229 | 7.399 |
| ablation_rec_only | 12.09 | 24.55 | 0.8538 | 11.24 |
| weaker_one_epoch | 16.34 | 32.15 | 0.765 | 16.05 |
| closed_pca6 | 57.48 | 94.15 | 1.902 | 56.24 |
