#!/usr/bin/env python3
"""
Fig 9 – BER & FER vs σ₀/μ₀  (offset: μ_ofs=−0.2 kΩ, σ_ofs/μ₁=7%)

Studies the impact of a larger 7% temperature-induced resistance offset
on the proposed code vs raw data.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate
from config import OUT_DIR, safe


def run(n_frames: int = 300_000, alpha: float = 2.5):
    """Run Fig 9 experiment and return (sig_pct, results_dict)."""
    sig_vals = np.arange(2, 11) / 100.0   # 2% to 10%
    r9 = {k: [] for k in ['bs', 'fs', 'bh', 'fh', 'br', 'fr']}

    print("\n─── Fig 9: BER/FER vs σ₀/μ₀ (μofs=−0.2 kΩ, σofs/μ₁=7%) ───")
    for sr in sig_vals:
        res = simulate(n_frames=n_frames, P1=2e-4, sigma_ratio=sr,
                       alpha=alpha, mu_ofs=-0.2, sig_ofs_ratio=0.07, batch=5000)
        r9['bs'].append(safe(res['BER_soft']));  r9['fs'].append(safe(res['FER_soft']))
        r9['bh'].append(safe(res['BER_hard']));  r9['fh'].append(safe(res['FER_hard']))
        r9['br'].append(safe(res['BER_raw']));   r9['fr'].append(safe(res['FER_raw']))
        print(f"  σ/μ={sr*100:.0f}%  BER_soft={res['BER_soft']:.2e}  "
              f"BER_raw={res['BER_raw']:.2e}")

    sig_pct = sig_vals * 100
    return sig_pct, r9


def plot(sig_pct, r9, save=True):
    """Create and optionally save Fig 9."""
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.semilogy(sig_pct, r9['br'], 'r-^',  label='BER – raw data w/o coding')
    ax.semilogy(sig_pct, r9['fr'], 'r--^', label='FER – raw data w/o coding')
    ax.semilogy(sig_pct, r9['bh'], 'g-o',  label='BER – proposed code, detector')
    ax.semilogy(sig_pct, r9['fh'], 'g--o', label='FER – proposed code, detector')
    ax.semilogy(sig_pct, r9['bs'], 'b-s',  label='BER – proposed code, decoder')
    ax.semilogy(sig_pct, r9['fs'], 'b--s', label='FER – proposed code, decoder')
    ax.set_xlabel('σ₀/μ₀ (%)')
    ax.set_ylabel('BER & FER')
    ax.legend(fontsize=7, loc='upper left')
    ax.set_title('Fig 9 – Performance with Offset\n'
                 '(μofs=−0.2 kΩ, σofs/μ₁=7%, P₁=2×10⁻⁴, α=2.5)')
    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'fig9_offset7pct.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    sig_pct, r9 = run()
    plot(sig_pct, r9)
