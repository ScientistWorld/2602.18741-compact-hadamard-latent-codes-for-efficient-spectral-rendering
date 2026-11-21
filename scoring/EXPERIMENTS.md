# Experiment Overview

All experiments compare a compact representation, rendered with at most two
RGB-equivalent passes, against full 47-sample spectral rendering on held-out
reflectance and light spectra.

## spectral_product_broadband

Establishes that a compact representation keeps colour accurate for a single
material-light interaction under ordinary broadband lights (lamps, LEDs,
fluorescents, daylight-like and unusual flipped spectra). This is the common
case; standard RGB rendering is already fairly good here, so it guards against
methods that trade everyday accuracy for stress-case gains.

## spectral_product_narrowband

Establishes accuracy for a single interaction under spiky narrowband lights,
the stress case where RGB rendering loses wavelength-specific information and
shows large colour shifts.

## multibounce_narrowband

Establishes that errors stay controlled when light interacts with three
materials in a row under narrowband illumination, rather than compounding.

## multibounce_proxy

Mirrors the paper's own selection protocol: the same chains measured after
one, two and three interactions under a mix of broadband and narrowband
lights. It checks stability across interaction counts and connects the gym to
the paper's reported numbers.

## rendered_scenes

Establishes accuracy for rendered pixels, where many light paths of different
depths, from several lights of different intensities, are scaled and summed.
It tests that the representation behaves correctly under all operations a
renderer applies together, including deep interreflections, which is where
approximation error is expected to show most.

## rgb_upsampling

Establishes whether assets that only exist as RGB values (legacy textures and
light colours) can be brought into the compact representation and rendered
more faithfully than ordinary RGB rendering, under broadband illumination as
in typical production scenes.

## Validity

Each submission must stay within two RGB-equivalent passes and produce finite
results; otherwise every metric of every experiment takes its worst value.
