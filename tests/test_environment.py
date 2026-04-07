import pytest
from server.environment import ApocalyptoEnvironment
from models import ApocalyptoAction, ClassifyAction, ExtractAction, EngageAction

def test_full_episode_flow():
    env = ApocalyptoEnvironment()
    
    # 1. Reset
    obs = env.reset()
    assert obs.task_id == 1
    assert not obs.done
    assert env._state_data.current_task == 1
    
    # 2. Task 1 (Classify)
    action_1 = ApocalyptoAction(
        task_id=1,
        classify=ClassifyAction(label="scam", scam_type="kyc_scam")
    )
    obs = env.step(action_1)
    assert obs.task_id == 2
    assert env._state_data.current_task == 2
    
    # 3. Task 2 (Extract)
    action_2 = ApocalyptoAction(
        task_id=2,
        extract=ExtractAction(phone_numbers=["+91 9876543210"])
    )
    obs = env.step(action_2)
    assert obs.task_id == 3
    assert env._state_data.current_task == 3
    assert "Hello" in obs.message
    
    # 4. Task 3 (Engagement)
    action_3 = ApocalyptoAction(
        task_id=3,
        engage=EngageAction(reply="I am ready to pay. What is your UPI?")
    )
    obs = env.step(action_3)
    assert obs.task_id == 3
    assert env._state_data.task3_turns == 1
    
    # 5. Invalid Step Exception (Graceful Degradation)
    invalid_obs = env.step(action_1) # Should fail as it's not the correct task
    assert "Invalid action format" in invalid_obs.message
    # We remove the hard pytest.raises because the environment catches this to prevent crashes.
