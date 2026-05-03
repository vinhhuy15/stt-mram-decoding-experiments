# Rule 02 – Quy trình thêm decoder mới

## Tổng quan

Decoder mới KHÔNG được thay thế baseline. Nó chạy **song song** với baseline
trong cùng một simulation và kết quả được so sánh trực tiếp.

```
Cùng 1 batch dữ liệu → chạy cả baseline lẫn decoder mới → so sánh BER/FER
```

---

## Bước 1: Implement decoder

### Option A – Decoder đơn giản (thêm vào `decoders.py`)

Mở `decoders.py`, thêm hàm vào **cuối file**:

```python
def my_decoder_name(received: np.ndarray, **ctx) -> np.ndarray:
    """
    [Mô tả ngắn kiến trúc]

    Parameters
    ----------
    received : (N, 9) float32 – tín hiệu liên tục ra từ kênh GMC
    **ctx    : dict – channel context gồm:
                  alpha      : float  – attenuator factor
                  threshold  : float  – (mu0 + mu1) / 2
                  mu0, mu1   : float  – mean resistance (kΩ)
                  sig0       : float  – std-dev low state
                  sig1_eff   : float  – effective std-dev high state

    Returns
    -------
    decoded_idx : (N,) int32 – user-data indices trong [0, 127]
    """
    # ... implement ...
    return decoded_idx
```

### Option B – Decoder phức tạp (tạo file riêng)

Tạo file `decoders_<tên>.py` ở root project (cạnh `decoders.py`):

```python
# decoders_myname.py
import numpy as np
# import torch, etc.

def my_decoder_name(received: np.ndarray, **ctx) -> np.ndarray:
    ...
```

---

## Bước 2: Tạo file experiment

Copy template:
```bash
copy experiments\exp_custom_decoder_template.py experiments\exp_<tên>.py
```

Sửa **đúng 3 chỗ** trong file mới:

```python
# ① Tên (dùng cho tên file output)
EXPERIMENT_NAME = "<tên>"   # không có dấu cách, dùng underscore

# ② Import decoder
from decoders import my_decoder_name          # Option A
# from decoders_myname import my_decoder_name # Option B

# ③ Gọi trong wrapper
def my_decoder(received, **ctx):
    return my_decoder_name(received, **ctx)
```

---

## Bước 3: Chạy

```bash
# Lần đầu – tính toán đầy đủ
python experiments\exp_<tên>.py

# Sau khi sửa decoder – bắt buộc rerun
python experiments\exp_<tên>.py --rerun

# Lần sau nếu không sửa gì – load cache nhanh
python experiments\exp_<tên>.py
```

---

## Bước 4: Kiểm tra output

Sau khi chạy xong, kiểm tra:

```
✅ results/custom_<tên>_fig7.npz  – có tồn tại
✅ figures/custom_<tên>_fig7.png  – BER_custom ≤ BER_soft (nếu tốt hơn baseline)
✅ Console không có NaN hay inf trong BER_custom
```

---

## Quy tắc bắt buộc khi implement decoder

| Rule | Lý do |
|------|-------|
| Output phải là `(N,) int32` trong `[0, 127]` | Codebook có 128 entries |
| Không được đọc `uid` (label) bên trong decoder | Đó là data leakage |
| Không được gọi `run_channel()` bên trong decoder | Channel chỉ chạy 1 lần trong engine |
| Không được sửa `received` in-place | Baseline cũng dùng array đó |
| Phải handle batch size N tùy ý | Engine truyền batch=5000 mặc định |

---

## Ví dụ: Adaptive threshold decoder

```python
# decoders.py – thêm vào cuối

def adaptive_threshold_decode(received: np.ndarray, **ctx) -> np.ndarray:
    """
    Decoder dùng ngưỡng thích nghi theo từng cột thay vì ngưỡng cố định.
    """
    from codebook import CB

    # Tính ngưỡng adaptive per-column (mean của mỗi cột)
    col_thresh = received.mean(axis=0, keepdims=True)  # (1, 9)
    hard = (received > col_thresh).astype(np.float32)  # (N, 9)

    N = hard.shape[0]
    best_idx = np.zeros(N, dtype=np.int32)
    best_d   = np.full(N, np.inf, dtype=np.float32)
    for start in range(0, 128, 32):
        end  = min(start + 32, 128)
        diff = hard[:, None, :] - CB[None, start:end, :]
        d    = np.sum(diff ** 2, axis=2)
        local_min = np.argmin(d, axis=1)
        local_d   = d[np.arange(N), local_min]
        mask = local_d < best_d
        best_d[mask]   = local_d[mask]
        best_idx[mask] = start + local_min[mask]
    return best_idx
```
