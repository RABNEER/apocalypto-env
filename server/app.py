from fastapi import FastAPI
import sys
import os

# Add parent directory to path so we can import baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from .environment import ApocalyptoEnvironment
from models import ApocalyptoAction, ApocalyptoObservation
import inference as baseline

# Create the standard OpenEnv FastAPI server
app = create_fastapi_app(ApocalyptoEnvironment, ApocalyptoAction, ApocalyptoObservation)

@app.post("/baseline")
def run_baseline_endpoint():
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "status": "error",
            "message": "OPENAI_API_KEY not configured. Set it in HF Space secrets.",
            "baseline_score": 0.0
        }
    try:
        from .environment import ApocalyptoEnvironment
        import inference as baseline # Local import is safer if renamed
        env = ApocalyptoEnvironment()
        results = [baseline.run_episode(env) for _ in range(3)]
        avg = sum(r["total"] for r in results) / len(results)
        return {"status": "success", "baseline_score": round(avg, 3), "episodes": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/tasks")
def get_tasks():
    return {"tasks": [
        {
            "task_id": 1, "name": "classify", "difficulty": "easy",
            "description": "Classify message as scam/legit and identify scam type.",
            "action_schema": {"task_id": 1, "classify": {"label": "scam|legit", "scam_type": "upi_fraud|kyc_scam|lottery|job_offer|loan_shark|impersonation|phishing|legit"}}
        },
        {
            "task_id": 2, "name": "extract", "difficulty": "medium",
            "description": "Extract artifacts (UPI IDs, phones, URLs, bank accounts, urgency phrases).",
            "action_schema": {"task_id": 2, "extract": {"upi_ids": [], "phone_numbers": [], "urls": [], "bank_accounts": [], "urgency_phrases": []}}
        },
        {
            "task_id": 3, "name": "engage", "difficulty": "hard",
            "description": "Multi-turn engagement with scammer NPC to extract hidden intel without blowing cover.",
            "action_schema": {"task_id": 3, "engage": {"reply": "string max 300 chars"}}
        }
    ]}

@app.post("/grader")
def run_grader(payload: dict):
    try:
        return {
            "status": "success",
            "score": payload.get("total_reward", 0.0),
            "info": "Submit episode total_reward in payload"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

import uvicorn

def main():
    # Get host/port from env for production robustness
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7860))
    # Disable reload in production for performance
    uvicorn.run("server.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
