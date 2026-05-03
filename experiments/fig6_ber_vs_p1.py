#!/usr/bin/env python3
"""
Fig 6 – BER vs write-error rate P₁  (σ₀/μ₀=9%, α=2.5, no offset)

Compares BER of proposed code (soft & hard decoders) against raw data
across a range of write error rates P₁.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate
from config import OUT_DIR, safe


def run(n_frames: int = 300_000, alpha: float = 2.5):
    """Run Fig 6 experiment and return (P1_vals, ber_soft, ber_hard, ber_raw)."""
    P1_vals = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3]
    ber_s, ber_h, ber_r = [], [], []

    print("\n─── Fig 6: BER vs write-error rate P₁ (σ₀/μ₀=9%) ───")
    for P1 in P1_vals:
        r = simulate(n_frames=n_frames, P1=P1, sigma_ratio=0.09,
                     alpha=alpha, batch=5000)
        ber_s.append(safe(r['BER_soft']))
        ber_h.append(safe(r['BER_hard']))
        ber_r.append(safe(r['BER_raw']))
        print(f"  P1={P1:.0e}  soft={r['BER_soft']:.2e}  "
              f"hard={r['BER_hard']:.2e}  raw={r['BER_raw']:.2e}")

    return P1_vals, ber_s, ber_h, ber_r


def plot(P1_vals, ber_s, ber_h, ber_r, save=True):
    """Create and optionally save Fig 6."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(P1_vals, ber_s, 'b-o',   label='Proposed code – decoder output')
    ax.semilogx(P1_vals, ber_h, 'b--s',  label='Proposed code – detector output')
    ax.semilogx(P1_vals, ber_r, 'r-^',   label='Raw data w/o coding – detector output')
    ax.set_xlabel('P₁ (write error rate 0→1)')
    ax.set_ylabel('BER')
    ax.set_xlim(1e-8, 1e-3)
    ax.legend(fontsize=8)
    ax.set_title('Fig 6 – BER vs Write Error Rate P₁\n'
                 '(σ₀/μ₀=9%, α=2.5)')
    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'fig6_ber_vs_P1.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    P1_vals, ber_s, ber_h, ber_r = run()
    plot(P1_vals, ber_s, ber_h, ber_r)
