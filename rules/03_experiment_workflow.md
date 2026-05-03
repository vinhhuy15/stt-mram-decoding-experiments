# Rule 03 – Quy trình thí nghiệm chuẩn

## Nguyên tắc cốt lõi

> **Một thí nghiệm = Một file.**
> Không nhét nhiều thí nghiệm khác nhau vào cùng một script.

---

## Vòng đời của một thí nghiệm

```
1. Viết decoder mới
        ↓
2. Tạo file exp_*.py (copy từ template)
        ↓
3. Chạy --quick trước để kiểm tra không lỗi
        ↓
4. Chạy full (300k frames)
        ↓
5. Kết quả tự động cache vào results/*.npz
        ↓
6. Figure tự động lưu vào figures/custom_*.png
        ↓
7. So sánh với baseline
```

---

## Quy tắc chạy thí nghiệm

### Trước khi chạy full run

Luôn kiểm tra nhanh trước:
```bash
python run_all.py --quick          # test toàn bộ baseline (~2 phút)
python experiments\exp_mine.py     # nếu có cache thì chạy ngay
```

### Khi sửa decoder và muốn chạy lại

```bash
python experiments\exp_mine.py --rerun
```

Không dùng `--rerun` khi không có thay đổi — tốn thời gian không cần thiết.

### Không chạy trực tiếp trong `simulation.py`

`simulation.py` là engine, không phải script chạy trực tiếp.
Mọi thí nghiệm phải đi qua file trong `experiments/`.

---

## Quản lý kết quả

### Cache `.npz` trong `results/`

```
results/
├── custom_my_decoder_fig7.npz      ← kết quả của bạn
├── custom_my_decoder_fig8.npz
└── ...
```

**Không commit file `.npz` lên git** (nếu dùng git) — chúng tự tạo lại được.
Thêm vào `.gitignore`:
```
results/*.npz
```

### Figure trong `figures/`

```
figures/
├── fig5_attenuator.png             ← baseline (đừng ghi đè)
├── fig6_ber_vs_P1.png              ← baseline
├── ...
├── custom_my_decoder_fig7.png      ← của bạn (prefix "custom_")
└── summary_all_figures.png         ← baseline dashboard
```

**Rule:** Output của experiment bạn phải có prefix `custom_` trong tên file.
Không được ghi đè `fig5_*.png` đến `fig10_*.png` và `summary_*.png`.

---

## Thứ tự ưu tiên khi debug BER bất thường

1. **BER_custom = BER_soft**: Decoder của bạn chưa khác gì baseline → kiểm tra lại logic
2. **BER_custom = NaN**: Có phép chia cho 0 → kiểm tra output shape
3. **BER_custom = 1.0**: Tất cả decode sai → output index sai range hoặc sai dtype
4. **BER_custom > BER_raw**: Decoder tệ hơn không coding → kiểm tra lại thuật toán

---

## N_frames tối thiểu theo vùng BER cần đo

| BER target | n_frames tối thiểu | Lý do |
|-----------|-------------------|-------|
| ~10⁻³ | 100_000 | Cần ≥100 lỗi để ổn định |
| ~10⁻⁴ | 1_000_000 | Cần ≥100 lỗi |
| ~10⁻⁵ | 10_000_000 | Rất chậm, cân nhắc importance sampling |

> Default 300_000 frame đủ cho vùng BER ≥ 10⁻⁴. Tăng `n_frames` nếu muốn đo vùng thấp hơn.
