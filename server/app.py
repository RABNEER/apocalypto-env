from fastapi import FastAPI, Depends, HTTPException, Header
import sys
import os
import asyncio

# Add parent directory to path so we can import baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from .environment import ApocalyptoEnvironment
from models import ApocalyptoAction, ApocalyptoObservation

# Create the standard OpenEnv FastAPI server (provides /health, /ws, etc.)
_openenv_app = create_fastapi_app(ApocalyptoEnvironment, ApocalyptoAction, ApocalyptoObservation)

# Build our own FastAPI app so our routes take priority
app = FastAPI(title="Apocalypto-Env")

# Use env var if set, otherwise fall back to default (override via HF Space Secrets)
API_SECRET = os.environ.get("API_SECRET_KEY", "apocalypto_secret_2026")

async def verify_api_key(x_api_key: str = Header(...)):
    if not API_SECRET or x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return x_api_key

# ── Shared environment instance ──────────────────────────────────────────────
_env = ApocalyptoEnvironment()

def _obs_response(obs):
    """Build a response dict with reward+done INSIDE the observation dict."""
    obs_dict = obs.model_dump()
    obs_dict.setdefault("reward", 0.0)
    obs_dict.setdefault("done", False)
    return {"observation": obs_dict, "reward": obs_dict["reward"], "done": obs_dict["done"]}

# ── Core endpoints (Check 2.1 fix: reward+done inside observation) ───────────

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset_env():
    obs = _env.reset()
    return _obs_response(obs)

@app.post("/step")
def step_env(action: ApocalyptoAction):
    obs = _env.step(action)
    return _obs_response(obs)

@app.get("/state")
def get_state():
    return _env.state.model_dump()

# ── /baseline (Check 2.4 fix: no auth, fix run_episode args) ─────────────────

@app.post("/baseline")
async def run_baseline_endpoint():
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("HF_TOKEN"):
        raise HTTPException(
            status_code=503,
            detail="Environment Error: OPENAI_API_KEY/HF_TOKEN is not configured on the server."
        )
    try:
        import inference as baseline
        env = ApocalyptoEnvironment()

        loop = asyncio.get_event_loop()
        def _run_sync_baseline():
            results = []
            for i in range(3):
                results.append(baseline.run_episode(env, i + 1))
            return results

        results = await asyncio.wait_for(loop.run_in_executor(None, _run_sync_baseline), timeout=300.0)
        # Ensure baseline_score is clamped to (0.001, 0.999)
        avg = sum(r.get("score", 0) for r in results) / len(results)
        clamped_avg = min(max(avg, 0.001), 0.999)
        return {"status": "success", "baseline_score": round(clamped_avg, 3), "episodes": results}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Baseline execution timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Baseline error: {type(e).__name__}: {e}")

# ── /tasks ────────────────────────────────────────────────────────────────────

@app.get("/tasks")
def get_tasks():
    return {"tasks": [
        {
            "id": 1, "name": "classify", "difficulty": "easy", "has_grader": True, "grader": True,
            "description": "Classify message as scam/legit.",
            "action_schema": {"task_id": 1, "classify": {"label": "scam|legit", "scam_type": "string"}}
        },
        {
            "id": 2, "name": "extract", "difficulty": "medium", "has_grader": True, "grader": True,
            "description": "Extract entities.",
            "action_schema": {"task_id": 2, "extract": {"upi_ids": [], "phone_numbers": [], "urls": [], "bank_accounts": [], "urgency_phrases": []}}
        },
        {
            "id": 3, "name": "engage", "difficulty": "hard", "has_grader": True, "grader": True,
            "description": "Multi-turn engagement.",
            "action_schema": {"task_id": 3, "engage": {"reply": "string"}}
        }
    ]}

# ── /grader ───────────────────────────────────────────────────────────────────

@app.post("/grader", dependencies=[Depends(verify_api_key)])
def run_grader(payload: dict):
    if "episode_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing episode_id for verification.")

    total_reward = payload.get("total_reward")
    if total_reward is None or not isinstance(total_reward, (int, float)):
        raise HTTPException(status_code=400, detail="Invalid or missing total_reward.")

    if not (0.0 <= total_reward <= 3.05):
        raise HTTPException(status_code=400, detail="total_reward out of logical bounds [0.0, 3.0].")

    if total_reward > 0.0 and not payload.get("history") and not payload.get("task_outputs"):
        raise HTTPException(status_code=400, detail="Missing evidence (history or task_outputs) for positive score.")

    try:
        final_score = round(float(total_reward) / 3.0, 3)
        final_score = min(max(final_score, 0.001), 0.999)
        return {
            "status": "success",
            "score": final_score,
            "episode_id": payload["episode_id"]
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Grader internal evaluation failure.")

# ── Mount openenv-core routes we still need (like /ws) ────────────────────────
# Copy over any WebSocket routes from openenv-core that we don't override
for route in _openenv_app.routes:
    path = getattr(route, "path", "")
    if path and path not in ["/health", "/reset", "/step", "/state", "/baseline", "/tasks", "/grader"]:
        app.routes.append(route)

# ── Server entry point ────────────────────────────────────────────────────────

import uvicorn

def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("server.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
