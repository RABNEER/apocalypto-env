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
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
)
MODEL = os.environ.get("MODEL_NAME", "llama3-8b-8192")
HF_TOKEN = os.environ.get("HF_TOKEN", "")  # Required by spec

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

    while not obs.done and steps < 15:
        current_task = obs.task_id
        # Inject task_id explicitly into every prompt to prevent schema confusion
        user_content = f"""Current task_id: {current_task}
You MUST respond with task_id {current_task} schema only.

Observation:
{json.dumps(obs.model_dump(), indent=2)}"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0,
            # response_format={"type": "json_object"} # Some providers don't support this
        )

        try:
            raw = response.choices[0].message.content
            # Strip markdown code fences if model adds them
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            action_json = json.loads(raw)

            # Robustness heuristic: if model outputs multiple types (e.g., "kyc_scam|phishing"), pick the first one
            if "classify" in action_json and isinstance(action_json["classify"], dict):
                st = action_json["classify"].get("scam_type", "")
                if isinstance(st, str) and "|" in st:
                    action_json["classify"]["scam_type"] = st.split("|")[0].strip()

            action = ApocalyptoAction(**action_json)
            
            # Record reward for the current task
            prev_reward = env.state.total_reward
            obs = env.step(action)
            step_reward = env.state.total_reward - prev_reward
            
            # Since env advances task automatically, we map the reward to the task we STARTED the step with
            task_scores[current_task] += step_reward

        except Exception as e:
            print(f"  [Step {steps}] Error: {e}")
            pass

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
    print("Running Apocalypto-Env baseline (inference.py)...")
    print(f"Model: {MODEL}")
    print(f"API Base: {client.base_url}")
    print("-" * 40)

    env = ApocalyptoEnvironment()
    results = []

    for i in range(5):
        res = run_episode(env)
        results.append(res)
        print(f"Episode {i+1}: Total={res['total']} | T1={res['task1']}, T2={res['task2']}, T3={res['task3']} | Steps={res['steps']}")

    avg = sum(r["total"] for r in results) / len(results)
    avg_t1 = sum(r["task1"] for r in results) / len(results)
    avg_t2 = sum(r["task2"] for r in results) / len(results)
    avg_t3 = sum(r["task3"] for r in results) / len(results)
    
    print("-" * 40)
    print(f"Averages: T1={avg_t1:.3f}, T2={avg_t2:.3f}, T3={avg_t3:.3f}")
    print(f"Final Baseline Reward: {avg:.3f} / 3.0")
    print("Done.")
