#!/usr/bin/env python3
"""
Error-counting utilities for BER / FER measurement.

Converts 7-bit user-data indices to binary and counts
bit errors (BER) and frame errors (FER).
"""

import numpy as np

_SHIFTS = np.arange(7, dtype=np.int32)   # bit positions 0-6


def idx_to_bits(idx: np.ndarray) -> np.ndarray:
    """
    Convert user-data indices to binary representation.

    Parameters
    ----------
    idx : (N,) int array – values in [0, 127]

    Returns
    -------
    bits : (N, 7) int array – LSB first
    """
    return (idx[:, None] >> _SHIFTS[None, :]) & 1


def count_errors(true_idx: np.ndarray, pred_idx: np.ndarray):
    """
    Count bit errors and frame errors between true and predicted indices.

    Parameters
    ----------
    true_idx : (N,) int array
    pred_idx : (N,) int array

    Returns
    -------
    bit_errors   : int – total number of bit mismatches across all frames
    frame_errors : int – number of frames with at least one bit error
    """
    fe = int((true_idx != pred_idx).sum())
    be = int((idx_to_bits(true_idx) != idx_to_bits(pred_idx)).sum())
    return be, fe
