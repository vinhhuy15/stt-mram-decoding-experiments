# STT-MRAM Decoding Experiments

> A modular Monte-Carlo simulation framework for STT-MRAM channel modeling and decoder evaluation, with baseline reproduction of the 7/9-Rate Sparse Code.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.21%2B-013243?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.4%2B-blue)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project reproduces and extends the results from the following paper:

> **"On the Design of 7/9-Rate Sparse Code for Spin-Torque Transfer Magnetic Random Access Memory"**  
> Chi Dinh Nguyen, FPT University, Hanoi — *IEEE Access*, Vol. 9, 2021  
> DOI: [10.1109/ACCESS.2021.3134282](https://doi.org/10.1109/ACCESS.2021.3134282)

**Primary goals:**
- Reproduce Figures 5–10 from the paper using Monte-Carlo simulation
- Provide a clean, extensible framework for benchmarking new decoder architectures against the baseline

---

## Project Structure

```
project_stt_mram/
│
├── config.py                      ← Global config (plot style, paths, constants)
├── codebook.py                    ← 128-codeword codebook (weight 2 & 4, n=9)
├── channel.py                     ← Cascade channel: BAC → Z-channel → GMC
├── decoders.py                    ← Baseline decoders: ML soft + hard threshold
├── metrics.py                     ← BER / FER computation, idx ↔ bits conversion
├── simulation.py                  ← Monte-Carlo engine + result caching (save/load)
│
├── experiments/
│   ├── fig5_attenuator.py         ← BER/FER vs α (attenuator sweep)
│   ├── fig6_ber_vs_p1.py          ← BER vs write error probability P₁
│   ├── fig7_sigma_no_offset.py    ← BER/FER vs σ₀/μ₀ (no temperature offset)
│   ├── fig8_offset_4pct.py        ← BER/FER vs σ₀/μ₀ (σ_ofs = 4%)
│   ├── fig9_offset_7pct.py        ← BER/FER vs σ₀/μ₀ (σ_ofs = 7%)
│   ├── fig10_comparison.py        ← Offset comparison: 4% vs 7%
│   ├── summary_dashboard.py       ← All 6 figures in a single dashboard image
│   └── exp_custom_decoder_template.py  ← ⭐ Start here to test a new decoder
│
├── results/                       ← Auto-generated .npz cache files (on first run)
├── figures/                       ← Output PNG figures
│
├── plans/                         ← Research notes and paper analysis
├── rules/                         ← Project conventions and workflow guides
│
├── run_all.py                     ← Run all baseline experiments
└── check_setup.py                 ← Verify environment setup
```

---

## Requirements

```bash
pip install numpy matplotlib
```

- Python >= 3.9
- No GPU required — all simulations run on CPU via NumPy

---

## Quick Start

### 1. Verify your environment
```bash
python check_setup.py
```

### 2. Run all 6 baseline figures
```bash
# Full run (300k frames/point, ~30–60 min)
python run_all.py

# Quick test to verify correctness (10k frames/point, ~2 min)
python run_all.py --quick
```

### 3. Run a specific figure
```bash
python experiments/fig7_sigma_no_offset.py
python experiments/fig5_attenuator.py
# ... and so on
```

Output files will be saved to:
- `results/*.npz` — numerical results (cached)
- `figures/*.png` — plot images

---

## Testing a New Decoder

The core design goal of this framework is to make it easy to plug in and compare a custom decoder against the baseline. Here is the full workflow:

### Step 1 — Implement your decoder in `decoders.py`

Add a new function at the bottom of `decoders.py`. The two existing baseline functions serve as references:

```python
# decoders.py

def my_new_decoder(received: np.ndarray, **ctx) -> np.ndarray:
    """
    Args:
        received : (N, 9) float32  — continuous signal from the GMC channel
        ctx      : dict containing {alpha, threshold, mu0, mu1, sig0, sig1_eff}

    Returns:
        (N,) int32  — user-data index in range [0, 127]
    """
    alpha     = ctx['alpha']
    threshold = ctx['threshold']
    mu0, mu1  = ctx['mu0'], ctx['mu1']
    sig0      = ctx['sig0']

    # --- Your decoding logic here ---
    from codebook import CB
    r = (received / alpha).astype('float32')
    # ...
    return decoded_indices  # shape (N,), dtype int32
```

> **Note:** Only the decoder function needs to be implemented. You do not need to modify `simulation.py` or any engine file.

### Step 2 — Create an experiment file from the template

```powershell
Copy-Item experiments\exp_custom_decoder_template.py experiments\exp_my_new_decoder.py
```

Open the new file and edit **two lines**:

```python
# ① Set a unique name for your experiment (used in output filenames)
EXPERIMENT_NAME = "my_new_decoder"

# ② Import and wire up your decoder
from decoders import my_new_decoder

def my_decoder(received, **ctx):
    return my_new_decoder(received, **ctx)
```

### Step 3 — Run and compare

```bash
# First run: computes and caches results (~30–60 min with 300k frames)
python experiments/exp_my_new_decoder.py

# Subsequent runs: loads from cache instantly (~1 sec)
python experiments/exp_my_new_decoder.py

# Force recompute (e.g., after modifying your decoder)
python experiments/exp_my_new_decoder.py --rerun
```

**Example console output:**
```
--- Experiment: my_new_decoder (Fig 7, n=300,000) ---
  σ/μ=8%   baseline=1.2e-04  custom=8.5e-05  raw=5.0e-04
  σ/μ=9%   baseline=3.4e-04  custom=2.1e-04  raw=1.3e-03
  ...
  [saved] results/custom_my_new_decoder_fig7.npz
  → Saved figures/custom_my_new_decoder_fig7.png
```

### Data Flow

```
decoders.py              ← Add your decoder function here
     │
     ▼
experiments/
exp_my_new_decoder.py    ← Copy from template, edit 2 lines
     │  (calls simulate() with custom_decoder=)
     ▼
simulation.py            ← No changes needed
     │  (runs channel + baseline + custom in parallel)
     ▼
results/*.npz            ← Cached numerical results
figures/*.png            ← Comparison plots
```

---

## Key Parameters

| Parameter | Description | Paper Value |
|-----------|-------------|-------------|
| `P1` | Write error probability (0→1, dominant) | `2e-4` |
| `sigma_ratio` | σ₀/μ₀ = σ₁/μ₁ (fabrication quality) | `0.09` (9%) |
| `alpha` | Attenuation factor for the ML decoder | `2.5` (optimal from Fig 5) |
| `mu0`, `mu1` | Mean resistance levels (kΩ) | `1.0`, `2.0` |
| `mu_ofs` | Resistance offset due to temperature (kΩ) | `0.0` or `-0.2` |
| `sig_ofs_ratio` | σ_ofs / μ₁ | `0.0`, `0.04`, `0.07` |
| `n_frames` | Number of Monte-Carlo frames | `300_000` |

---

## Baseline Results Summary

| Figure | Key Finding |
|--------|-------------|
| Fig 5  | Optimal attenuator α = **2.5** (matches paper) |
| Fig 6  | Raw error floor ≈ 10⁻³; sparse code ≈ 10⁻⁴ |
| Fig 7  | Code improves tolerance by ~2.2% in σ₀/μ₀ over raw data |
| Fig 8–9 | Code is significantly less sensitive to temperature offset |
| Fig 10 | At σ₀/μ₀ ≥ 5%, the 7% offset starts to show visible degradation |

---

## Notes

- The `results/` directory is created automatically on the first run.
- After modifying a decoder, always use `--rerun` to invalidate the cache.
- Increase `n_frames` to `2_000_000` for BER curves at very low error rates (≈7× slower but closer to the paper).

---

## License

This project is for research and educational purposes. See [LICENSE](LICENSE) for details.
