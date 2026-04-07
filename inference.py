"""
Apocalypto-Env Baseline Inference Script
Official hackathon compliance: named inference.py, uses OpenAI client only.
Required env vars: OPENAI_API_KEY, API_BASE_URL, MODEL_NAME, HF_TOKEN
"""

import os
import json
from openai import OpenAI
from server.environment import ApocalyptoEnvironment
from models import ApocalyptoAction

# Official required env var names — do not rename these
def get_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        base_url=os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
    )

def get_model():
    return os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")

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


def run_episode(env: ApocalyptoEnvironment) -> dict:
    """Runs one full episode (Task 1 → Task 2 → Task 3) and returns result dict."""
    obs = env.reset()
    task_scores = {1: 0.0, 2: 0.0, 3: 0.0}
    steps = 0
    consecutive_errors = 0

    while not obs.done and steps < 15:
        if consecutive_errors > 3:
            print(f"  [Abort] Too many consecutive errors at step {steps}. Ending episode.")
            break

        current_task = obs.task_id
        user_content = f"Current task_id: {current_task}\nObservation: {json.dumps(obs.model_dump())}"

        try:
            response = get_client().chat.completions.create(
                model=get_model(),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0,
            )
            raw = response.choices[0].message.content
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            action_json = json.loads(raw)

            action = ApocalyptoAction(**action_json)
            prev_reward = env.state.total_reward
            obs = env.step(action)
            step_reward = env.state.total_reward - prev_reward
            task_scores[current_task] += step_reward
            consecutive_errors = 0 # reset on success

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"  [Step {steps}] Error: {type(e).__name__}")
            consecutive_errors += 1
            # If we hit an error, we MUST refresh observation from env or move on
            # to avoid stale loops. Here we just increment steps and hope next retry works
            # or environmental safety kicks in.

        steps += 1

    total = env.state.total_reward
    return {
        "task1": round(task_scores[1], 3),
        "task2": round(task_scores[2], 3),
        "task3": round(task_scores[3], 3),
        "total": round(total, 3),
        "steps": steps
    }


if __name__ == "__main__":
    import sys
    try:
        print("Running Apocalypto-Env baseline (inference.py)...")
        print(f"Model: {get_model()}")
        print("-" * 40)

        env = ApocalyptoEnvironment()
        results = []

        for i in range(5):
            res = run_episode(env)
            results.append(res)
            print(f"Episode {i+1}: Total={res['total']} | T1={res['task1']}, T2={res['task2']}, T3={res['task3']} | Steps={res['steps']}")

        avg = sum(r["total"] for r in results) / len(results)
        print("-" * 40)
        print(f"Final Baseline Reward: {avg:.3f} / 3.0")
        print("Done.")

    except Exception as e:
        print(f"FATAL: Baseline failed: {e}")
        # Exit with code 1 for failure signaling (P2 fix)
        sys.exit(1)
