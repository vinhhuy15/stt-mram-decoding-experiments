# Rule 06 – From `plans/` to Running Experiment (AI Auto-Workflow)

> When the user drops a new architecture file into `plans/`, the AI agent
> MUST follow this rule end-to-end WITHOUT asking for permission at each step.
> Ask only once at the beginning if anything is critically unclear.

---

## Trigger Condition

This rule activates when **any of the following is true**:

- User says: *"I added a new decoder plan"*, *"implement this"*, *"tôi vừa thêm plan mới"*, etc.
- User pastes content describing a decoder architecture
- A new `.md` file appears in `plans/` that is NOT `baseline_paper.md`

---

## Required Format of a Plan File in `plans/`

When you create a plan file, structure it as follows so the AI can parse it automatically:

```markdown
# Plan: <DecoderName>

## Architecture
[Mô tả thuật toán / kiến trúc giải mã. Ví dụ: dùng Bayesian posterior, neural network, adaptive threshold...]

## Key Idea
[Điểm khác biệt chính so với baseline ML soft decoder]

## Input / Output Contract
- Input : (N, 9) float32 – continuous GMC output  ← MUST match
- Output: (N,) int32 in [0, 127]                  ← MUST match

## Parameters
[Các siêu tham số nếu có, ví dụ: learning_rate, hidden_dim, n_neighbors...]

## Expected Behavior
[Kỳ vọng BER thấp hơn hay ngang baseline? Ở vùng nào? Tại sao?]

## Figures to Compare
[Danh sách figures muốn so sánh: Fig 7 (mặc định), Fig 8, Fig 9, Fig 6...]
```

> If a field is missing, the AI will use default values (see below).

---

## AI Execution Workflow (Step-by-Step)

When the trigger fires, the AI agent MUST execute ALL of the following steps in order:

### Step 0 – Parse the plan file

Read the plan file and extract:
- `decoder_name` ← snake_case from the `# Plan:` heading (e.g., `bayesian_soft`)
- `algorithm_description` ← from `## Architecture` and `## Key Idea`
- `figures_to_compare` ← from `## Figures to Compare` (default: `["fig7"]`)
- `parameters` ← from `## Parameters` (default: none)

**If `## Architecture` is missing or empty → STOP and ask the user.**  
All other missing fields → use defaults silently.

---

### Step 1 – Implement the decoder

**File to edit:** `decoders.py` (append to end) OR create `decoders_<name>.py` if complex

Rules:
- Function signature MUST be: `def <decoder_name>(received: np.ndarray, **ctx) -> np.ndarray`
- Output MUST be `(N,) int32` in `[0, 127]`
- MUST NOT read `uid` (label) — no data leakage
- MUST NOT call `run_channel()` inside the decoder
- MUST NOT modify `received` in-place
- MUST use chunked processing when iterating over the 128-entry codebook (CHUNK=32)
- Include the full docstring template from `rules/04_code_conventions.md`

```python
# Example skeleton the AI MUST follow:
def <decoder_name>(received: np.ndarray, **ctx) -> np.ndarray:
    """
    <DecoderName> – <one-line description from plan>.

    <Key idea vs baseline.>

    Parameters
    ----------
    received : (N, 9) float32 – continuous signal from GMC channel
    **ctx    : {alpha, threshold, mu0, mu1, sig0, sig1_eff}

    Returns
    -------
    (N,) int32 – user-data indices in [0, 127]
    """
    from codebook import CB
    N = received.shape[0]
    # ... implement based on plan ...
    return decoded_idx  # (N,) int32
```

---

### Step 2 – Create the experiment file

**Action:** Copy `experiments/exp_custom_decoder_template.py` → `experiments/exp_<decoder_name>.py`

Then edit exactly 3 locations:

```python
# ① Name
EXPERIMENT_NAME = "<decoder_name>"

# ② Import
from decoders import <decoder_name>        # if added to decoders.py
# from decoders_<name> import <decoder_name>  # if separate file

# ③ Wrapper
def my_decoder(received, **ctx):
    return <decoder_name>(received, **ctx)
```

Do NOT modify any other part of the template.

---

### Step 3 – Quick sanity check

Run:
```bash
python experiments/exp_<decoder_name>.py --quick
```

Expected: no Python errors, no NaN/inf in BER_custom output.

**If the quick run FAILS:**
- Show the full error to the user
- DO NOT proceed to Step 4
- Attempt to fix the bug and re-run Step 3

---

### Step 4 – Report and ask before full run

After the quick run passes, STOP and report:

```
✅ Quick run passed.
   Decoder   : <decoder_name>
   BER_custom (quick, ~10k frames): <value>
   BER_soft   (baseline, same run): <value>

Ready to launch full run (300k frames, ~30–60 min)?
Type "yes" to confirm or specify a different n_frames.
```

**Wait for user confirmation before running full simulation.**

---

### Step 5 – Full run (after user confirms)

```bash
python experiments/exp_<decoder_name>.py
```

When done, report:

```
✅ Full run complete.

Results saved:
  📊 results/custom_<decoder_name>_fig7.npz
  🖼  figures/custom_<decoder_name>_fig7.png

Summary:
  σ/μ=8%    BER_custom=X.Xe-XX   BER_soft=X.Xe-XX   Δ=+/-XX%
  σ/μ=9%    ...
  σ/μ=10%   ...
  ...

Interpretation: [1–2 sentences comparing to baseline]
```

---

## Default Values When Plan Fields Are Missing

| Missing Field | Default |
|---------------|---------|
| `## Figures to Compare` | Fig 7 only (`sigma_ratio` sweep, no offset) |
| `## Parameters` | None (pure algorithmic decoder, no hyperparams) |
| `n_frames` | `300_000` for full run, `10_000` for quick run |
| `alpha` | `2.5` (optimal from paper) |
| `## Expected Behavior` | Skip; AI will not make prior assumption |

---

## What the AI Must NOT Do

```
❌ Modify codebook.py, channel.py, metrics.py, or simulation.py
❌ Overwrite baseline figures (fig5_*.png to fig10_*.png, summary_*.png)
❌ Run the full 300k simulation without user confirmation (Step 4)
❌ Skip the quick run (Step 3) — always sanity-check first
❌ Implement a decoder that reads uid (ground truth labels) inside the function
❌ Create files outside the designated locations (decoders.py / decoders_*.py / experiments/)
```

---

## Example: Minimal Plan File

Save as `plans/bayesian_soft.md`:

```markdown
# Plan: bayesian_soft

## Architecture
Compute posterior P(c | r) for each codeword c using Bayes' theorem with
the GMC likelihood (Gaussian per bit). Pick argmax posterior instead of
argmin Euclidean distance.

## Key Idea
Instead of L2 distance in codeword space, use log-likelihood ratio per bit
weighted by the channel parameters (mu0, mu1, sig0, sig1_eff) from ctx.

## Input / Output Contract
- Input : (N, 9) float32
- Output: (N,) int32 in [0, 127]

## Parameters
None.

## Expected Behavior
Should match or exceed ML soft decoder since it uses the exact channel model.
Expect BER_custom ≤ BER_soft across all sigma ratios.

## Figures to Compare
Fig 7, Fig 8
```

→ Drop this file in `plans/` and tell the AI: **"Implement the plan in plans/bayesian_soft.md"**.  
The AI will execute Steps 0–4 automatically.
