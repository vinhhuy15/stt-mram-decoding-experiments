#!/usr/bin/env python3
"""
Run all baseline experiments (Figures 5–10) and generate the summary dashboard.

Usage:
    python run_all.py              # full run (300k frames/point)
    python run_all.py --quick      # quick test run (10k frames/point)
"""

import sys
import numpy as np

# Ensure project root is on path
sys.path.insert(0, __file__ and __import__('os').path.dirname(
    __import__('os').path.abspath(__file__)) or '.')

import config  # noqa: F401 – loads UTF-8 fix and plot style

from experiments import fig5_attenuator
from experiments import fig6_ber_vs_p1
from experiments import fig7_sigma_no_offset
from experiments import fig8_offset_4pct
from experiments import fig9_offset_7pct
from experiments import fig10_comparison
from experiments import summary_dashboard


def main():
    np.random.seed(42)

    # Parse --quick flag
    n_frames = 10_000 if '--quick' in sys.argv else 300_000
    print(f"Running with n_frames={n_frames:,}")

    # ── Fig 5 ────────────────────────────────────────────────────
    alphas, ber5, fer5 = fig5_attenuator.run(n_frames)
    fig5_attenuator.plot(alphas, ber5, fer5)

    ALPHA = 2.5  # paper's recommended value

    # ── Fig 6 ────────────────────────────────────────────────────
    P1_vals, ber6_s, ber6_h, ber6_r = fig6_ber_vs_p1.run(n_frames, ALPHA)
    fig6_ber_vs_p1.plot(P1_vals, ber6_s, ber6_h, ber6_r)

    # ── Fig 7 ────────────────────────────────────────────────────
    sp7, r7 = fig7_sigma_no_offset.run(n_frames, ALPHA)
    fig7_sigma_no_offset.plot(sp7, r7)

    # ── Fig 8 ────────────────────────────────────────────────────
    sp8, r8 = fig8_offset_4pct.run(n_frames, ALPHA)
    fig8_offset_4pct.plot(sp8, r8)

    # ── Fig 9 ────────────────────────────────────────────────────
    _, r9 = fig9_offset_7pct.run(n_frames, ALPHA)
    fig9_offset_7pct.plot(sp8, r9)

    # ── Fig 10 ───────────────────────────────────────────────────
    fig10_comparison.plot(sp8, r8['bs'], r9['bs'])

    # ── Summary Dashboard ────────────────────────────────────────
    summary_dashboard.plot_dashboard(
        alphas, ber5, fer5,
        P1_vals, ber6_s, ber6_h, ber6_r,
        sp7, r7,
        sp8, r8,
        r9,
    )

    print("\n✓ All experiments complete.")


if __name__ == '__main__':
    main()
