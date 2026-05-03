#!/usr/bin/env python3
"""
Decoders for the 7/9-rate sparse code.

Two decoding strategies from the paper:
  1. ML soft decoder   – Euclidean distance with attenuator α (Eq. 4)
  2. Hard threshold     – conventional (μ₀+μ₁)/2 threshold + nearest codeword

Reference:
  "On the Design of 7/9-Rate Sparse Code for STT-MRAM",
  Chi Dinh Nguyen, IEEE Access 2021.
"""

import numpy as np
from codebook import CB


def soft_decode(received: np.ndarray, alpha: float) -> np.ndarray:
    """
    Maximum-likelihood soft decoding using Euclidean distance (Eq. 4).

    The received signal is attenuated by factor α before computing distances.
    Finds the codeword c* = argmin_c ||recv/α − c||^2.

    Parameters
    ----------
    received : (N, 9) float32
    alpha    : attenuator factor

    Returns
    -------
    best_idx : (N,) int32 – decoded user-data indices
    """
    r = (received / alpha).astype(np.float32)   # (N, 9)
    N = r.shape[0]
    best_idx = np.zeros(N, dtype=np.int32)
    best_d   = np.full(N, np.inf, dtype=np.float32)

    CHUNK = 32   # process 32 codewords at a time → ~3.5 MB per chunk at N=5000
    for start in range(0, 128, CHUNK):
        end  = min(start + CHUNK, 128)
        diff = r[:, None, :] - CB[None, start:end, :]   # (N, chunk, 9)
        d    = np.sum(diff ** 2, axis=2)                 # (N, chunk)
        local_min_idx = np.argmin(d, axis=1)             # (N,)
        local_min_d   = d[np.arange(N), local_min_idx]   # (N,)
        mask = local_min_d < best_d
        best_d[mask]   = local_min_d[mask]
        best_idx[mask] = start + local_min_idx[mask]

    return best_idx


def hard_decode(received: np.ndarray, threshold: float) -> np.ndarray:
    """
    Hard-decision (threshold) detector followed by nearest-codeword look-up.

    Parameters
    ----------
    received  : (N, 9) float32
    threshold : scalar – conventional (mu0+mu1)/2 threshold

    Returns
    -------
    best_idx : (N,) int32 – decoded user-data indices
    """
    hard = (received > threshold).astype(np.float32)   # (N, 9)  → 0/1
    N = hard.shape[0]
    best_idx = np.zeros(N, dtype=np.int32)
    best_d   = np.full(N, np.inf, dtype=np.float32)
    CHUNK = 32
    for start in range(0, 128, CHUNK):
        end  = min(start + CHUNK, 128)
        diff = hard[:, None, :] - CB[None, start:end, :]
        d    = np.sum(diff ** 2, axis=2)
        local_min_idx = np.argmin(d, axis=1)
        local_min_d   = d[np.arange(N), local_min_idx]
        mask = local_min_d < best_d
        best_d[mask]   = local_min_d[mask]
        best_idx[mask] = start + local_min_idx[mask]
    return best_idx
