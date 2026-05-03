# Baseline Reproduction – 7/9-Rate Sparse Code for STT-MRAM

**Paper:** "On the Design of 7/9-Rate Sparse Code for Spin-Torque Transfer Magnetic Random Access Memory"  
**Author:** Chi Dinh Nguyen (FPT University, Hanoi) · IEEE Access, Vol. 9, 2021  
**DOI:** [10.1109/ACCESS.2021.3134282](https://doi.org/10.1109/ACCESS.2021.3134282)

---

## Cấu trúc thư mục

```
project_stt_mram/
│
├── config.py                      ← Cấu hình chung (plot style, đường dẫn, constants)
├── codebook.py                    ← Codebook 128 codewords (weight 2 & 4, n=9)
├── channel.py                     ← Kênh cascade: BAC → Z-channel → GMC
├── decoders.py                    ← Decoder baseline: ML soft + Hard threshold
├── metrics.py                     ← Đo lỗi: BER / FER, idx ↔ bits
├── simulation.py                  ← Engine Monte-Carlo + save/load kết quả
│
├── experiments/
│   ├── fig5_attenuator.py         ← BER/FER vs α
│   ├── fig6_ber_vs_p1.py          ← BER vs P₁
│   ├── fig7_sigma_no_offset.py    ← BER/FER vs σ₀/μ₀ (no offset)
│   ├── fig8_offset_4pct.py        ← BER/FER vs σ₀/μ₀ (σ_ofs = 4%)
│   ├── fig9_offset_7pct.py        ← BER/FER vs σ₀/μ₀ (σ_ofs = 7%)
│   ├── fig10_comparison.py        ← So sánh offset 4% vs 7%
│   ├── summary_dashboard.py       ← Dashboard 6 hình trong 1 ảnh
│   └── exp_custom_decoder_template.py  ← Template để test decoder mới ← BẮT ĐẦU TỪ ĐÂY
│
├── results/                       ← Cache kết quả .npz (tự tạo khi chạy)
├── figures/                       ← Ảnh output PNG
│
├── run_all.py                     ← Chạy toàn bộ baseline
├── check_setup.py                 ← Kiểm tra cài đặt
└── stt_mram_sparse_code.py        ← File gốc (backup, không sửa)
```

---

## Yêu cầu

```bash
pip install numpy matplotlib
```

Python >= 3.9.

---

## Cách chạy baseline

### Chạy tất cả 6 figures (300k frames/điểm, ~30–60 phút)
```bash
python run_all.py
```

### Test nhanh để kiểm tra không lỗi (10k frames/điểm, ~2 phút)
```bash
python run_all.py --quick
```

### Chạy từng figure riêng lẻ
```bash
python experiments/fig5_attenuator.py
python experiments/fig7_sigma_no_offset.py
# ... tương tự cho các fig khác
```

### Kiểm tra cài đặt
```bash
python check_setup.py
```

---

## Thêm decoder mới & so sánh với baseline

Đây là workflow chính khi bạn muốn **cải tiến kiến trúc khối giải mã**.

### Tổng quan cơ chế

`simulate()` trong `simulation.py` chấp nhận tham số `custom_decoder=`:

```python
result = simulate(
    n_frames=300_000, P1=2e-4, sigma_ratio=0.09, alpha=2.5,
    custom_decoder=my_decoder_fn,   # ← truyền decoder của bạn vào đây
)
# result sẽ có thêm: result['BER_custom'], result['FER_custom']
# cùng với baseline:  result['BER_soft'], result['BER_hard'], result['BER_raw']
```

Decoder của bạn nhận tín hiệu đầu ra của kênh và trả về user-data index:

```python
def my_decoder(received: np.ndarray, **ctx) -> np.ndarray:
    """
    received : (N, 9) float32  – tín hiệu liên tục từ kênh GMC
    ctx      : dict chứa {alpha, threshold, mu0, mu1, sig0, sig1_eff}

    Trả về : (N,) int32  – user-data index từ 0 đến 127
    """
    ...
```

---

### Bước 1 – Implement decoder mới trong `decoders.py`

Mở `decoders.py` và thêm hàm của bạn vào cuối file. Hai hàm baseline có sẵn để tham khảo cách viết:

```python
# decoders.py  (thêm vào cuối)

def my_new_decoder(received: np.ndarray, **ctx) -> np.ndarray:
    """Decoder kiến trúc mới của tôi."""
    alpha     = ctx['alpha']
    threshold = ctx['threshold']
    mu0       = ctx['mu0']
    mu1       = ctx['mu1']
    sig0      = ctx['sig0']
    sig1_eff  = ctx['sig1_eff']

    # --- Viết logic decoder của bạn ở đây ---
    # Ví dụ: soft_decode đã được sửa đổi
    from codebook import CB
    r = (received / alpha).astype('float32')
    # ... thuật toán của bạn ...
    return decoded_indices   # shape (N,), dtype int32
```

> **Lưu ý:** Chỉ cần implement hàm này. Không cần sửa `simulation.py` hay bất kỳ file engine nào.

---

### Bước 2 – Tạo file experiment riêng

Copy template và đặt tên theo decoder của bạn:

```bash
# Windows
copy experiments\exp_custom_decoder_template.py experiments\exp_my_new_decoder.py

# hoặc PowerShell
Copy-Item experiments\exp_custom_decoder_template.py experiments\exp_my_new_decoder.py
```

Mở file mới, sửa **2 chỗ**:

```python
# ① Đặt tên cho decoder (dùng trong tên file output)
EXPERIMENT_NAME = "my_new_decoder"   # ← sửa tên ở đây

# ② Import và dùng decoder của bạn thay vì placeholder
from decoders import my_new_decoder   # ← import hàm vừa viết

def my_decoder(received, **ctx):       # hàm wrapper gọi vào decoder
    return my_new_decoder(received, **ctx)
```

> File experiment chứa `run()` (chạy simulation + tự cache) và `plot()` (vẽ so sánh).  
> Bạn **không cần sửa** phần còn lại nếu chỉ muốn so sánh trên Fig 7.

---

### Bước 3 – Chạy và xem kết quả

```bash
# Chạy lần đầu (tính toán đầy đủ, mất 30-60 phút với 300k frames)
python experiments/exp_my_new_decoder.py

# Lần sau load từ cache, không tính lại (~1 giây)
python experiments/exp_my_new_decoder.py

# Muốn bắt buộc tính lại (ví dụ sau khi sửa decoder)
python experiments/exp_my_new_decoder.py --rerun
```

Output sẽ bao gồm:
- `results/custom_my_new_decoder_fig7.npz` — dữ liệu số (cache)
- `figures/custom_my_new_decoder_fig7.png` — figure so sánh

**Ví dụ console output:**
```
--- Experiment: my_new_decoder (Fig 7, n=300,000) ---
  σ/μ=8%   baseline=1.2e-04  custom=8.5e-05  raw=5.0e-04
  σ/μ=9%   baseline=3.4e-04  custom=2.1e-04  raw=1.3e-03
  ...
  [saved] results/custom_my_new_decoder_fig7.npz
  → Saved figures/custom_my_new_decoder_fig7.png
```

---

### Ví dụ: So sánh trên nhiều figure

Nếu bạn muốn so sánh trên Fig 8 hoặc Fig 6 thay vì Fig 7, sửa hàm `run()` trong file experiment:

```python
# Thay đổi sig_vals và các tham số simulation trong run()
for sr in sig_vals:
    r = simulate(
        n_frames=n_frames,
        P1=2e-4,
        sigma_ratio=sr,
        alpha=alpha,
        mu_ofs=-0.2,          # ← thêm offset để ra Fig 8
        sig_ofs_ratio=0.04,   # ← thêm offset để ra Fig 8
        batch=5000,
        custom_decoder=my_decoder,
    )
```

---

### Sơ đồ luồng dữ liệu

```
decoders.py          ← Thêm hàm decoder mới ở đây
    │
    ▼
experiments/
exp_my_new_decoder.py  ← Copy từ template, sửa 2 chỗ
    │  (gọi simulate() với custom_decoder=)
    ▼
simulation.py          ← Không cần sửa
    │  (chạy kênh, baseline, custom song song)
    ▼
results/*.npz          ← Cache kết quả số
figures/*.png          ← Figure so sánh
```

---

## Các tham số chính

| Tham số | Ý nghĩa | Giá trị paper |
|---------|---------|--------------|
| `P1` | Xác suất lỗi ghi 0→1 (dominant) | `2e-4` |
| `sigma_ratio` | σ₀/μ₀ = σ₁/μ₁ (chất lượng fabrication) | `0.09` (9%) |
| `alpha` | Hệ số suy giảm cho ML decoder | `2.5` (tối ưu từ Fig 5) |
| `mu0`, `mu1` | Điện trở trung bình (kΩ) | `1.0`, `2.0` |
| `mu_ofs` | Offset điện trở do nhiệt độ (kΩ) | `0.0` hoặc `-0.2` |
| `sig_ofs_ratio` | σ_ofs / μ₁ | `0.0`, `0.04`, `0.07` |
| `n_frames` | Số frame Monte-Carlo | `300_000` |

---

## Kết quả baseline tóm tắt

| Figure | Kết quả chính |
|--------|--------------|
| Fig 5 | α tối ưu = **2.5** (khớp paper) |
| Fig 6 | Error floor raw ≈ 10⁻³; code ≈ 10⁻⁴ |
| Fig 7 | Code cải thiện ~2.2% σ₀/μ₀ so với raw data |
| Fig 8–9 | Code ít nhạy cảm hơn với offset nhiệt độ |
| Fig 10 | σ₀/μ₀ ≥ 5% thì offset 7% bắt đầu ảnh hưởng rõ |

---

## Ghi chú

- File gốc `stt_mram_sparse_code.py` được giữ nguyên làm **backup** — không bao giờ sửa.
- Thư mục `results/` tự tạo khi chạy lần đầu.
- Mỗi lần sửa decoder, nhớ dùng `--rerun` để tính lại cache.
- Tăng `n_frames` lên `2_000_000` để BER ở vùng thấp sát với paper hơn (chậm hơn ~7×).
