# Rule 01 – File Ownership (Ai được sửa file nào)

## Phân loại: FROZEN / STABLE / EXTENSIBLE / YOURS

### 🔒 FROZEN – Tuyệt đối không sửa

| File | Lý do |
|------|-------|
| `stt_mram_sparse_code.py` | Backup gốc, ground truth |
| `codebook.py` | Logic xây codebook là bất biến |
| `channel.py` | Channel model cố định theo paper |
| `metrics.py` | Công thức BER/FER cố định |

> Nếu cần sửa FROZEN file, phải có lý do rất mạnh và thảo luận với người dùng trước.

---

### 🟡 STABLE – Chỉ sửa khi có lý do rõ ràng

| File | Được sửa khi nào |
|------|----------------|
| `simulation.py` | Thêm tính năng engine (không xóa API cũ) |
| `config.py` | Thêm tham số mới, thay đổi plot style |
| `run_all.py` | Thêm experiment mới vào pipeline chạy all |
| `experiments/fig5_*.py` đến `fig10_*.py` | Chỉnh sửa plot (label, màu, title) |
| `experiments/summary_dashboard.py` | Thêm subplot mới |

> Khi sửa STABLE file: **không xóa behavior cũ**, chỉ mở rộng.
> Ví dụ: `simulate()` được thêm `custom_decoder=None` nhưng vẫn chạy đúng khi không truyền.

---

### 🟢 EXTENSIBLE – Được thêm code, không sửa code cũ

| File | Cách mở rộng |
|------|-------------|
| `decoders.py` | **Thêm hàm mới vào cuối**. Không sửa `soft_decode()`, `hard_decode()` |

> Hai hàm `soft_decode()` và `hard_decode()` là **baseline reference**.
> Decoder mới của bạn phải là hàm riêng, không override.

---

### 🆕 YOURS – Tạo mới tự do

| Vị trí | Mục đích |
|--------|---------|
| `experiments/exp_*.py` | Experiment của bạn (copy từ template) |
| `decoders_*.py` (root) | Decoder phức tạp cần file riêng |
| `results/*.npz` | Cache kết quả (tự tạo/xóa thoải mái) |
| `figures/custom_*.png` | Figure output của experiment bạn |
| `rules/*.md` | Thêm rule mới nếu cần |

---

## Tóm tắt nhanh

```
Muốn thêm decoder mới?     → Thêm hàm vào decoders.py (cuối file)
                               hoặc tạo decoders_myname.py
Muốn chạy thí nghiệm?      → Tạo experiments/exp_myname.py
Muốn sửa channel model?    → KHÔNG (frozen)
Muốn sửa codebook?         → KHÔNG (frozen)
Muốn thay đổi BER formula? → KHÔNG (frozen)
Muốn thêm tham số config?  → config.py (stable, thêm vào cuối)
```
