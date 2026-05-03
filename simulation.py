#!/usr/bin/env python3
"""
Monte-Carlo simulation engine for the 7/9-rate sparse code.

Runs batched simulations comparing:
  - Proposed code with ML soft decoding           (baseline)
  - Proposed code with hard threshold decoding    (baseline)
  - Raw 7-bit data with threshold detection       (no-coding baseline)
  - Any custom decoder passed via `custom_decoder` (your new architecture)
"""

import os
import numpy as np

from codebook import CB
from channel import run_channel
from decoders import soft_decode, hard_decode
from metrics import idx_to_bits, count_errors


def simulate(n_frames: int,
             P1: float,
             sigma_ratio: float,
             alpha: float,
             mu0: float = 1.0,
             mu1: float = 2.0,
             mu_ofs: float = 0.0,
             sig_ofs_ratio: float = 0.0,
             batch: int = 5000,
             custom_decoder=None) -> dict:
    """
    Monte-Carlo BER/FER estimation over n_frames 7-bit user-data frames.

    Parameters
    ----------
    n_frames       : number of 7-bit frames to simulate
    P1             : write error rate 0→1 (dominant)
    sigma_ratio    : σ₀/μ₀ = σ₁/μ₁ (fabrication quality)
    alpha          : attenuator factor for the baseline soft decoder
    mu0, mu1       : mean resistance (kΩ) of low/high state
    mu_ofs         : mean resistance offset (temperature effect)
    sig_ofs_ratio  : σ_ofs / μ₁
    batch          : batch size for vectorised processing
    custom_decoder : optional callable with signature
                     ``fn(received: np.ndarray, **ctx) -> np.ndarray``
                     where ctx contains {alpha, threshold, mu0, mu1, sig0, sig1_eff}.
                     Returns (N,) decoded user-data indices.
                     When provided, results appear under keys BER_custom / FER_custom.

    Returns
    -------
    dict with keys:
        BER_soft,   FER_soft   – baseline ML soft-decoding
        BER_hard,   FER_hard   – baseline hard threshold + nearest CW
        BER_raw,    FER_raw    – raw 7-bit data, no coding (reference)
        BER_custom, FER_custom – your decoder (only present if custom_decoder given)
    """
    P0 = P1 / 100
    Pr = P1 / 100
    sig0     = sigma_ratio * mu0
    sig1     = sigma_ratio * mu1
    sig1_eff = np.sqrt(sig1**2 + (sig_ofs_ratio * mu1)**2)
    threshold = (mu0 + mu1) / 2.0

    # Channel context passed to custom decoder
    ctx = dict(alpha=alpha, threshold=threshold,
               mu0=mu0, mu1=mu1, sig0=sig0, sig1_eff=sig1_eff)

    accum = dict(be_s=0, fe_s=0, be_h=0, fe_h=0,
                 be_r=0, fe_r=0, nb=0, nf=0)
    if custom_decoder is not None:
        accum.update(be_c=0, fe_c=0)

    done = 0
    while done < n_frames:
        B = min(batch, n_frames - done)
        done += B

        # ── Proposed Code ────────────────────────────────────────────────────
        uid = np.random.randint(0, 128, B)
        cw  = CB[uid].astype(np.uint8)
        rx  = run_channel(cw, P1, P0, Pr, mu0, mu1,
                          sig0, sig1_eff, mu_ofs)

        ds = soft_decode(rx, alpha)
        be, fe = count_errors(uid, ds)
        accum['be_s'] += be;  accum['fe_s'] += fe

        dh = hard_decode(rx, threshold)
        be, fe = count_errors(uid, dh)
        accum['be_h'] += be;  accum['fe_h'] += fe

        # ── Custom decoder (your proposed architecture) ───────────────────────
        if custom_decoder is not None:
            dc = custom_decoder(rx, **ctx)
            be, fe = count_errors(uid, dc)
            accum['be_c'] += be;  accum['fe_c'] += fe

        # ── Raw 7-bit data (no coding reference) ─────────────────────────────
        raw  = idx_to_bits(uid)
        rx_r = run_channel(raw, P1, P0, Pr, mu0, mu1,
                           sig0, sig1_eff, mu_ofs)
        det  = (rx_r > threshold).astype(np.uint8)
        accum['be_r'] += int((det != raw).sum())
        accum['fe_r'] += int(np.any(det != raw, axis=1).sum())

        accum['nb'] += B * 7
        accum['nf'] += B

    nb = accum['nb'];  nf = accum['nf']
    result = {
        'BER_soft': accum['be_s'] / nb,
        'FER_soft': accum['fe_s'] / nf,
        'BER_hard': accum['be_h'] / nb,
        'FER_hard': accum['fe_h'] / nf,
        'BER_raw':  accum['be_r'] / nb,
        'FER_raw':  accum['fe_r'] / nf,
    }
    if custom_decoder is not None:
        result['BER_custom'] = accum['be_c'] / nb
        result['FER_custom'] = accum['fe_c'] / nf
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Result persistence helpers
# ─────────────────────────────────────────────────────────────────────────────

def save_results(path: str, **arrays) -> None:
    """
    Save named numpy arrays to a .npz file.

    Usage
    -----
    save_results('results/fig7_baseline.npz',
                 sig_pct=sig_pct, ber_soft=r7['bs'], fer_soft=r7['fs'])
    """
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    np.savez(path, **arrays)
    print(f"  [saved] {path}")


def load_results(path: str) -> dict:
    """
    Load arrays saved by save_results().

    Usage
    -----
    data = load_results('results/fig7_baseline.npz')
    sig_pct  = data['sig_pct']
    ber_soft = data['ber_soft']
    """
    data = np.load(path)
    return {k: data[k] for k in data.files}

