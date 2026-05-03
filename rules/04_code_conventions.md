# Rule 04 – Code Conventions

## Naming

### Files
```
decoders.py              ← baseline (không đổi tên)
decoders_<theme>.py      ← decoder mới theo nhóm (vd: decoders_neural.py)
exp_<name>.py            ← experiment script (trong experiments/)
```

### Decoder functions
```python
soft_decode()                    ← baseline (đặt sẵn, KHÔNG sửa)
hard_decode()                    ← baseline (đặt sẵn, KHÔNG sửa)
adaptive_threshold_decode()      ← ví dụ decoder mới
```

### Variables chuẩn trong decoder
```python
N        # batch size
received # (N, 9) float32 – input
best_idx # (N,)   int32   – output
best_d   # (N,)   float32 – distance tracker
CHUNK    # int    – chunk size để tránh OOM
```

---

## Docstring bắt buộc cho decoder mới

```python
def my_decoder(received: np.ndarray, **ctx) -> np.ndarray:
    """
    [Tên] – [Mô tả 1 dòng].

    [Ý tưởng chính, điểm khác với baseline]

    Parameters
    ----------
    received : (N, 9) float32 – tín hiệu từ kênh GMC
    **ctx    : {alpha, threshold, mu0, mu1, sig0, sig1_eff}

    Returns
    -------
    (N,) int32 – user-data indices trong [0, 127]
    """
```

---

## Chunked processing – bắt buộc khi duyệt toàn codebook

```python
# ĐÚNG – chunk 32, RAM-safe
CHUNK = 32
for start in range(0, 128, CHUNK):
    end  = min(start + CHUNK, 128)
    diff = r[:, None, :] - CB[None, start:end, :]  # (N, CHUNK, 9)
    ...

# SAI – tạo (N, 128, 9) nguyên khối → OOM tại N=5000
diff = r[:, None, :] - CB[None, :, :]
```

---

## EXPERIMENT_NAME – quy tắc đặt tên

```python
EXPERIMENT_NAME = "adaptive_threshold"   # ✅ lowercase, underscore
EXPERIMENT_NAME = "Adaptive Threshold"   # ❌ dấu cách
EXPERIMENT_NAME = "exp1"                 # ❌ không mô tả
```

---

## Import order trong experiment files

```python
import sys, os
sys.path.insert(0, ...)        # 1. path setup

import numpy as np             # 2. third-party
import matplotlib.pyplot as plt

from simulation import simulate # 3. project core
from config import OUT_DIR, safe

from decoders import my_fn      # 4. decoder của bạn (cuối)
```

---

## Quy tắc cứng cho decoder

| Rule | Lý do |
|------|-------|
| Output `(N,) int32` trong `[0,127]` | Codebook có 128 entries |
| Không đọc `uid` (label) bên trong | Data leakage |
| Không gọi `run_channel()` bên trong | Channel chỉ chạy 1 lần |
| Không sửa `received` in-place | Baseline cùng dùng array đó |
| Xử lý được N bất kỳ | Engine dùng batch=5000 |
