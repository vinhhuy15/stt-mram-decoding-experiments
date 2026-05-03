# Rule 05 – Hướng dẫn cho AI Agent

> File này dành riêng cho AI assistant (Gemini, GPT, Claude, v.v.)
> được giao task làm việc trong project này.
> Đọc file này TRƯỚC KHI thực hiện bất kỳ thay đổi nào.

---

## Bước bắt buộc khi bắt đầu session mới

1. Đọc `rules/00_project_invariants.md` — biết cái gì không được đụng
2. Đọc `rules/01_file_ownership.md` — biết file nào được sửa
3. Xác nhận task của user nằm trong phạm vi EXTENSIBLE hoặc YOURS
4. Nếu task yêu cầu sửa FROZEN file → hỏi lại user, không tự ý làm

---

## Phân loại task và cách xử lý

### Task: "Thêm decoder mới"
→ Làm theo `rules/02_adding_decoder.md`
→ Thêm hàm vào `decoders.py` (cuối file) HOẶC tạo `decoders_<name>.py`
→ Tạo `experiments/exp_<name>.py` từ template
→ KHÔNG sửa `simulation.py`, `channel.py`, `codebook.py`, `metrics.py`

### Task: "Sửa channel model / codebook"
→ Hỏi lại user: "Đây là FROZEN file. Bạn có chắc muốn sửa không?"
→ Nếu user xác nhận: tạo bản copy (`channel_v2.py`) thay vì sửa trực tiếp

### Task: "Thêm tham số simulation"
→ Thêm vào `simulate()` với default value giữ backward compatibility
→ Ví dụ đúng: `def simulate(..., new_param=None)` — không break call cũ

### Task: "Vẽ figure so sánh"
→ Lưu vào `figures/custom_<name>_<fig>.png`
→ KHÔNG ghi đè `fig5_*.png` đến `fig10_*.png`

### Task: "Chạy toàn bộ baseline"
→ `python run_all.py --quick` (test) hoặc `python run_all.py` (full)
→ KHÔNG chạy trực tiếp `simulation.py`

---

## Những điều AI agent KHÔNG được tự ý làm

```
❌ Xóa hoặc rename bất kỳ file nào
❌ Sửa logic trong: codebook.py, channel.py, metrics.py, stt_mram_sparse_code.py
❌ Thay đổi signature của simulate() theo cách break backward compat
❌ Thay đổi soft_decode() hoặc hard_decode() trong decoders.py
❌ Ghi đè figure baseline (fig5 đến fig10, summary)
❌ Thay đổi np.random.seed(42) trong run_all.py
❌ Thêm dependency nặng (PyTorch, TF) vào core modules (codebook/channel/metrics)
```

---

## Câu hỏi cần hỏi user trước khi làm

Nếu task không rõ ràng, hỏi:

1. **Decoder mới này dùng thuật toán gì?** (ML, threshold-based, neural net?)
2. **So sánh trên figure nào?** (Fig 7 mặc định, hay Fig 6/8/9?)
3. **n_frames cần bao nhiêu?** (300k mặc định, hay cần nhiều hơn?)
4. **Muốn lưu kết quả không?** (mặc định là có, vào `results/`)

---

## Cấu trúc dữ liệu cần nhớ

```python
# Codebook
CB        # (128, 9) float32 – global singleton trong codebook.py

# Đầu vào decoder
received  # (N, 9) float32 – giá trị điện trở liên tục từ kênh
ctx       # dict: {alpha, threshold, mu0, mu1, sig0, sig1_eff}

# Đầu ra decoder
decoded   # (N,) int32 – index vào CB, phải thuộc [0, 127]

# Kết quả simulate()
{
  'BER_soft':   float,  # baseline ML soft
  'FER_soft':   float,
  'BER_hard':   float,  # baseline hard threshold
  'FER_hard':   float,
  'BER_raw':    float,  # no-coding reference
  'FER_raw':    float,
  'BER_custom': float,  # chỉ có khi truyền custom_decoder=
  'FER_custom': float,
}
```

---

## Luồng kiểm tra nhanh sau khi thay đổi

```bash
python check_setup.py      # kiểm tra import và core features
python run_all.py --quick  # kiểm tra toàn bộ baseline pipeline
```

Nếu một trong hai lệnh trên fail → rollback thay đổi và báo user.
