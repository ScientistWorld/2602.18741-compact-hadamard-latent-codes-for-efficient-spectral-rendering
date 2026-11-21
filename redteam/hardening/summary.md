# Hardening suite summary

Seed spread (max-min over 5 seeds) of rank gain: honest cohort 0.0636, all cohort 0.0239; honest-cohort seed mean +0.0481, std 0.0242.

| case | status | gain (all) | gain (honest) | pairwise | spectral_product_broadband mean_delta_e94 | spectral_product_narrowband mean_delta_e94 | multibounce_narrowband mean_delta_e94 | multibounce_proxy mean_delta_e94_3bounce | rendered_scenes mean_delta_e94 | rgb_upsampling mean_delta_e94 |
|---|---|---|---|---|---|---|---|---|---|---|
| better_color | ok | +0.0417 | +0.1199 | +2.500 | 1.879 | 5.213 | 2.86 | 0.96 | 2.85 | 3.911 |
| better_color_chain_sep | ok | +0.0377 | +0.1076 | +2.500 | 2.46 | 5.88 | 3.008 | 1.143 | 3.515 | 2.379 |
| reference_seed3 | ok | +0.0239 | +0.0601 | +2.200 | 2.615 | 6.25 | 3.244 | 1.235 | 3.568 | 4.267 |
| reference_seed4 | ok | +0.0226 | +0.0636 | +2.500 | 2.416 | 6.128 | 3.238 | 1.122 | 3.437 | 3.99 |
| shortcut_munsell_leak | ok | +0.0220 | - | +2.700 | 2.455 | 6.04 | 3.213 | 1.15 | 3.433 | 4.105 |
| reference_seed2 | ok | +0.0218 | +0.0622 | +2.400 | 2.519 | 6.142 | 3.239 | 1.137 | 3.497 | 3.71 |
| better_color_chain | ok | +0.0195 | +0.0587 | +2.200 | 2.46 | 5.88 | 3.008 | 1.143 | 3.515 | 4.112 |
| reference_seed5 | ok | +0.0189 | +0.0544 | +2.700 | 2.514 | 6.211 | 3.285 | 1.155 | 3.524 | 3.898 |
| better_sep_upsampler | ok | +0.0168 | +0.0466 | +0.600 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 2.516 |
| variant_band_init | ok | +0.0147 | +0.0419 | +2.100 | 2.64 | 6.225 | 3.3 | 1.163 | 3.597 | 4.204 |
| better_chain | ok | +0.0010 | +0.0026 | +1.200 | 2.753 | 7.148 | 3.759 | 1.369 | 4.074 | 4.372 |
| better_long | ok | +0.0001 | +0.0002 | -1.100 | 2.792 | 7.248 | 3.807 | 1.388 | 4.124 | 4.236 |
| reference | ok | +0.0000 | +0.0000 | +0.000 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 4.265 |
| shortcut_forged_fields | ok | +0.0000 | - | +0.000 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 4.265 |
| shortcut_metadata | ok | +0.0000 | - | +0.000 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 4.265 |
| zz_unlisted_method_name | ok | +0.0000 | - | +0.000 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 4.265 |
| better_chain_exposure | ok | -0.1077 | -0.2449 | -4.000 | 3.205 | 8.904 | 4.923 | 1.714 | 5.139 | 4.32 |
| better_exposure | ok | -0.1082 | -0.2443 | -3.400 | 3.22 | 8.791 | 5.104 | 1.896 | 5.191 | 4.185 |
| closed_box6 | ok | -0.1164 | -0.2971 | -3.400 | 5.446 | 9.643 | 4.859 | 1.895 | 6.731 | 4.221 |
| weaker_k3 | ok | -0.2196 | -0.5225 | -4.000 | 4.029 | 12.14 | 6.081 | 2.007 | 6.5 | 4.94 |
| rgb_baseline | ok | -0.3470 | -0.7319 | -2.800 | 2.611 | 9.911 | 6.256 | 2.191 | 5.206 | 2.682 |
| ablation_rec_only | ok | -0.4445 | -1.0913 | -4.000 | 9.256 | 13.02 | 11.77 | 6.963 | 13.39 | 9.769 |
| weaker_one_epoch | ok | -0.5947 | -1.5333 | -4.000 | 11.09 | 21.26 | 12.72 | 6.046 | 14.69 | 11.42 |
| shortcut_no_upsampler | ok_without_upsampling | -0.6635 | - | -0.600 | 2.768 | 7.274 | 3.813 | 1.384 | 4.11 | 100 |
| shortcut_constant_zero | ok | -2.0863 | - | -4.000 | 53.53 | 46.83 | 14.8 | 8.183 | 53.43 | 53.65 |
| closed_pca6 | ok | -3.6136 | -9.0702 | -4.000 | 50.24 | 56.51 | 87.78 | 70.62 | 96.71 | 55.89 |
| shortcut_answer_file | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_codec | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_empty_rows | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_full_spectral | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_k9 | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_nan_weights | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_not_json | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_null_weights | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |
| shortcut_wide_encoder | failed | -4.5292 | - | -4.000 | 100 | 100 | 100 | 100 | 100 | 100 |

