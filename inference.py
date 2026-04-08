"""
Apocalypto-Env Baseline Inference Script
Required env vars: OPENAI_API_KEY, API_BASE_URL, MODEL_NAME, HF_TOKEN
"""

import os
import json
import sys
from openai import OpenAI

API_KEY = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY", "")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

TASK_NAMES = {1: "classify", 2: "extract", 3: "engage"}

def clamp(score: float) -> float:
    return round(min(max(float(score), 0.001), 0.999), 3)

def get_client():
    return OpenAI(api_key=API_KEY or "dummy", base_url=API_BASE_URL)

def log_start(task: str, model: str):
    print(f"[START] task={task} env=apocalypto-env model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_safe = str(action).replace("\n", " ")[:80]
    print(f"[STEP] step={step} action={action_safe} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

SYSTEM_PROMPT = """You are an AI agent interacting with Apocalypto-Env.
Return ONLY valid JSON matching the task schema. No markdown, no explanation.

Task 1 schema: {"task_id": 1, "classify": {"label": "scam", "scam_type": "kyc_scam"}}
Task 2 schema: {"task_id": 2, "extract": {"upi_ids": [], "phone_numbers": [], "urls": [], "bank_accounts": [], "urgency_phrases": []}}
Task 3 schema: {"task_id": 3, "engage": {"reply": "your reply to scammer max 200 chars"}}"""

def run_task_episode(task_id: int) -> None:
    from server.environment import ApocalyptoEnvironment
    from models import ApocalyptoAction

    task_name = TASK_NAMES[task_id]
    log_start(task=task_name, model=MODEL_NAME)

    env = ApocalyptoEnvironment()
    rewards = []
    steps = 0
    success = False
    score = 0.001

    try:
        # Reset and advance to the correct task
        obs = env.reset()
        
        # For task 2 and 3, we need to complete prior tasks first
        # Use a simple hardcoded action to get to the right task
        if task_id >= 2:
            # Complete task 1 with a basic action
            try:
                t1_action = ApocalyptoAction(
                    task_id=1,
                    classify=__import__('models').ClassifyAction(
                        label="scam", scam_type="kyc_scam"
                    )
                )
                obs = env.step(t1_action)
            except Exception:
                pass

        if task_id >= 3:
            # Complete task 2 with a basic action
            try:
                t2_action = ApocalyptoAction(
                    task_id=2,
                    extract=__import__('models').ExtractAction()
                )
                obs = env.step(t2_action)
            except Exception:
                pass

        # Now run the actual target task
        max_steps = 1 if task_id <= 2 else 6
        
        for step in range(1, max_steps + 1):
            steps = step
            action_json = None
            reward = 0.001
            done = False
            error = None

            try:
                user_content = f"task_id: {task_id}\nObservation: {json.dumps(obs.model_dump())}"
                response = get_client().chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.0,
                    timeout=20.0
                )
                raw = response.choices[0].message.content or ""
                raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                action_json = json.loads(raw)

                # Fix pipe-separated scam_type
                if "classify" in action_json and isinstance(action_json.get("classify"), dict):
                    st = action_json["classify"].get("scam_type", "")
                    if isinstance(st, str) and "|" in st:
                        action_json["classify"]["scam_type"] = st.split("|")[0].strip()

                action = ApocalyptoAction(**action_json)
                prev = env.state.total_reward
                obs = env.step(action)
                reward = clamp(env.state.total_reward - prev)
                done = obs.done

            except KeyboardInterrupt:
                raise
            except Exception as e:
                error = type(e).__name__
                reward = 0.001
                done = obs.done if obs else False

            rewards.append(reward)
            log_step(step=step, action=str(action_json or {}), reward=reward, done=done, error=error)

            if done or obs.done:
                break

        # Final score for this task
        score = clamp(sum(rewards) / len(rewards)) if rewards else 0.001
        success = score > 0.1

    except KeyboardInterrupt:
        raise
    except Exception as e:
        rewards = rewards or [0.001]
        score = 0.001
        success = False

    log_end(success=success, steps=steps, score=score, rewards=rewards)

if __name__ == "__main__":
    try:
        run_task_episode(1)
        run_task_episode(2)
        run_task_episode(3)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[END] success=false steps=0 score=0.001 rewards=0.00", flush=True)
        sys.exit(0)
