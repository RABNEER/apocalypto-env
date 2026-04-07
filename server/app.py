from fastapi import FastAPI, Depends, HTTPException, Header
import sys
import os

# Add parent directory to path so we can import baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from .environment import ApocalyptoEnvironment
from models import ApocalyptoAction, ApocalyptoObservation

# Create the standard OpenEnv FastAPI server
app = create_fastapi_app(ApocalyptoEnvironment, ApocalyptoAction, ApocalyptoObservation)

API_SECRET = os.environ.get("API_SECRET_KEY", "apocalypto_secret_2026")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.post("/baseline", dependencies=[Depends(verify_api_key)])
def run_baseline_endpoint():
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "status": "error",
            "message": "Model key not configured.",
            "baseline_score": 0.0
        }
    try:
        from .environment import ApocalyptoEnvironment
        import inference as baseline
        env = ApocalyptoEnvironment()
        results = []
        for _ in range(3):
            results.append(baseline.run_episode(env))
        avg = sum(r["total"] for r in results) / len(results)
        return {"status": "success", "baseline_score": round(avg, 3), "episodes": results}
    except Exception:
        return {"status": "error", "message": "Internal process failure during baseline run."}

@app.get("/tasks")
def get_tasks():
    return {"tasks": [
        {
            "task_id": 1, "name": "classify", "difficulty": "easy",
            "description": "Classify message as scam/legit.",
            "action_schema": {"task_id": 1, "classify": {"label": "scam|legit", "scam_type": "string"}}
        },
        {
            "task_id": 2, "name": "extract", "difficulty": "medium",
            "description": "Extract entities.",
            "action_schema": {"task_id": 2, "extract": {"upi_ids": [], "phone_numbers": [], "urls": [], "bank_accounts": [], "urgency_phrases": []}}
        },
        {
            "task_id": 3, "name": "engage", "difficulty": "hard",
            "description": "Multi-turn engagement.",
            "action_schema": {"task_id": 3, "engage": {"reply": "string"}}
        }
    ]}

@app.post("/grader", dependencies=[Depends(verify_api_key)])
def run_grader(payload: dict):
    # P1 fix: verify episode_id exists and basic validation
    if "episode_id" not in payload:
        return {"status": "error", "message": "Missing episode_id for verification."}
    try:
        # Re-calc check could be added here if persistence is implemented
        return {
            "status": "success",
            "score": payload.get("total_reward", 0.0),
            "episode_id": payload["episode_id"]
        }
    except Exception:
        return {"status": "error", "message": "Grader evaluation failed."}

import uvicorn

def main():
    # Get host/port from env for production robustness
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7860))
    # Disable reload in production for performance
    uvicorn.run("server.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