All metrics, test slice:

**spectral_product_broadband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 1.879 | 4.521 | 0.4439 | 1.733 |
| reference_seed4 | 2.416 | 6.072 | 0.4306 | 2.153 |
| better_color_chain | 2.46 | 5.319 | 0.4372 | 2.132 |
| better_color_chain_sep | 2.46 | 5.319 | 0.4372 | 2.132 |
| reference_seed5 | 2.514 | 6.524 | 0.4308 | 2.197 |
| reference_seed2 | 2.519 | 6.512 | 0.4309 | 2.198 |
| rgb_baseline | 2.611 | 7.298 | 0.8957 | 3.082 |
| reference_seed3 | 2.615 | 6.578 | 0.4296 | 2.154 |
| variant_band_init | 2.64 | 6.821 | 0.4305 | 2.263 |
| better_chain | 2.753 | 5.786 | 0.4253 | 2.462 |
| better_sep_upsampler | 2.768 | 5.759 | 0.4249 | 2.483 |
| reference | 2.768 | 5.759 | 0.4249 | 2.483 |
| better_long | 2.792 | 5.82 | 0.4254 | 2.53 |
| better_chain_exposure | 3.205 | 7.239 | 0.5137 | 3.242 |
| better_exposure | 3.22 | 7.179 | 0.5116 | 3.195 |
| weaker_k3 | 4.029 | 9.159 | 0.5548 | 4.31 |
| closed_box6 | 5.446 | 12.38 | 0.435 | 3.987 |
| ablation_rec_only | 9.256 | 15.48 | 0.5293 | 8.382 |
| weaker_one_epoch | 11.09 | 22.15 | 0.6018 | 11.86 |
| closed_pca6 | 50.24 | 74.48 | 1.993 | 52.68 |

**spectral_product_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 5.213 | 12.81 | 0.7072 | 4.449 |
| better_color_chain | 5.88 | 13.57 | 0.7059 | 5.342 |
| better_color_chain_sep | 5.88 | 13.57 | 0.7059 | 5.342 |
| reference_seed4 | 6.128 | 14.87 | 0.6948 | 5.305 |
| reference_seed2 | 6.142 | 15.06 | 0.6943 | 5.45 |
| reference_seed5 | 6.211 | 15.32 | 0.6942 | 5.5 |
| variant_band_init | 6.225 | 15.47 | 0.6933 | 5.664 |
| reference_seed3 | 6.25 | 13.04 | 0.6859 | 5.372 |
| better_chain | 7.148 | 15.39 | 0.6931 | 6.374 |
| better_long | 7.248 | 15.56 | 0.6927 | 6.417 |
| better_sep_upsampler | 7.274 | 15.54 | 0.6926 | 6.439 |
| reference | 7.274 | 15.54 | 0.6926 | 6.439 |
| better_exposure | 8.791 | 19.65 | 0.7602 | 8.142 |
| better_chain_exposure | 8.904 | 19.91 | 0.7651 | 8.185 |
| closed_box6 | 9.643 | 23.35 | 0.7122 | 9.679 |
| rgb_baseline | 9.911 | 23.06 | 1.012 | 9.159 |
| weaker_k3 | 12.14 | 26.33 | 0.8559 | 10.65 |
| ablation_rec_only | 13.02 | 27.35 | 0.7215 | 13.57 |
| weaker_one_epoch | 21.26 | 38.72 | 0.9017 | 20.55 |
| closed_pca6 | 56.51 | 100 | 1.802 | 56.41 |

