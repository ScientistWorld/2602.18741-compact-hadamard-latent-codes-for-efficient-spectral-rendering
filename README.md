# Compact Hadamard Latent Codes for Efficient Spectral Rendering

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

<!-- hardening-note -->
> [!NOTE]
> **Red-teamed and hardened.** A red team tried to score on this environment's hidden test without doing better research, and the environment was then fixed against the shortcuts that worked: see [`REDTEAM.md`](REDTEAM.md) and [`HARDENING.md`](HARDENING.md). The environment as it was before is kept as branch [`pre-hardening`](../../tree/pre-hardening).

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2602.18741"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2602.18741-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2602.18741](https://arxiv.org/abs/2602.18741) |
|:---|:---|
| **Domain** | Computer Graphics / Spectral Rendering |
| **TL;DR** | The paper learns compact spectral codes that can be rendered as a few RGB passes while approximating full spectral rendering much more accurately than ordinary RGB rendering. |

## Summary

Full spectral rendering is accurate under wavelength-dependent materials and illumination, but it is much more expensive than RGB rendering because it evaluates many wavelength samples. This paper proposes a compact latent spectral representation designed to support rendering-style composition, allowing spectral assets to be rendered through standard RGB infrastructure and decoded back to spectra or display colors. The reported main configuration uses six latent channels, rendered as two RGB passes, and is evaluated against 47-channel spectral rendering ground truth. The paper also studies RGB-asset conversion, narrowband illumination stress cases, and stability across repeated light-material interactions.

## Problem

Can a renderer produce images that match full spectral rendering much more closely than standard RGB rendering while using only a small number of RGB-like render passes? The challenge is to preserve wavelength-dependent color behavior under varied reflectances, broadband lights, narrowband lights, and repeated material-light interactions without paying the cost of rendering dozens of wavelength samples per shading operation.

## The paper's method

The paper introduces Hadamard spectral codes: compact nonnegative latent vectors for spectra that are meant to be manipulated with the same scaling, addition, and elementwise multiplication operations used in rendering. The main practical point is that a `k`-channel code can be split into RGB triplets and rendered through an unmodified RGB renderer in `k / 3` passes.

## Key results of the paper

- The `k=6` setting uses two RGB render passes instead of 47 spectral samples, reported as roughly a `23x` render-pass reduction.
- In a synthetic multi-bounce test used for model selection, the selected configuration reports mean CIE94 errors of `2.16`, `1.79`, and `1.74` for one, two, and three bounces.
- The paper claims lower color error than standard RGB rendering, especially under narrowband illumination, while remaining visually close to 47-channel spectral ground truth in several rendered scenes.

## Run it

```bash
pip install sciworld
sw research 2602.18741 --mode innovate --agent claude-code
sw evaluate 2602.18741
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

