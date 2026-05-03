#!/usr/bin/env python3
"""
Fig 5 – BER & FER vs attenuator α  (P₁=2×10⁻⁴, σ₀/μ₀=10%)

Sweeps the attenuator factor α to find the optimal value for
the ML soft decoder. Paper reports α_opt = 2.5.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate
from config import OUT_DIR, safe


def run(n_frames: int = 300_000):
    """Run Fig 5 experiment and return (alphas, ber, fer)."""
    alphas = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0]
    ber, fer = [], []

    print("\n─── Fig 5: BER/FER vs attenuator α ───")
    for a in alphas:
        r = simulate(n_frames=n_frames, P1=2e-4, sigma_ratio=0.10,
                     alpha=a, batch=5000)
        ber.append(safe(r['BER_soft']))
        fer.append(safe(r['FER_soft']))
        print(f"  α={a:.1f}  BER={r['BER_soft']:.2e}  FER={r['FER_soft']:.2e}")

    return alphas, ber, fer


def plot(alphas, ber, fer, save=True):
    """Create and optionally save Fig 5."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(alphas, fer, 'k-^', label='FER – decoder output')
    ax.semilogy(alphas, ber, 'b-o', label='BER – decoder output')
    ax.set_xlabel('α (attenuator factor)')
    ax.set_ylabel('BER & FER Performance')
    ax.set_xlim(1, 8);  ax.set_ylim(1e-4, 1)
    ax.legend(loc='upper right')
    ax.set_title('Fig 5 – Performance vs Attenuator α\n'
                 '(P₁=2×10⁻⁴, σ₀/μ₀=10%)')
    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'fig5_attenuator.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    alphas, ber, fer = run()
    plot(alphas, ber, fer)

    alpha_best = alphas[int(np.argmin(ber))]
    print(f"  Best α = {alpha_best}  (paper reports 2.5)")
