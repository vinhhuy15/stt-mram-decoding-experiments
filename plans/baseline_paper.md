# 📄 Tóm Tắt Paper: 7/9-Rate Sparse Code for STT-MRAM

> **Tiêu đề đầy đủ:** On the Design of 7/9-Rate Sparse Code for Spin-Torque Transfer Magnetic Random Access Memory  
> **Tác giả:** Chi Dinh Nguyen (FPT University, Hanoi, Vietnam)  
> **Tạp chí:** IEEE Access, Vol. 9, pp. 164562–164569, 2021  
> **DOI:** [10.1109/ACCESS.2021.3134282](https://doi.org/10.1109/ACCESS.2021.3134282)  
> **Tài trợ:** NAFOSTED, grant 102.04-2019.307

---

## 1. Bối Cảnh & Động Lực Nghiên Cứu

### 1.1 STT-MRAM là gì?
**Spin-Torque Transfer Magnetic Random Access Memory (STT-MRAM)** là công nghệ bộ nhớ không bay hơi (nonvolatile) thế hệ mới. Cấu tạo cơ bản gồm hai thành phần:

- **MTJ (Magnetic Tunnel Junction):** phần tử lưu trữ dữ liệu, gồm hai lớp sắt từ và một lớp oxide mỏng ở giữa.
  - **Parallel (P):** hai lớp từ hóa cùng chiều → **Low Resistance State (LRS)** → bit logic `0`
  - **Antiparallel (AP):** hai lớp từ hóa ngược chiều → **High Resistance State (HRS)** → bit logic `1`
- **nMOS transistor:** phần tử điều khiển truy cập (cấu trúc **1T1J**: one-transistor, one-MTJ)

### 1.2 Ưu điểm của STT-MRAM
- Không bay hơi (nonvolatile)
- Tốc độ đọc/ghi nanosecond, độ trễ thấp
- Độ bền (endurance) cao
- Tiêu thụ điện thấp hơn Flash
- Kỳ vọng thay thế cả SRAM (cache) và DRAM (main memory)

### 1.3 Thách thức kỹ thuật chính
| Vấn đề | Nguyên nhân | Hệ quả |
|--------|-------------|--------|
| **Process variations** | Biến động hình học và điện trở MTJ | Sai lệch ngưỡng dòng switching |
| **Thermal fluctuation** | Nhiệt độ làm MTJ tự switching | Write error ngẫu nhiên |
| **Read disturb** | Dòng đọc đủ lớn để gây switching nhầm | Mất dữ liệu khi đọc |
| **Asymmetric write error** | Dòng ghi `1` (0→1) cần lớn hơn dòng ghi `0` (1→0) | **P(0→1 fail) >> P(1→0 fail)** |

### 1.4 Tại sao cần sparse code?
> **Quan sát then chốt:** Xác suất lỗi ghi `0→1` (tức ghi bit `1`) **cao hơn nhiều** so với `1→0`.  
> → Nếu giảm số lượng bit `1` trong dữ liệu ghi, ta giảm được write failure rate.

Các mã ECC truyền thống (Hamming, BCH) không khai thác được tính bất đối xứng này. Sparse code là giải pháp phù hợp vì nó **kiểm soát trực tiếp số lượng bit `1`** trong codeword.

---

## 2. Channel Model cho STT-MRAM

### 2.1 Cascaded Channel Model (Section II)
Paper áp dụng mô hình kênh tầng (cascaded) gồm 3 giai đoạn nối tiếp:

```
Bit gốc c → [BAC] → [Z-channel] → [GMC] → Tín hiệu nhận r
              ↑           ↑            ↑
          Write error  Read disturb  Read decision
```

#### Giai đoạn 1: BAC – Binary Asymmetric Channel (Write Error)
- `0 → 1` với xác suất `P₀/2`  
- `1 → 0` với xác suất `P₁/2`  
- **Quan trọng:** P₁ >> P₀ (P₀ và Pᵣ thường nhỏ hơn P₁ khoảng 2 bậc độ lớn)

#### Giai đoạn 2: Z-channel (Read Disturb Error)
- Phụ thuộc hướng dòng đọc:
  - **Write-0 direction:** `1 → 0` với xác suất `Pᵣ`
  - **Write-1 direction:** `0 → 1` với xác suất `Pᵣ`

#### Giai đoạn 3: GMC – Gaussian Mixture Channel (Read Decision Error)
- Trạng thái `0`: điện trở R₀ ~ **N(μ₀, σ₀²)**
- Trạng thái `1`: điện trở R₁ ~ **N(μ₁ + μ_ofs, σ₁² + σ_ofs²)**
- Tham số chuẩn (công nghệ 45nm): μ₀ = 1 kΩ, μ₁ = 2 kΩ

### 2.2 Crossover Probabilities sau khi kết hợp BAC + Z-channel

**Hướng write-0:**
```
p₀ = (P₀/2)(1−Pᵣ)             q₀ = (1−P₀/2) + (P₀/2)Pᵣ
p₁ = P₁/2 + (1−P₁/2)Pᵣ       q₁ = (1−P₁/2)(1−Pᵣ)
```

**Hướng write-1:**
```
p₀ = P₀/2 + (1−P₀/2)Pᵣ       q₀ = (1−P₀/2)(1−Pᵣ)
p₁ = P₁/2 + (1−Pᵣ)            q₁ = (1−P₁/2) + (P₁/2)Pᵣ
```

---

## 3. Thiết Kế Sparse Code 7/9-Rate

### 3.1 Ý tưởng cốt lõi
Mã hóa **7-bit user data** thành **9-bit codeword** sao cho Hamming weight của codeword **luôn nhỏ hơn n/2 = 4.5**, tức là ≤ 4.  
→ Số bit `1` luôn thiểu số → Giảm số lần ghi `0→1` → Giảm write failure rate.

### 3.2 Xây dựng Codebook

**Tổng số sequence 9-bit có weight ≤ 4:**
```
S = C(9,0) + C(9,1) + C(9,2) + C(9,3) + C(9,4)
  =    1   +    9   +   36   +   84   +  126   = 256 sequences
```
→ 256 sequences đủ để xây mã 8/9-rate, nhưng Hamming distance = 1 (quá thấp).

**Chiến lược chọn 128 codewords cho 7/9-rate:**
- **36 codewords weight-2:** tất cả C(9,2) = 36 tổ hợp
- **92 codewords weight-4:** chọn 92 trong C(9,4) = 126 tổ hợp

→ Codebook S_w có **128 codewords**, Hamming distance tối thiểu = **2** (tốt hơn 8/9-rate).

### 3.3 Encoder
- Sử dụng **Look-Up Table (LUT) kích thước 128 = 2⁷**
- Ánh xạ 1:1: chuỗi 7-bit `0000000`…`1111111` → codeword c₀…c₁₂₇
- **Độ phức tạp:** O(1) — tra bảng đơn giản

### 3.4 Decoder (Maximum Likelihood)
Decoder tìm codeword có **khoảng cách Euclidean nhỏ nhất** đến tín hiệu nhận:

```
d(rᵢ, cᵢ) = sqrt( Σⱼ₌₁⁹ (rᵢⱼ − cᵢⱼ)² )
```

**Điểm quan trọng:** Tín hiệu nhận `r` được đưa thẳng vào decoder *không qua thresholding*, sau đó được **nhân với hệ số suy giảm 1/α** trước khi tính khoảng cách.

### 3.5 Hệ số suy giảm α (Attenuator)
- α là tham số cần chỉnh (tunable hyperparameter)
- Giá trị tối ưu: **α = 2.5** (được xác định bằng simulation)
- α quá nhỏ hoặc quá lớn đều làm BER tăng mạnh
- Ý nghĩa: cân bằng giữa thông tin kênh nhận được và ảnh hưởng của nhiễu đến quá trình tính khoảng cách

---

## 4. Kết Quả Mô Phỏng

### 4.1 Cấu hình mô phỏng
- Công nghệ tham chiếu: **45nm**
- μ₀ = 1 kΩ, μ₁ = 2 kΩ, σ₀/μ₀ = σ₁/μ₁
- P₀ = Pᵣ = P₁/100 (hai bậc độ lớn nhỏ hơn P₁)
- α = 2.5 (cố định cho các thí nghiệm sau khi tối ưu)

### 4.2 Fig 5 – BER/FER vs Attenuator α
- P₁ = 2×10⁻⁴, σ₀/μ₀ = 10%
- **Kết luận:** α = 2.5 cho BER thấp nhất; ngoài khoảng [2.5, 3.0] hiệu năng suy giảm mạnh

### 4.3 Fig 6 – BER vs Write Error Rate P₁ (σ₀/μ₀ = 9%)
| Chỉ số | Raw data | Proposed code |
|--------|----------|---------------|
| Error floor | ~10⁻³ BER | ~10⁻⁵ BER |
| Ngưỡng P₁ bão hòa | P₁ ≤ 10⁻⁴ | P₁ ≤ 10⁻⁵ |
| BER tại P₁=10⁻⁴ | 1.3×10⁻³ | 1.5×10⁻⁴ |

**Kết luận:** Code giảm error floor **2 bậc độ lớn** so với raw data.

### 4.4 Fig 7 – BER/FER vs σ₀/μ₀ (Không offset, P₁ = 2×10⁻⁴)
- Code cải thiện khoảng **2.2% σ₀/μ₀** so với raw data ở mức BER = 10⁻³
- Khi σ₀/μ₀ ≈ 15%: decoder và detector có xu hướng hội tụ (code gain giảm)
- ML decoder luôn tốt hơn hard-threshold detector

### 4.5 Fig 8 & 9 – Ảnh hưởng của Offset Điện Trở (μ_ofs = −0.2 kΩ)
Offset xảy ra khi nhiệt độ tăng làm dịch chuyển phân phối R₁:

| Điều kiện | σ_ofs/μ₁ = 4% | σ_ofs/μ₁ = 7% |
|-----------|---------------|---------------|
| σ₀/μ₀ từ 2% đến 7% | Code: BER ~10⁻⁴ (flat) | Code: BER ~10⁻⁴ (flat) |
| σ₀/μ₀ từ 2% đến 7% | Raw: 10⁻⁴ → 10⁻² | Raw: 10⁻² → 3.5×10⁻² |

**Kết luận:** Code **ít nhạy cảm với offset** hơn rõ rệt so với raw data.

### 4.6 Fig 10 – So sánh BER tại 2 mức offset
- Khi σ₀/μ₀ < 5%: BER ở 4% và 7% offset gần như không khác nhau
- Khi σ₀/μ₀ ≥ 5%: offset 7% bắt đầu gây suy giảm hiệu năng rõ rệt

---

## 5. So Sánh với Các Phương Pháp Khác

| Phương pháp | Code rate | Hamming distance | Khai thác asymmetry |
|-------------|-----------|-----------------|---------------------|
| 64/71 Regular Hamming | ~0.901 | 3 | ✗ |
| 64/72 Extended Hamming | ~0.889 | 4 | ✗ |
| **7/9 Sparse Code (paper này)** | **0.778** | **2** | **✓** |
| 8/9 Sparse Code (baseline) | 0.889 | 1 | ✓ |

> Lưu ý: Code rate 7/9 ≈ 0.778 thấp hơn Hamming nhưng khai thác được đặc tính bất đối xứng mà ECC truyền thống bỏ qua, đặc biệt hiệu quả trong vùng write error cao.

---

## 6. Hạn Chế & Hướng Phát Triển

### Hạn chế
- **Không có khả năng sửa lỗi (error correction):** chỉ là constrained code, không phải ECC
- Error floor còn cao (~10⁻⁵) ở vùng write error rate thấp hơn 10⁻⁵
- Code rate 7/9 thấp hơn Hamming code → overhead lớn hơn
- Chưa phân tích chi tiết về energy, area, timing của mạch thực tế

### Hướng phát triển đề xuất
- **Error-correction sparse code:** kết hợp sparse constraint với ECC để vừa giảm write error vừa sửa được read error
- Áp dụng machine learning / neural network cho threshold detection (đã có sơ bộ ở [23])
- Thiết kế mã sparse 2D cho crossbar resistive memory arrays

---

## 7. Các Khái Niệm Quan Trọng Cần Nhớ

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| **STT-MRAM** | Bộ nhớ từ dùng spin-polarized current để ghi; nonvolatile |
| **MTJ** | Magnetic Tunnel Junction – phần tử lưu trữ cơ bản |
| **LRS / HRS** | Low/High Resistance State – tương ứng bit 0 / bit 1 |
| **Sparse code** | Constrained code đảm bảo số bit `1` luôn < n/2 |
| **Hamming weight** | Số lượng bit `1` trong một codeword |
| **BAC** | Binary Asymmetric Channel – mô hình lỗi ghi bất đối xứng |
| **Z-channel** | Mô hình read disturb (chỉ lỗi theo một chiều) |
| **GMC** | Gaussian Mixture Channel – mô hình nhiễu đọc |
| **Attenuator α** | Hệ số chia tín hiệu nhận trước khi ML decode; tối ưu = 2.5 |
| **Error floor** | Mức BER tối thiểu khi write error rate → 0 (do read error) |
| **P₁** | Xác suất lỗi ghi 0→1 (dominant error, P₁ >> P₀) |
| **σ₀/μ₀** | Độ phân tán tương đối của điện trở – đo chất lượng fabrication |

---

## 8. Quick Reference cho Agent/User

### Muốn reproduce kết quả?
→ Chạy `python stt_mram_sparse_code.py` (xem project đi kèm)

### Muốn thay đổi tham số?
```python
# Các tham số chính trong hàm simulate():
P1           = 2e-4    # write error rate 0→1 (dominant)
sigma_ratio  = 0.09    # σ₀/μ₀ = σ₁/μ₁ (fabrication quality)
alpha        = 2.5     # attenuator (optimal, từ Fig 5)
mu_ofs       = -0.2    # offset điện trở (kΩ), do nhiệt độ
sig_ofs_ratio= 0.04    # σofs/μ₁ (4% hoặc 7% theo paper)
n_frames     = 300_000 # tăng lên 2_000_000 để BER sát paper hơn
```

### Codebook hoạt động thế nào?
```
User data (7-bit) → [LUT 128 entries] → Codeword (9-bit, weight ∈ {2, 4})
                                                ↓
                                     Ghi vào STT-MRAM
                                                ↓
                              [Cascaded Channel: BAC → Z → GMC]
                                                ↓
                           Tín hiệu nhận r (continuous, analog)
                                                ↓
                          [ML Decoder: argmin ||r/α − c||²]
                                                ↓
                                  User data khôi phục (7-bit)
```

---

## 9. Tài Liệu Tham Khảo Chính

| Ref | Nội dung |
|-----|---------|
| [16] Cai & Immink (2017) | Cascaded channel model gốc cho STT-MRAM – **nền tảng của paper này** |
| [17] Wen et al. (2013) | CD-ECC – content-dependent ECC cho asymmetric NVM |
| [18] Azad et al. (2019) | AWARE – adaptive ECC cho write errors trong STT-RAM |
| [12] Nguyen et al. (2021) | 2D weight-constrained codes cho crossbar ReRAM |
| [15] Everspin MR4A16B | Chip STT-MRAM thương mại với 64/71-rate Hamming code |
| [23] Mei et al. (2019) | Neural network-based dynamic threshold cho NVM |

---

*Tài liệu này được tạo để cung cấp ngữ cảnh đầy đủ cho bất kỳ agent hoặc user nào muốn hiểu, tái hiện, hoặc mở rộng nghiên cứu trong paper trên.*