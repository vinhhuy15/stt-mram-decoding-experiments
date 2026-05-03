# Rule 00 – Project Invariants (KHÔNG ĐƯỢC THAY ĐỔI)

> ⚠️ Đây là danh sách những thứ **bất biến** của project.
> Bất kỳ AI agent hay contributor nào vi phạm những rule này đều có thể
> phá vỡ tính nhất quán của toàn bộ thí nghiệm.

---

## 1. File backup – TUYỆT ĐỐI không sửa, không xóa

```
stt_mram_sparse_code.py
```

File này là **ground truth** của baseline gốc từ paper.
Mọi kết quả so sánh đều phải đối chiếu được với file này.
Nếu có nghi ngờ về output, chạy file này để xác nhận.

---

## 2. Codebook – KHÔNG thay đổi logic xây dựng

File: `codebook.py` · Hàm: `build_codebook()`

Codebook phải thỏa mãn **chính xác**:
- Shape: `(128, 9)`, dtype `float32`
- 36 codewords weight-2: tất cả C(9,2)
- 92 codewords weight-4: **92 codewords đầu tiên theo thứ tự lexicographic** của C(9,4)
- Mapping: user-data index `i` (0–127) ↔ `CB[i]`

> **Tại sao không được đổi?** Encoder và decoder đều dùng index vào CB.
> Thay đổi codebook sẽ làm toàn bộ kết quả BER/FER mất giá trị so sánh.

---

## 3. Channel model – KHÔNG thay đổi pipeline 3 giai đoạn

File: `channel.py` · Hàm: `run_channel()`

Pipeline bất biến:
```
BAC (write error)  →  Z-channel (read disturb)  →  GMC (Gaussian noise)
```

Các tham số chuẩn (45nm technology, từ paper):
```
mu0 = 1.0 kΩ,  mu1 = 2.0 kΩ
P0  = P1 / 100
Pr  = P1 / 100
```

> Không được thay đổi thứ tự giai đoạn, công thức xác suất, hay tham số mặc định.
> Chỉ được truyền khác qua argument – không hardcode giá trị mới.

---

## 4. Metrics – KHÔNG thay đổi cách đếm lỗi

File: `metrics.py`

- **BER**: số bit lỗi / tổng số bit (7 bit/frame)
- **FER**: số frame có ít nhất 1 bit lỗi / tổng số frame
- `idx_to_bits()`: LSB first, 7 bits

> Thay đổi cách đếm lỗi sẽ làm mất khả năng so sánh với paper.

---

## 5. Seed ngẫu nhiên trong `run_all.py`

```python
np.random.seed(42)
```

Seed này đảm bảo reproducibility của baseline chính thức.
**Không thay đổi seed trong `run_all.py`.**
Experiment cá nhân có thể dùng seed khác trong file riêng của mình.

---

## 6. Kết quả baseline đã được xác nhận

Các giá trị sau đã khớp định tính với paper (Chi Dinh Nguyen, 2021):

| Thí nghiệm | Kết quả baseline đã xác nhận |
|-----------|------------------------------|
| Fig 5 | α_opt = 2.5 |
| Fig 7 | BER_soft < BER_raw ở toàn dải σ/μ = 8–15% |
| Fig 8–9 | BER code ít nhạy với offset hơn raw data |

> Kết quả experiment mới của bạn phải so sánh với baseline này, không phải thay thế.
