"""
Apocalypto-Env: Adversarial Social Engineering and Fraud Detection RL Environment.
Meta x HuggingFace OpenEnv Hackathon India | Round 1 Submission.
"""

from .environment import ApocalyptoEnvironment
from .scammer_sim import ScammerNPC
from .dataset import load_scam_scenarios

__all__ = ["ApocalyptoEnvironment", "ScammerNPC", "load_scam_scenarios"]
