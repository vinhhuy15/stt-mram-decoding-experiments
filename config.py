#!/usr/bin/env python3
"""
Global configuration for STT-MRAM sparse code experiments.

Centralizes all shared settings: plot style, output paths, and default
simulation parameters so that individual experiment scripts stay clean.
"""

import os
import sys

# ── Fix Unicode output on Windows ─────────────────────────────────────────────
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Output directory ──────────────────────────────────────────────────────────
# Figures are saved next to the code by default; override via env variable.
OUT_DIR = os.environ.get(
    'STT_MRAM_OUT',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Matplotlib global style ───────────────────────────────────────────────────
plt.rcParams.update({
    'font.size': 10,
    'lines.linewidth': 1.8,
    'lines.markersize': 5,
    'axes.grid': True,
    'grid.alpha': 0.35,
})

# ── Default simulation parameters (Section IV of paper) ──────────────────────
DEFAULT_PARAMS = dict(
    mu0       = 1.0,        # low-resistance mean (kΩ)
    mu1       = 2.0,        # high-resistance mean (kΩ)
    alpha     = 2.5,        # optimal attenuator factor (Fig 5)
    P1        = 2e-4,       # dominant write error rate 0→1
    sigma_ratio = 0.09,     # σ₀/μ₀ = σ₁/μ₁  (fabrication quality)
    mu_ofs    = 0.0,        # mean resistance offset (kΩ)
    sig_ofs_ratio = 0.0,    # σ_ofs / μ₁
    n_frames  = 300_000,    # Monte-Carlo frames per simulation point
    batch     = 5000,       # batch size for vectorised processing
)

# ── Utility ───────────────────────────────────────────────────────────────────
def safe(v: float) -> float:
    """Clip zero values so log-scale plots work."""
    return max(v, 1e-7)
