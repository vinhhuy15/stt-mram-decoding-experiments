#!/usr/bin/env python3
"""
Cascaded STT-MRAM channel model (Section II of paper).

Three stages:
  1. BAC  (Binary Asymmetric Channel)  – write errors
  2. Z-channel                          – read-disturb errors
  3. GMC  (Gaussian Mixture Channel)    – read-decision noise

Reference:
  "On the Design of 7/9-Rate Sparse Code for STT-MRAM",
  Chi Dinh Nguyen, IEEE Access 2021.
"""

import numpy as np


def run_channel(c: np.ndarray,
                P1: float, P0: float, Pr: float,
                mu0: float, mu1: float,
                sig0: float, sig1_eff: float,
                mu_ofs: float = 0.0,
                write0_direction: bool = True) -> np.ndarray:
    """
    Simulate the cascaded STT-MRAM channel (Fig. 3 in paper).

    Stage 1 – BAC (write error):
        0→1 with prob P0/2,  1→0 with prob P1/2

    Stage 2 – Z channel (read-disturb error):
        write-0 direction: 1→0 with prob Pr   (erroneous 1→0)
        write-1 direction: 0→1 with prob Pr   (erroneous 0→1)

    Stage 3 – GMC (Gaussian mixture read-decision noise):
        state 0 → R ~ N(mu0,  sig0^2)
        state 1 → R ~ N(mu1+mu_ofs, sig1_eff^2)

    Parameters
    ----------
    c               : (N, L) integer array of stored bits
    P1, P0, Pr      : error probabilities as defined in paper
    mu0, mu1        : mean resistance (kΩ) of low/high state
    sig0, sig1_eff  : effective std-dev (kΩ) of low/high state
    mu_ofs          : mean offset of high-resistance (temperature effect)
    write0_direction: True → read current in write-0 direction

    Returns
    -------
    received : (N, L) float32 – continuous analog received signal
    """
    N, L = c.shape
    c = c.astype(np.float32)

    # Stage 1: BAC
    u1 = np.random.rand(N, L).astype(np.float32)
    c_bac = c.copy()
    c_bac[(c == 0) & (u1 < P0 / 2)] = 1.0   # 0→1 write error
    c_bac[(c == 1) & (u1 < P1 / 2)] = 0.0   # 1→0 write error

    # Stage 2: Z channel
    u2 = np.random.rand(N, L).astype(np.float32)
    c_z = c_bac.copy()
    if write0_direction:
        c_z[(c_bac == 1) & (u2 < Pr)] = 0.0   # erroneous 1→0 read-disturb
    else:
        c_z[(c_bac == 0) & (u2 < Pr)] = 1.0   # erroneous 0→1 read-disturb

    # Stage 3: GMC
    n0 = np.random.normal(mu0,           sig0,     (N, L)).astype(np.float32)
    n1 = np.random.normal(mu1 + mu_ofs,  sig1_eff, (N, L)).astype(np.float32)
    received = np.where(c_z == 0, n0, n1)
    return received
