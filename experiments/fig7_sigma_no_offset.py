#!/usr/bin/env python3
"""
Fig 7 – BER & FER vs σ₀/μ₀  (P₁=2×10⁻⁴, no offset, α=2.5)

Compares proposed code (soft decoder, hard detector) against raw data
across a range of fabrication variation σ₀/μ₀ from 8% to 15%.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate
from config import OUT_DIR, safe


def run(n_frames: int = 300_000, alpha: float = 2.5):
    """Run Fig 7 experiment and return (sig_pct, results_dict)."""
    sig_vals = np.arange(8, 16) / 100.0   # 8% to 15%
    r7 = {k: [] for k in ['bs', 'fs', 'bh', 'fh', 'br', 'fr']}

    print("\n─── Fig 7: BER/FER vs σ₀/μ₀ (no offset, P₁=2×10⁻⁴) ───")
    for sr in sig_vals:
        res = simulate(n_frames=n_frames, P1=2e-4, sigma_ratio=sr,
                       alpha=alpha, batch=5000)
        r7['bs'].append(safe(res['BER_soft']));  r7['fs'].append(safe(res['FER_soft']))
        r7['bh'].append(safe(res['BER_hard']));  r7['fh'].append(safe(res['FER_hard']))
        r7['br'].append(safe(res['BER_raw']));   r7['fr'].append(safe(res['FER_raw']))
        print(f"  σ/μ={sr*100:.0f}%  BER_soft={res['BER_soft']:.2e}  "
              f"BER_raw={res['BER_raw']:.2e}")

    sig_pct = sig_vals * 100
    return sig_pct, r7


def plot(sig_pct, r7, save=True):
    """Create and optionally save Fig 7."""
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.semilogy(sig_pct, r7['bs'], 'k-^',  label='BER – decoder output')
    ax.semilogy(sig_pct, r7['fs'], 'k--^', label='FER – decoder output')
    ax.semilogy(sig_pct, r7['bh'], 'b-o',  label='BER – detector output')
    ax.semilogy(sig_pct, r7['fh'], 'b--o', label='FER – detector output')
    ax.semilogy(sig_pct, r7['br'], 'r-s',  label='BER – raw data w/o coding')
    ax.semilogy(sig_pct, r7['fr'], 'r--s', label='FER – raw data w/o coding')
    ax.set_xlabel('σ₀/μ₀ (%)')
    ax.set_ylabel('BER & FER')
    ax.legend(fontsize=7, loc='upper left')
    ax.set_title('Fig 7 – Performance vs σ₀/μ₀ (no offset, P₁=2×10⁻⁴, α=2.5)')
    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'fig7_ber_vs_sigma.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    sig_pct, r7 = run()
    plot(sig_pct, r7)
