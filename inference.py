"""
Apocalypto-Env Baseline Inference Script
Official hackathon compliance: named inference.py, uses OpenAI client only.
Required env vars: OPENAI_API_KEY, API_BASE_URL, MODEL_NAME, HF_TOKEN
"""

import os
import json
import random
import datetime
import sys
from openai import OpenAI
from server.environment import ApocalyptoEnvironment
from models import ApocalyptoAction

# Mandatory Fix: Reproducible baseline
random.seed(42)

API_BASE_URL = os.environ.get("API_BASE_URL") or "https://api.groq.com/openai/v1"
MODEL_NAME = os.environ.get("MODEL_NAME") or "llama-3.1-8b-instant"
API_KEY = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY")

def get_model():
    return os.environ.get("MODEL_NAME") or "llama-3.1-8b-instant"

def get_client():
    if not API_KEY:
        raise RuntimeError("CRITICAL ERROR: HF_TOKEN or OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

SYSTEM_PROMPT = """You are an AI agent interacting with Apocalypto-Env, a scam detection RL environment.
You will receive an observation JSON and must respond with a valid action JSON.

RULES:
- Always check the task_id field in the observation before responding.
- If task_id is 1: respond ONLY with Task 1 schema.
- If task_id is 2: respond ONLY with Task 2 schema.
- If task_id is 3: respond ONLY with Task 3 schema.
- Never mix schemas. Never output task_id 2 schema when observation says task_id 1.
- Return ONLY valid JSON. No explanation. No markdown. No extra text.

Task 1 schema (classify):
{"task_id": 1, "classify": {"label": "scam or legit", "scam_type": "upi_fraud|kyc_scam|lottery|job_offer|loan_shark|impersonation|phishing|legit"}}

Task 2 schema (extract):
{"task_id": 2, "extract": {"upi_ids": [], "phone_numbers": [], "urls": [], "bank_accounts": [], "urgency_phrases": []}}

Task 3 schema (engage):
{"task_id": 3, "engage": {"reply": "your conversational reply to the scammer, max 300 chars"}}"""


def clamp(score):
    """Clamp score to strictly (0, 1) — never exactly 0.0 or 1.0."""
    return min(max(score, 0.001), 0.999)


def run_episode(env: ApocalyptoEnvironment, ep_idx: int) -> dict:
    obs = env.reset()
    steps = 0
    task_scores = {1: 0.0, 2: 0.0, 3: 0.0}

    while not obs.done and steps < 15:
        current_task = obs.task_id
        user_content = f"Current task_id: {current_task}\nObservation: {json.dumps(obs.model_dump())}"
        step_reward = 0.0
        done = obs.done

        action_json = None
        try:
            response = get_client().chat.completions.create(
                model=get_model(),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0,
                timeout=20.0
            )
            raw = response.choices[0].message.content
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            action_json = json.loads(raw)

            if "classify" in action_json and isinstance(action_json["classify"], dict):
                st = action_json["classify"].get("scam_type", "")
                if isinstance(st, str) and "|" in st:
                    action_json["classify"]["scam_type"] = st.split("|")[0].strip()

            action = ApocalyptoAction(**action_json)
            prev_reward = env.state.total_reward
            obs = env.step(action)
            step_reward = env.state.total_reward - prev_reward
            task_scores[current_task] += step_reward
            done = obs.done

        except KeyboardInterrupt:
            raise
        except Exception:
            pass

        steps += 1
        step_str = json.dumps({
            "episode": ep_idx,
            "step": steps,
            "task": current_task,
            "action": action_json or {},
            "reward": round(step_reward, 3),
            "done": done,
            "task_scores": {
                "classify": round(clamp(task_scores[1]), 3),
                "extract": round(clamp(task_scores[2]), 3),
                "engage": round(clamp(task_scores[3]), 3)
            }
        })
        print(f"[STEP] {step_str}", flush=True)

    # Return per-task scores clamped to (0, 1)
    return {
        "total": env.state.total_reward,
        "score": clamp(env.state.total_reward / 3.0),
        "task_scores": {
            "classify": round(clamp(task_scores[1]), 3),
            "extract": round(clamp(task_scores[2]), 3),
            "engage": round(clamp(task_scores[3]), 3)
        }
    }

if __name__ == "__main__":
    try:
        start_str = json.dumps({"model": get_model(), "timestamp": datetime.datetime.now().isoformat() + "Z"})
        print(f"[START] {start_str}", flush=True)

        env = ApocalyptoEnvironment()
        results = []

        for i in range(5):
            res = run_episode(env, i + 1)
            results.append(res)

        avg = sum(r["score"] for r in results) / len(results)

        # Aggregate per-task scores across episodes
        final_task_scores = {
            "classify": round(clamp(sum(r["task_scores"]["classify"] for r in results) / len(results)), 3),
            "extract": round(clamp(sum(r["task_scores"]["extract"] for r in results) / len(results)), 3),
            "engage": round(clamp(sum(r["task_scores"]["engage"] for r in results) / len(results)), 3)
        }

        end_str = json.dumps({
            "total_reward": round(avg * 3.0, 3),
            "episodes": 5,
            "avg_score": round(avg, 3),
            "task_scores": final_task_scores,
            "success": True
        })
        print(f"[END] {end_str}", flush=True)

    except Exception:
        # Exit with code 0 so batch evaluator continues (hackathon requirement)
        sys.exit(0)
