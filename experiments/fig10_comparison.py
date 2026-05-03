#!/usr/bin/env python3
"""
Fig 10 – BER of proposed code: σ_ofs/μ₁=4% vs 7% offset comparison.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from config import OUT_DIR


def plot(sig_pct, ber_4pct, ber_7pct, save=True):
    """Create and optionally save Fig 10."""
    print("\n─── Fig 10: BER comparison – σofs/μ₁=4% vs 7% ───")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(sig_pct, ber_4pct, 'k-^', label='Proposed code, σofs/μ₁=4%')
    ax.semilogy(sig_pct, ber_7pct, 'b-o', label='Proposed code, σofs/μ₁=7%')
    ax.set_xlabel('σ₀/μ₀ (%)')
    ax.set_ylabel('BER')
    ax.legend(fontsize=9)
    ax.set_title('Fig 10 – BER under Different Offset Variations\n'
                 '(μofs=−0.2 kΩ, P₁=2×10⁻⁴, α=2.5)')
    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'fig10_offset_comparison.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    from fig8_offset_4pct import run as run8
    from fig9_offset_7pct import run as run9
    sig_pct, r8 = run8()
    _,       r9 = run9()
    plot(sig_pct, r8['bs'], r9['bs'])
