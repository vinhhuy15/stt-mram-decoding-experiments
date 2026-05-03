#!/usr/bin/env python3
"""
Summary Dashboard – All 6 figures (5–10) in a single PNG.
Requires pre-computed results from the individual experiment scripts.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from config import OUT_DIR


def plot_dashboard(alphas, ber5, fer5,
                   P1_vals, ber6_s, ber6_h, ber6_r,
                   sp7, r7,
                   sp8, r8,
                   r9,
                   save=True):
    """Build combined summary figure with all 6 subplots."""
    print("\n─── Building combined summary figure ───")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle(
        'Baseline Reproduction – 7/9-Rate Sparse Code for STT-MRAM\n'
        '(Chi Dinh Nguyen, IEEE Access 2021)',
        fontsize=13, fontweight='bold'
    )

    # 5
    ax = axes[0, 0]
    ax.semilogy(alphas, fer5, 'k-^', label='FER')
    ax.semilogy(alphas, ber5, 'b-o', label='BER')
    ax.set_xlabel('α');  ax.set_ylabel('BER & FER')
    ax.set_xlim(1, 8);   ax.set_ylim(1e-4, 1)
    ax.legend(fontsize=8)
    ax.set_title('Fig 5 – vs Attenuator α\n(P₁=2×10⁻⁴, σ₀/μ₀=10%)')

    # 6
    ax = axes[0, 1]
    ax.semilogx(P1_vals, ber6_s, 'b-o',  label='Proposed, decoder', ms=4)
    ax.semilogx(P1_vals, ber6_h, 'b--s', label='Proposed, detector', ms=4)
    ax.semilogx(P1_vals, ber6_r, 'r-^',  label='Raw data', ms=4)
    ax.set_xlabel('P₁');   ax.set_ylabel('BER')
    ax.legend(fontsize=7)
    ax.set_title('Fig 6 – BER vs P₁\n(σ₀/μ₀=9%, α=2.5)')

    # 7
    ax = axes[0, 2]
    ax.semilogy(sp7, r7['bs'], 'k-^', label='BER dec', ms=4)
    ax.semilogy(sp7, r7['fs'], 'k--^', label='FER dec', ms=4)
    ax.semilogy(sp7, r7['bh'], 'b-o', label='BER det', ms=4)
    ax.semilogy(sp7, r7['br'], 'r-s', label='BER raw', ms=4)
    ax.set_xlabel('σ₀/μ₀ (%)'); ax.set_ylabel('BER & FER')
    ax.legend(fontsize=7)
    ax.set_title('Fig 7 – vs σ₀/μ₀ (no offset)')

    # 8
    ax = axes[1, 0]
    ax.semilogy(sp8, r8['br'], 'r-^', label='BER raw', ms=4)
    ax.semilogy(sp8, r8['bs'], 'b-s', label='BER dec', ms=4)
    ax.semilogy(sp8, r8['fs'], 'b--s', label='FER dec', ms=4)
    ax.set_xlabel('σ₀/μ₀ (%)'); ax.set_ylabel('BER & FER')
    ax.legend(fontsize=7)
    ax.set_title('Fig 8 – vs σ₀/μ₀ (σofs/μ₁=4%)')

    # 9
    ax = axes[1, 1]
    ax.semilogy(sp8, r9['br'], 'r-^', label='BER raw', ms=4)
    ax.semilogy(sp8, r9['bs'], 'b-s', label='BER dec', ms=4)
    ax.semilogy(sp8, r9['fs'], 'b--s', label='FER dec', ms=4)
    ax.set_xlabel('σ₀/μ₀ (%)'); ax.set_ylabel('BER & FER')
    ax.legend(fontsize=7)
    ax.set_title('Fig 9 – vs σ₀/μ₀ (σofs/μ₁=7%)')

    # 10
    ax = axes[1, 2]
    ax.semilogy(sp8, r8['bs'], 'k-^', label='σofs/μ₁=4%', ms=4)
    ax.semilogy(sp8, r9['bs'], 'b-o', label='σofs/μ₁=7%', ms=4)
    ax.set_xlabel('σ₀/μ₀ (%)'); ax.set_ylabel('BER')
    ax.legend(fontsize=8)
    ax.set_title('Fig 10 – BER offset comparison')

    for ax in axes.flat:
        ax.grid(True, which='both', alpha=0.3)

    plt.tight_layout()
    if save:
        path = os.path.join(OUT_DIR, 'summary_all_figures.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        print(f"  → Saved {path}")
    plt.close()
