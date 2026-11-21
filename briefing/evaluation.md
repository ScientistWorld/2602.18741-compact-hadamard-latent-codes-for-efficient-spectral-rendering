# Evaluation

## What a method submits

Each method is one directory `outputs/<method_name>/` containing `codec.json`.
Every directory under `outputs/` is scored; the directory name is the method name.
The file describes, as small feed-forward networks, how the method represents
spectra compactly. Everything else (held-out spectra, rendered instances,
the renderer, exposure, colorimetry, metrics) belongs to the evaluator.

```json
{
  "encoder": NET,                  // spectrum (47) -> code (k); or give
  "encoder_reflectance": NET,      //   separate encoders for reflectances
  "encoder_illuminant": NET,       //   and light emission spectra
  "decoder": NET,                  // code (k) -> spectrum (47)
  "upsampler": NET,                // linear sRGB (3) -> code (k); or give
  "upsampler_reflectance": NET,    //   separate upsamplers per asset type
  "upsampler_illuminant": NET
}
```

`NET` is either a plain matrix (`out x in`, a linear map without bias) or
`{"layers": [{"weight": out x in, "bias": [out] (optional), "activation": A, "beta": b (softplus only)}, ...]}`
with `A` one of `identity`, `linear`, `relu`, `leaky_relu`, `softplus`,
`silu`, `sigmoid`, `tanh`, `elu`, `gelu`, `abs`, `square`. Each network may
have at most 2,000,000 parameters. Other fields in the file are ignored.

## How the evaluator renders

1. Encode every reflectance and every light with the method's encoders.
   Negative code values are clamped to zero, as an RGB renderer cannot carry
   negative albedo or emission.
2. Render in code space with the operations an unmodified RGB renderer
   performs on each channel: per-channel multiplication at every
   light-material interaction, scaling by geometric/intensity factors, and
   summation over light paths. Each group of three channels is one RGB pass.
3. Decode the rendered code once with the method's decoder; negative decoded
   values are clamped to zero.
4. Compare with the full 47-sample spectral render of the same instance.

The ground truth is spectral rendering on 47 samples over 368-830 nm
(zero outside 400-700 nm).

## Validity gates

A submission fails, and receives the worst value of every metric in every
experiment, if: `codec.json` is missing or unreadable; a network is malformed
(shape mismatch, unknown activation, non-finite or non-numeric weights, too
many parameters); the two encoders disagree on the code width; the code width
is not between 1 and 6 channels (at most two RGB passes); or any code or
decoded spectrum on the test inputs is non-finite. Missing or malformed
upsamplers fail only the RGB-upsampling experiment. Worst values: CIE94
error 100 (per-sample errors are also capped at 100), relative spectral
error 2.0 (per-sample errors capped at 2.0).

## Colorimetry

- CIE 1931 2-degree colour-matching functions, box-resampled to the 47-sample grid.
- XYZ is normalised so that the equal-energy spectrum over 400-700 nm has Y = 1;
  that spectrum is also the CIELAB reference white.
- Colour error: CIE94 (graphic arts weights), ground truth as reference.
- Spectral error (`spectral_nrmse`): per sample `||decoded - true|| / ||true||`
  over the 47 samples, averaged.
- Exposure: product and chain experiments scale prediction and ground truth by
  the same factor, chosen so that a perfect white reflector under the light
  reaches 1 in its strongest normalised tristimulus channel. Scenes use a
  per-scene auto-exposure (90th-percentile pixel brought to 0.8). The
  multi-bounce proxy uses no re-exposure (the paper's protocol).

## Experiments

| experiment | instances | metrics |
|---|---|---|
| `spectral_product_broadband` | 4,000 held-out reflectance x broadband-light products | mean / p95 CIE94, spectral_nrmse |
| `spectral_product_narrowband` | 4,000 products with spiky narrowband lights | mean / p95 CIE94, spectral_nrmse |
| `multibounce_narrowband` | 3,000 light x 3-reflectance chains, narrowband lights | mean / p95 CIE94, spectral_nrmse |
| `multibounce_proxy` | 3,000 chains S1, S2, S3 (half broadband, half narrowband lights) | mean CIE94 per bounce |
| `rendered_scenes` | 300 scenes x 48 pixels; each pixel sums 30 weighted paths of depth 1-8 from two lights (broadband or narrowband, random intensity) over ten materials | mean / p95 CIE94, spectral_nrmse |
| `rgb_upsampling` | 4,000 products under broadband lights where the method only sees each asset's linear-sRGB value (through its upsamplers) | mean / p95 CIE94, spectral_nrmse |

Legacy RGB values (`data/spectral_data.py: asset_rgb`): a reflectance's
albedo is its linear sRGB under D65 divided channelwise by the linear sRGB of
D65 (white maps to 1, 1, 1); a light's value is its linear-sRGB radiance.
Negative values are clipped to zero.

## Baseline

`rgb_baseline` is ordinary RGB rendering in the same interface: assets are
converted to linear-sRGB albedo / radiance, multiplied per channel in one
pass, and the rendered RGB is shown as a nonnegative spectrum with exactly
that colour. On legacy RGB assets it needs no upsampling.

## Data

`data/spectra_train.json` holds the public training spectra: measured matt
Munsell reflectances plus saturated synthetic reflectances, and measured,
standard and synthetic lamp, daylight-derived, blackbody, flipped and
narrowband light spectra, with their colour-matching functions and D65.
Held-out reflectances and lights of the same families are used only by the
hidden test and are never available to a method.

## Running

- `bash scripts/evaluate_train.sh` scores every method under `outputs/` on the
  training spectra and writes `scoring/scores_train.json`.
- `bash scripts/evaluate_test.sh` (hidden) runs the identical protocol on the
  held-out spectra and writes `scoring/scores_test.json`.

## Paper targets

The paper's multi-bounce selection proxy reports mean CIE94 errors of 2.16,
1.79 and 1.74 for one, two and three interactions with a six-channel code
rendered in two RGB passes, about a 23x render-pass reduction over 47-sample
spectral rendering. Its rendered-scene comparisons show clearly larger RGB
rendering errors under narrowband illumination.
