from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# ── TASK 1 ──────────────────────────────────────────────────────────────────

class ClassifyAction(BaseModel):
    label: Literal["scam", "legit"]
    scam_type: Literal[
        "upi_fraud", "kyc_scam", "lottery",
        "job_offer", "loan_shark", "impersonation",
        "phishing", "legit"
    ]

# ── TASK 2 ──────────────────────────────────────────────────────────────────

class ExtractAction(BaseModel):
    upi_ids: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    bank_accounts: List[str] = Field(default_factory=list)
    urgency_phrases: List[str] = Field(default_factory=list)

# ── TASK 3 ──────────────────────────────────────────────────────────────────

class EngageAction(BaseModel):
    reply: str = Field(..., max_length=300)

# ── UNIFIED ACTION ───────────────────────────────────────────────────────────

class ApocalyptoAction(BaseModel):
    task_id: Literal[1, 2, 3]
    classify: Optional[ClassifyAction] = None
    extract: Optional[ExtractAction] = None
    engage: Optional[EngageAction] = None

# ── OBSERVATION ──────────────────────────────────────────────────────────────

class ApocalyptoObservation(BaseModel):
    task_id: int
    message: str                            # The scam message or thread
    turn_number: Optional[int] = None       # Task 3 only
    turns_remaining: Optional[int] = None   # Task 3 only
    suspicion_level: Optional[str] = None   # Task 3 only: low / medium / high / blown
    done: bool = False
    info: dict = Field(default_factory=dict)

# ── STATE ────────────────────────────────────────────────────────────────────

class ApocalyptoState(BaseModel):
    episode_id: str
    current_task: int
    step_count: int               # Global steps for the entire episode
    task3_turns: int = 0          # Specifically tracks Task 3 turn limit (Max 8)
    total_reward: float
    done: bool