**multibounce_narrowband**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 2.86 | 8.24 | 0.7324 | 2.547 |
| better_color_chain | 3.008 | 8.544 | 0.7219 | 2.699 |
| better_color_chain_sep | 3.008 | 8.544 | 0.7219 | 2.699 |
| reference_seed4 | 3.238 | 9.276 | 0.7122 | 2.819 |
| reference_seed2 | 3.239 | 9.221 | 0.712 | 2.859 |
| reference_seed3 | 3.244 | 9.162 | 0.6974 | 2.742 |
| reference_seed5 | 3.285 | 9.325 | 0.7118 | 2.896 |
| variant_band_init | 3.3 | 9.345 | 0.7105 | 2.949 |
| better_chain | 3.759 | 9.877 | 0.7112 | 3.341 |
| better_long | 3.807 | 9.907 | 0.7124 | 3.34 |
| better_sep_upsampler | 3.813 | 10.04 | 0.7121 | 3.351 |
| reference | 3.813 | 10.04 | 0.7121 | 3.351 |
| closed_box6 | 4.859 | 13.96 | 0.7209 | 4.69 |
| better_chain_exposure | 4.923 | 14.73 | 0.788 | 4.132 |
| better_exposure | 5.104 | 14.78 | 0.8016 | 4.389 |
| weaker_k3 | 6.081 | 17.7 | 0.8754 | 5.066 |
| rgb_baseline | 6.256 | 17.45 | 1.034 | 5.512 |
| ablation_rec_only | 11.77 | 27.2 | 1.214 | 12.33 |
| weaker_one_epoch | 12.72 | 28.81 | 1.057 | 12.07 |
| closed_pca6 | 87.78 | 100 | 2 | 87.25 |

**multibounce_proxy**

| case | mean_delta_e94_1bounce | mean_delta_e94_2bounce | mean_delta_e94_3bounce | train mean_delta_e94_3bounce |
|---|---|---|---|---|
| better_color | 2.424 | 1.662 | 0.96 | 0.8508 |
| reference_seed4 | 2.96 | 2.01 | 1.122 | 0.9869 |
| reference_seed2 | 3.018 | 2.041 | 1.137 | 1.003 |
| better_color_chain | 3.003 | 2.048 | 1.143 | 0.9776 |
| better_color_chain_sep | 3.003 | 2.048 | 1.143 | 0.9776 |
| reference_seed5 | 3.036 | 2.068 | 1.155 | 1.016 |
| variant_band_init | 3.099 | 2.102 | 1.163 | 1.019 |
| reference_seed3 | 3.092 | 2.126 | 1.235 | 1.03 |
| better_chain | 3.528 | 2.398 | 1.369 | 1.191 |
| better_sep_upsampler | 3.576 | 2.42 | 1.384 | 1.205 |
| reference | 3.576 | 2.42 | 1.384 | 1.205 |
| better_long | 3.582 | 2.425 | 1.388 | 1.212 |
| better_chain_exposure | 4.3 | 3.011 | 1.714 | 1.566 |
| closed_box6 | 5.488 | 3.55 | 1.895 | 1.644 |
| better_exposure | 4.255 | 3.087 | 1.896 | 1.734 |
| weaker_k3 | 5.627 | 3.692 | 2.007 | 1.861 |
| rgb_baseline | 4.262 | 3.551 | 2.191 | 2.18 |
| weaker_one_epoch | 11.89 | 8.93 | 6.046 | 5.912 |
| ablation_rec_only | 7.726 | 7.77 | 6.963 | 6.988 |
| closed_pca6 | 36.68 | 59.13 | 70.62 | 70.05 |

