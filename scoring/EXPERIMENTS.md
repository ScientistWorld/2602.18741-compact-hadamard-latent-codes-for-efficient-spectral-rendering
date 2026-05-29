# Experiment Overview

## spectral_color_accuracy

Tests the central claim that a compact rendering pipeline can produce images closer to full spectral rendering than standard RGB rendering. The experiment covers the main scene conditions and reports color or image error against spectral ground truth.

## render_pass_efficiency

Tests whether the method achieves its accuracy within the intended compact rendering budget. This experiment exists to prevent improvements that simply use many more spectral samples or render passes.

## multibounce_stability

Tests whether the method remains reliable when light undergoes repeated interactions with scene materials. The purpose is to measure error accumulation under deeper transport, not just single-interaction reconstruction.

## narrowband_robustness

Tests the harder illumination setting where RGB rendering tends to produce large color shifts. The experiment asks whether the candidate method remains close to spectral ground truth under spiky or narrowband light spectra.

## rgb_asset_compatibility

Tests whether the system can handle scenes whose source assets are ordinary RGB colors or textures. The purpose is to evaluate practical compatibility with existing assets while still judging output against spectral ground truth.
