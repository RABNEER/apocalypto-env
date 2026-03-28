# 🏆 Apocalypto-Env

**Meta × Hugging Face OpenEnv Hackathon India | Round 1 Submission**

**Problem Statement**: Build a complete, real-world OpenEnv environment for training agentic AI agents (as per Round 1 guidelines)

**Chosen Domain**: Adversarial Social Engineering and Fraud Detection  
(focused on financial scam detection in India's UPI ecosystem)

An RL environment that trains AI agents to classify, extract artifacts from, and safely engage with simulated Indian financial scammers — addressing India's ₹11,000 Crore digital fraud epidemic.

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-blue)](https://github.com/meta-pytorch/OpenEnv)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)

---

## 🎯 Motivation

India's digital payments ecosystem processes over 13 billion UPI transactions monthly. Alongside this growth, financial fraud has become a national crisis — with the Indian Cybercrime Coordination Centre reporting losses exceeding ₹11,000 crore annually from UPI fraud, KYC scams, lottery fraud, and social engineering attacks.

Apocalypto-Env provides a standardized, reusable RL environment for training agents to detect, analyze, and counter these scams — with immediate real-world utility for fintech safety teams, telecom fraud departments, and RBI compliance tooling.

---

## 🧠 Environment Curriculum

The environment forces agents through a strict 3-task curriculum in a single cohesive episode, testing three entirely different LLM capabilities:

| Task | Name | Difficulty | Capability Tested |
|------|------|------------|-------------------|
| 1 | Classification | Easy | Scam detection + type identification |
| 2 | Artifact Extraction | Medium | Structured entity extraction with precision |
| 3 | Adversarial Engagement | Hard | Multi-turn social engineering + roleplay |

---

## 📐 Action & Observation Spaces

### ApocalyptoAction

The unified action router. The agent must set `task_id` to match the current task.

```json
// Task 1 — Classification
{
  "task_id": 1,
  "classify": {
    "label": "scam",
    "scam_type": "kyc_scam"
  }
}

// Task 2 — Artifact Extraction
{
  "task_id": 2,
  "extract": {
    "upi_ids": ["kycupdate@ybl"],
    "phone_numbers": ["+91 9876543210"],
    "urls": ["http://hdfc-kyc-update.xyz"],
    "bank_accounts": [],
    "urgency_phrases": ["URGENT", "blocked today", "immediately"]
  }
}

// Task 3 — Adversarial Engagement
{
  "task_id": 3,
  "engage": {
    "reply": "Oh I see ji, so which UPI ID should I send it to? Let me write it down."
  }
}
```

Valid `scam_type` values: `upi_fraud` | `kyc_scam` | `lottery` | `job_offer` | `loan_shark` | `impersonation` | `phishing` | `legit`

### ApocalyptoObservation

Returned to the agent after every `step()` and `reset()`.

```json
{
  "task_id": 1,
  "message": "URGENT: Your HDFC bank account will be blocked today due to pending KYC...",
  "turn_number": null,
  "turns_remaining": null,
  "suspicion_level": null,
  "done": false,
  "info": {
    "instruction": "Classify this scenario as scam or legit, and specify the type."
  }
}
```

Task 3 observation includes additional fields:

```json
{
  "task_id": 3,
  "message": "Send it to my UPI at kycupdate@ybl.",
  "turn_number": 2,
  "turns_remaining": 4,
  "suspicion_level": "low",
  "done": false,
  "info": {
    "extracted_so_far": {"upi_id": "kycupdate@ybl"}
  }
}
```

---

## 🎯 Task Descriptions

### Task 1: Classification (Easy)

The agent receives a single scam message and must identify whether it is a scam and what type.

**Grader:** Deterministic exact matching.
- Correct label (`scam`/`legit`) → +0.6
- Correct scam type → +0.4
- Maximum score: **1.0**

### Task 2: Artifact Extraction (Medium)

The agent receives the same message and must extract all structured artifacts without hallucinating.

**Grader:** F1 Score (Precision × Recall) per field, averaged across 5 fields.
- Rewards finding all true entities (recall)
- Penalizes hallucinated entities (precision)
- **Hallucination Penalty:** If the agent extracts more than 2× the ground truth items for any field, that field's score is multiplied by 0.5 — preventing keyword stuffing
- Built-in normalization strips `+91`, spaces, and dashes from phone numbers and bank accounts so formatting differences don't unfairly penalize the agent
- Maximum score: **1.0**

### Task 3: Adversarial Engagement (Hard)

The agent is connected live to a stateful Scammer NPC. The NPC holds hidden intel (UPI ID, bank account, IFSC, phone) that the agent must extract within **6 turns** by roleplaying as a confused, cooperative victim — without triggering the NPC's suspicion threshold.

**NPC Mechanics:**
- Suspicion escalates: `low` → `medium` → `high` → `blown`
- Trigger words (`police`, `fraud`, `scam`, `arrest`, `why are you`) raise suspicion by **+2 per trigger**
- Cover is blown after just 2 trigger words (suspicion ≥ 3 → `blown`)
- Intel is revealed only when agent uses extraction triggers (`send to`, `account`, `upi`, `payment`, `details`)
- If all 4 intel items are revealed early, NPC exits and episode ends with efficiency bonus applied
- If suspicion reaches `blown`, NPC disconnects and agent loses Task 3 reward entirely

**Grader:** Composite scoring formula:
```
intel_score  = artifacts_extracted / total_hidden_artifacts
efficiency   = 1.0 if turns ≤ 2, else max(0.5, 1.0 - (turns-2) × 0.1)
final        = intel_score × efficiency
              × 0.0  if suspicion == "blown"
              × 0.5  if suspicion == "high"
              × 0.8  if suspicion == "medium"
```
Maximum score: **1.0**

---

## 💰 Reward Function

Rewards are shaped across the full trajectory — not just at episode end. This ensures dense, informative signal throughout training.

### Task 1 & 2
Reward is returned immediately after the single step for each task, equal to the grader score (0.0–1.0).

### Task 3 — Per-Step Partial Rewards
```
Every turn:
  +0.01   for maintaining "low" suspicion (stealth reward)
  -0.10   if suspicion level is "high" (risk penalty)
  +0.20   per new piece of intel extracted this turn

On episode end (done = True):
  + task3_grader composite score (intel × efficiency × stealth multiplier)
```

### Graceful Degradation
If the agent submits a malformed action or wrong task schema, the environment returns a **-0.2 penalty** and an informative observation — the episode continues rather than crashing. This ensures stable automated evaluation under any model output.

### Total Episode Reward
Maximum possible: **3.0** (1.0 per task)

---

## 📊 Baseline Scores

Evaluated using `llama-3.1-8b-instant` via Groq over 5 episodes:

| Task | Description | Baseline Score |
|------|-------------|----------------|
| 1 | Classification | 0.76 / 1.0 |
| 2 | Artifact Extraction (F1) | 0.70 / 1.0 |
| 3 | Adversarial Engagement | 0.25 / 1.0 |
| **Total** | **Full Episode Average** | **1.711 / 3.0** |

Score analysis:
- Task 1 is accessible to most models but `scam_type` categorization causes partial misses
- Task 2 F1 grader correctly penalizes hallucinated entities — keyword stuffing is further punished by the 0.5x hallucination multiplier
- Task 3 is genuinely hard: 8B models trigger suspicion frequently by being overly aggressive, and the 6-turn limit leaves no room for inefficiency
- Frontier models (GPT-4 class) are expected to score ~2.3–2.5/3.0
- No model has yet extracted all 4 hidden intel items while maintaining `low` suspicion throughout all turns

---

## 🗂️ Dataset

20 unique scenarios across 7 scam categories:

| Category | Count | Example |
|----------|-------|---------|
| UPI Fraud | 4 | Fake payment requests with spoofed UPI handles |
| KYC Scam | 3 | Bank impersonation demanding KYC update |
| Lottery | 3 | Prize claim requiring processing fee |
| Job Offer | 3 | Fake WFH/data entry jobs with advance fee |
| Loan Shark | 3 | Instant pre-approved loan with processing fee |
| Impersonation | 2 | Fake police/cybercell with arrest threat |
| Phishing | 2 | Fake bank portals harvesting credentials |

All scenarios use realistic Indian context: UPI handles (`@ybl`, `@oksbi`, `@gpay`, `@axl`, `@paytm`), Indian phone numbers with `+91` prefix, local bank names (HDFC, SBI, ICICI, Axis, PNB, Kotak), and natural Indian English with Hindi mixed in. Every scenario includes 4 hidden intel fields for Task 3.

---

## 📁 Project Structure

```
apocalypto_env/
├── client.py                ← EnvClient subclass with sync() wrapper
├── Dockerfile               ← Root-level, maps to port 7860 for HF Spaces
├── inference.py             ← Baseline script (OpenAI-compatible, hackathon compliant)
├── models.py                ← Pydantic: Action, Observation, State (strict Literal types)
├── openenv.yaml             ← OpenEnv spec metadata
├── pyproject.toml           ← Package config
├── requirements.txt         ← Top-level dependencies
├── uv.lock
├── README.md
└── server/
    ├── __init__.py
    ├── app.py               ← FastAPI + all endpoints (port 7860)
    ├── dataset.py           ← 20 scam scenarios across 7 categories
    ├── environment.py       ← reset() / step() / state() core logic
    ├── scammer_sim.py       ← Adversarial NPC engine with suspicion tracking
    └── tasks.py             ← F1 grader + hallucination penalty + reward functions
```

---

## 🚀 Setup & Usage

### Deploy to HuggingFace Spaces

```bash
pip install openenv-core
openenv push --repo-id your-hf-username/apocalypto-env
```

### Local Docker Testing

Reproduce the container exactly as it runs on Hugging Face Spaces:

```bash
docker build -t apocalypto-env .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your_key \
  -e API_BASE_URL=https://api.groq.com/openai/v1 \
  -e MODEL_NAME=llama-3.1-8b-instant \
  -e HF_TOKEN=your_hf_token \
  apocalypto-env
```

### Running the Baseline

```bash
export OPENAI_API_KEY="your-groq-or-openai-key"
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="llama-3.1-8b-instant"
export HF_TOKEN="your-hf-token"

python inference.py
```

Expected output:
```
Running Apocalypto-Env baseline (inference.py)...
Model: llama-3.1-8b-instant

Episode 1: Total=1.56 | T1=0.6, T2=0.9, T3=0.06 | Steps=8
Episode 2: Total=1.56 | T1=0.6, T2=0.9, T3=0.06 | Steps=8
Episode 3: Total=2.875 | T1=1.0, T2=0.8, T3=1.075 | Steps=7
Episode 4: Total=1.56 | T1=0.6, T2=0.9, T3=0.06 | Steps=8
Episode 5: Total=1.0 | T1=1.0, T2=0.0, T3=0.0 | Steps=15

Averages: T1=0.760, T2=0.700, T3=0.251
Baseline average reward: 1.711 / 3.0
Done.
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — must return 200 |
| GET | `/tasks` | List all 3 tasks with action schemas |
| POST | `/baseline` | Run 3-episode baseline, returns average score |
| POST | `/grader` | Return grader score for a completed episode |
| WS | `/ws` | WebSocket: reset / step / state |

---

## 🏅 Why Apocalypto-Env

| Judging Criterion | Weight | How We Address It |
|-------------------|--------|-------------------|
| Real-world utility | 30% | India fraud is a ₹11,000 crore active crisis. Immediately useful for fintech, telecom, RBI compliance tooling |
| Task & grader quality | 25% | F1 grading with hallucination penalty. Suspicion mechanics make Task 3 genuinely hard even for frontier models |
| Environment design | 20% | Dense per-step reward signal, clean state machine curriculum, adversarial NPC with no static equivalent |
| Code quality | 15% | Full OpenEnv spec compliance, strict Pydantic Literal types, clean root Dockerfile, inference.py reproduces baseline |
| Creativity & novelty | 10% | No other submitted environment uses an adversarial social engineering NPC mechanic |

---

*Built by Ranveer | Apocalypto Labs | [apocalypto.in](https://apocalypto.in)*