**rendered_scenes**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color | 2.85 | 7.66 | 0.5258 | 2.458 |
| reference_seed4 | 3.437 | 8.778 | 0.5135 | 2.96 |
| reference_seed2 | 3.497 | 8.919 | 0.5142 | 3.038 |
| better_color_chain | 3.515 | 8.801 | 0.5278 | 3.062 |
| better_color_chain_sep | 3.515 | 8.801 | 0.5278 | 3.062 |
| reference_seed5 | 3.524 | 8.971 | 0.5141 | 3.05 |
| reference_seed3 | 3.568 | 9.365 | 0.5057 | 3.079 |
| variant_band_init | 3.597 | 9.091 | 0.5143 | 3.116 |
| better_chain | 4.074 | 10.03 | 0.5145 | 3.627 |
| better_sep_upsampler | 4.11 | 10.24 | 0.5142 | 3.656 |
| reference | 4.11 | 10.24 | 0.5142 | 3.656 |
| better_long | 4.124 | 10.21 | 0.5144 | 3.684 |
| better_chain_exposure | 5.139 | 13.81 | 0.5915 | 4.747 |
| better_exposure | 5.191 | 13.67 | 0.5923 | 4.804 |
| rgb_baseline | 5.206 | 15.42 | 0.9379 | 4.909 |
| weaker_k3 | 6.5 | 17.58 | 0.6436 | 6 |
| closed_box6 | 6.731 | 16.22 | 0.5213 | 5.846 |
| ablation_rec_only | 13.39 | 24.14 | 0.7168 | 12.99 |
| weaker_one_epoch | 14.69 | 29.1 | 0.7108 | 14.7 |
| closed_pca6 | 96.71 | 100 | 2 | 96.26 |

**rgb_upsampling**

| case | mean_delta_e94 | p95_delta_e94 | spectral_nrmse | train mean_delta_e94 |
|---|---|---|---|---|
| better_color_chain_sep | 2.379 | 6.51 | 0.5222 | 2.231 |
| better_sep_upsampler | 2.516 | 6.297 | 0.5182 | 2.467 |
| rgb_baseline | 2.682 | 7.919 | 0.904 | 3.046 |
| reference_seed2 | 3.71 | 7.219 | 0.5856 | 3.504 |
| reference_seed5 | 3.898 | 7.259 | 0.5901 | 3.663 |
| better_color | 3.911 | 7.288 | 0.5897 | 3.622 |
| reference_seed4 | 3.99 | 7.383 | 0.5927 | 3.734 |
| better_color_chain | 4.112 | 7.42 | 0.6118 | 3.896 |
| better_exposure | 4.185 | 7.713 | 0.6437 | 4.077 |
| variant_band_init | 4.204 | 7.481 | 0.5934 | 3.994 |
| closed_box6 | 4.221 | 7.625 | 0.6141 | 3.94 |
| better_long | 4.236 | 7.649 | 0.5879 | 4.049 |
| reference | 4.265 | 7.579 | 0.59 | 4.014 |
| reference_seed3 | 4.267 | 7.627 | 0.6029 | 3.966 |
| better_chain_exposure | 4.32 | 7.743 | 0.6329 | 4.251 |
| better_chain | 4.372 | 7.701 | 0.5964 | 4.149 |
| weaker_k3 | 4.94 | 8.791 | 0.59 | 4.87 |
| ablation_rec_only | 9.769 | 14.22 | 0.7951 | 9.314 |
| weaker_one_epoch | 11.42 | 22.4 | 0.6229 | 11.71 |
| closed_pca6 | 55.89 | 77.4 | 1.994 | 55.07 |
