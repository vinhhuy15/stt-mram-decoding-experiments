#!/usr/bin/env python3
"""
Template: Experiment so sánh decoder kiến trúc mới với baseline.

Workflow:
  1. Implement my_decoder() trong decoders.py (hoặc file riêng)
  2. Copy file này, đổi tên thành experiment của bạn (e.g. exp_nn_decoder.py)
  3. Import decoder của bạn và truyền vào tham số custom_decoder=
  4. Kết quả tự động so sánh với baseline trên cùng một figure

Chạy riêng:
    python experiments/exp_custom_decoder_template.py

Kết quả lưu vào:
    results/custom_<tên>.npz  (để dùng lại, không cần chạy lại)
    figures/custom_<tên>_fig7.png
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate, save_results, load_results
from config import OUT_DIR, safe

# ─────────────────────────────────────────────────────────────────────────────
# BƯỚC 1: Định nghĩa decoder của bạn ở đây
# ─────────────────────────────────────────────────────────────────────────────
def my_decoder(received: np.ndarray, **ctx) -> np.ndarray:
    """
    Decoder kiến trúc mới của bạn.

    Parameters
    ----------
    received : (N, 9) float32 – tín hiệu nhận từ kênh
    **ctx    : dict chứa {alpha, threshold, mu0, mu1, sig0, sig1_eff}
               (context của kênh, dùng nếu cần)

    Returns
    -------
    decoded_idx : (N,) int32 – decoded user-data indices (0-127)

    Ví dụ: đây là bản copy của soft_decode (thay bằng code của bạn)
    """
    # ── THAY THẾ PHẦN NÀY BẰNG DECODER CỦA BẠN ──────────────────────────────
    from decoders import soft_decode
    return soft_decode(received, alpha=ctx['alpha'])
    # ─────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# BƯỚC 2: Chạy thí nghiệm (Fig 7 – BER vs σ₀/μ₀, no offset)
# ─────────────────────────────────────────────────────────────────────────────
EXPERIMENT_NAME = "my_decoder"   # ← đặt tên cho decoder của bạn
RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'results', f'custom_{EXPERIMENT_NAME}_fig7.npz'
)


def run(n_frames: int = 300_000, alpha: float = 2.5, force_rerun: bool = False):
    """Chạy simulation hoặc load từ cache nếu đã có."""
    if os.path.exists(RESULTS_FILE) and not force_rerun:
        print(f"  [cache] Loading {RESULTS_FILE}")
        return load_results(RESULTS_FILE)

    sig_vals = np.arange(8, 16) / 100.0
    sig_pct  = sig_vals * 100
    ber_soft, fer_soft = [], []
    ber_hard, fer_hard = [], []
    ber_raw,  fer_raw  = [], []
    ber_cust, fer_cust = [], []

    print(f"\n--- Experiment: {EXPERIMENT_NAME} (Fig 7, n={n_frames:,}) ---")
    for sr in sig_vals:
        r = simulate(
            n_frames=n_frames, P1=2e-4, sigma_ratio=sr,
            alpha=alpha, batch=5000,
            custom_decoder=my_decoder,          # ← truyền decoder của bạn vào đây
        )
        ber_soft.append(safe(r['BER_soft']));  fer_soft.append(safe(r['FER_soft']))
        ber_hard.append(safe(r['BER_hard']));  fer_hard.append(safe(r['FER_hard']))
        ber_raw.append(safe(r['BER_raw']));    fer_raw.append(safe(r['FER_raw']))
        ber_cust.append(safe(r['BER_custom']));fer_cust.append(safe(r['FER_custom']))
        print(f"  σ/μ={sr*100:.0f}%  "
              f"baseline={r['BER_soft']:.2e}  "
              f"custom={r['BER_custom']:.2e}  "
              f"raw={r['BER_raw']:.2e}")

    data = dict(
        sig_pct=np.array(sig_pct),
        ber_soft=np.array(ber_soft), fer_soft=np.array(fer_soft),
        ber_hard=np.array(ber_hard), fer_hard=np.array(fer_hard),
        ber_raw=np.array(ber_raw),   fer_raw=np.array(fer_raw),
        ber_custom=np.array(ber_cust), fer_custom=np.array(fer_cust),
    )
    save_results(RESULTS_FILE, **data)
    return data


# ─────────────────────────────────────────────────────────────────────────────
# BƯỚC 3: Plot so sánh
# ─────────────────────────────────────────────────────────────────────────────
def plot(data: dict, save: bool = True):
    """Vẽ BER/FER của decoder mới chồng lên baseline."""
    sp = data['sig_pct']
    fig, ax = plt.subplots(figsize=(7, 5))

    # Baseline curves (mờ để không lấn át)
    ax.semilogy(sp, data['ber_soft'], 'k-^',  alpha=0.5, lw=1.2, label='Baseline – ML soft')
    ax.semilogy(sp, data['ber_hard'], 'b-o',  alpha=0.5, lw=1.2, label='Baseline – hard det')
    ax.semilogy(sp, data['ber_raw'],  'r-s',  alpha=0.4, lw=1.2, label='Raw (no coding)')

    # Your decoder (nổi bật)
    ax.semilogy(sp, data['ber_custom'], 'g-D', lw=2.2,
                label=f'{EXPERIMENT_NAME} – BER')
    ax.semilogy(sp, data['fer_custom'], 'g--D', lw=1.6,
                label=f'{EXPERIMENT_NAME} – FER')

    ax.set_xlabel('σ₀/μ₀ (%)')
    ax.set_ylabel('BER / FER')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_title(f'Fig 7 – {EXPERIMENT_NAME} vs Baseline\n'
                 '(no offset, P₁=2×10⁻⁴, α=2.5)')
    plt.tight_layout()

    if save:
        path = os.path.join(OUT_DIR, f'custom_{EXPERIMENT_NAME}_fig7.png')
        plt.savefig(path, dpi=150)
        print(f"  → Saved {path}")
    plt.close()


if __name__ == '__main__':
    np.random.seed(42)
    force = '--rerun' in sys.argv
    data  = run(force_rerun=force)
    plot(data)
