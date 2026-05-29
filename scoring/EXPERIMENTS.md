# Experiment Overview

## spectral_product_broadband

This experiment checks whether compact spectral rendering can approximate full spectral material-light products under ordinary broadband lights. It is the easiest central setting and confirms that accuracy is not lost in common illumination.

## spectral_product_narrowband

This experiment checks the paper's most important stress case: spiky illumination where RGB rendering loses wavelength-specific information. A useful method should produce lower color error than the RGB baseline while keeping a compact pass budget.

## multibounce_narrowband

This experiment checks whether error remains controlled after repeated light-material interactions. It prevents methods from only solving a one-bounce color match while failing when products are composed multiple times.

## rgb_upsampling_narrowband

This experiment checks whether legacy RGB assets can be lifted into the compact latent rendering pipeline and still beat ordinary RGB rendering under narrowband lights. It evaluates the practical integration claim separately from the native spectral-asset codec.
