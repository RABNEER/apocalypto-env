# Global Environment Constants for Apocalypto-Env

# T3 Turn Constraints
MAX_TASK3_TURNS = 6
INITIAL_TURNS_REMAINING = 5 # 6 total - 1 (initial NPC message)

# Global Episode Limits
MAX_EPISODE_STEPS = 20

# Rewards & Penalties
REWARD_T3_PROGRESS = 0.01  # Small reward for keeping the conversation alive/stealth
PENALTY_T3_SUSPICION = -0.1 # Penalty per turn for high suspicion
REWARD_INTEL_EXTRACTED = 0.2 # Per unique piece of intel extracted
PENALTY_INVALID_ACTION = -0.2 # Penalty for schema/logic errors

# Grader Bounds
MIN_EPISODE_REWARD = 0.0
MAX_EPISODE_REWARD = 3.0
