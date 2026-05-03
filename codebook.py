#!/usr/bin/env python3
"""
Codebook construction for the 7/9-rate sparse code.

128 codewords of length n=9:
  - 36 codewords of Hamming weight 2  (all C(9,2) = 36)
  - 92 codewords of Hamming weight 4  (first 92 of C(9,4) = 126, lex order)

Reference: Section III of
  "On the Design of 7/9-Rate Sparse Code for STT-MRAM",
  Chi Dinh Nguyen, IEEE Access 2021.
"""

import numpy as np
from itertools import combinations


def build_codebook() -> np.ndarray:
    """
    Build and return the (128, 9) binary codebook.

    Returns
    -------
    CB : np.ndarray, shape (128, 9), dtype float32
        Each row is a codeword; user-data index i maps to row i.
    """
    n = 9
    cws = []

    # Weight-2 (all 36)
    for pos in combinations(range(n), 2):
        cw = np.zeros(n, dtype=np.uint8)
        cw[list(pos)] = 1
        cws.append(cw)

    # Weight-4 (first 92 in lexicographic order)
    cnt = 0
    for pos in combinations(range(n), 4):
        if cnt >= 92:
            break
        cw = np.zeros(n, dtype=np.uint8)
        cw[list(pos)] = 1
        cws.append(cw)
        cnt += 1

    CB = np.array(cws, dtype=np.float32)
    assert CB.shape == (128, 9), "Codebook must be (128, 9)"
    weights = CB.sum(axis=1).astype(int)
    assert set(weights.tolist()) == {2, 4}, "Weights must be 2 or 4"
    return CB


# ── Module-level singleton ────────────────────────────────────────────────────
# Imported once and shared across all modules that need the codebook.
CB = build_codebook()
