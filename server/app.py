from fastapi import FastAPI
import sys
import os

# Add parent directory to path so we can import baseline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from .environment import ApocalyptoEnvironment
import inference as baseline

# Create the standard OpenEnv FastAPI server
app = create_fastapi_app(ApocalyptoEnvironment, title="Apocalypto-Env", version="1.0.0")

@app.post("/baseline")
def run_baseline_endpoint():
    try:
        from .environment import ApocalyptoEnvironment
        import inference as baseline # Local import is safer if renamed
        env = ApocalyptoEnvironment()
        results = [baseline.run_episode(env) for _ in range(3)]
        avg = sum(r["total"] for r in results) / len(results)
        return {"status": "success", "baseline_score": round(avg, 3), "episodes": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

import uvicorn
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=True)

if __name__ == "__main__":
    main()
