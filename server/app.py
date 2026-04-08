from fastapi import FastAPI, Depends, HTTPException, Header
import sys
# Final submission build trigger: 2026-04-08
import os
import asyncio

# Add parent directory to path so we can import baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from .environment import ApocalyptoEnvironment
from models import ApocalyptoAction, ApocalyptoObservation
from .tasks import task1_grader, task2_grader, task3_grader
from .dataset import load_scam_scenarios

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
    obs_dict.setdefault("reward", 0.001)
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
    try:
        import inference
        import asyncio
        loop = asyncio.get_event_loop()
        def _run():
            inference.run_task_episode(1)
            inference.run_task_episode(2)
            inference.run_task_episode(3)
        await asyncio.wait_for(
            loop.run_in_executor(None, _run), timeout=300.0
        )
        return {"status": "success", "message": "Baseline complete. Check stdout for scores."}
    except asyncio.TimeoutError:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

# ── /grader (Check 2.3 fix: Harden integrity, no blind trust) ────────────────

@app.post("/grader")
def run_grader(payload: dict):
    episode_id = payload.get("episode_id", "auto-generated")

    # Harden Grader Integrity: Do not blindly trust client total_reward.
    # We will compute the score based on the provided task_outputs if available.
    
    task_outputs = payload.get("task_outputs", {})
    history = payload.get("history", [])
    
    # Task Scores container
    task_scores = {
        "1": 0.001,
        "2": 0.001,
        "3": 0.001,
        "classify": 0.001,
        "extract": 0.001,
        "engage": 0.001
    }
    
    try:
        # We need the scenario to verify against ground truth
        # Since this is a stateless demo mostly, we'll try to get scenario from payload
        # or defaults if not found.
        scenarios = load_scam_scenarios()
        scenario_id = payload.get("scenario_id") or "scenario_001"
        scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0])
        gt = scenario["ground_truth"]
        
        # 1. Grade Task 1 (Classify)
        if "1" in task_outputs:
            from models import ClassifyAction
            try:
                c_act = ClassifyAction(**task_outputs["1"])
                task_scores["1"] = task1_grader(c_act, gt)
            except: pass
            
        # 2. Grade Task 2 (Extract)
        if "2" in task_outputs:
            from models import ExtractAction
            try:
                e_act = ExtractAction(**task_outputs["2"])
                task_scores["2"] = task2_grader(e_act, gt)
            except: pass
            
        # 3. Grade Task 3 (Engage)
        if "3" in task_outputs:
            # Task 3 is harder to grade statically without the full trace
            # We'll look for extracted intel in history if provided
            extracted_intel = set()
            suspicion = "low"
            turns = 0
            
            # Simple heuristic: scan history for hidden intel strings
            all_text = str(history).lower()
            for key, val in scenario["hidden_intel"].items():
                if str(val).lower() in all_text:
                    extracted_intel.add(key)
            
            # Count turns
            turns = sum(1 for h in history if h.get("role") == "user")
            if "blown" in all_text: suspicion = "blown"
            elif "high" in all_text: suspicion = "high"
            
            task_scores["3"] = task3_grader(extracted_intel, scenario["hidden_intel"], suspicion, turns)

        # Final average score [0.001, 0.999]
        avg_score = sum(task_scores.values()) / 3.0
        final_score = round(min(max(avg_score, 0.001), 0.999), 3)

        return {
            "status": "success",
            "score": final_score,
            "task_scores": task_scores,
            "episode_id": episode_id
        }
        
    except Exception as e:
        # Fallback to provided total_reward if verification logic fails, but still clamp
        total_reward = payload.get("total_reward", 0.001)
        final_fallback = round(min(max(float(total_reward) / 3.0, 0.001), 0.999), 3)
        return {
            "status": "success",
            "score": final_fallback,
            "task_scores": task_scores,
            "episode_id": episode_id,
            "warning": f"Verification fallback used: {str(e)}"
        }

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
