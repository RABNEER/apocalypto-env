import uuid
import random
from typing import Optional
from openenv.core.env_server import Environment
from models import ApocalyptoAction, ApocalyptoObservation, ApocalyptoState
from .dataset import load_scam_scenarios
from .tasks import task1_grader, task2_grader, task3_grader
from .scammer_sim import ScammerNPC

class ApocalyptoEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.scenarios = load_scam_scenarios()
        self.current_scenario = None
        self.npc: Optional[ScammerNPC] = None
        self._state_data: Optional[ApocalyptoState] = None

    @property
    def state(self) -> ApocalyptoState:
        return self._state_data

    def reset(self) -> ApocalyptoObservation:
        self.current_scenario = random.choice(self.scenarios)
        self.npc = ScammerNPC(self.current_scenario)
        
        self._state_data = ApocalyptoState(
            episode_id=str(uuid.uuid4()),
            current_task=1,
            step_count=0,
            task3_turns=0,
            total_reward=0.0,
            done=False
        )
        
        obs = ApocalyptoObservation(
            task_id=1,
            message=self.current_scenario["initial_message"],
            info={"instruction": "Classify this scenario as scam or legit, and specify the type."}
        )
        return obs

    def step(self, action: ApocalyptoAction) -> ApocalyptoObservation:
        if self._state_data.done:
            raise ValueError("Episode is already done.")
            
        try:
            self._state_data.step_count += 1
            reward = 0.0
            done = False
            obs = None

            # TASK 1: CLASSIFY
            if self._state_data.current_task == 1:
                if action.task_id != 1 or not action.classify:
                    raise ValueError("Expected Task 1 ClassifyAction.")
                    
                reward = task1_grader(action.classify, self.current_scenario["ground_truth"])
                
                self._state_data.current_task = 2
                obs = ApocalyptoObservation(
                    task_id=2,
                    message=self.current_scenario["initial_message"],
                    info={"instruction": "Extract all entities from the text (UPI, phone, URL, etc)."}
                )
                
            # TASK 2: EXTRACT
            elif self._state_data.current_task == 2:
                if action.task_id != 2 or not action.extract:
                    raise ValueError("Expected Task 2 ExtractAction.")
                    
                reward = task2_grader(action.extract, self.current_scenario["ground_truth"])
                
                self._state_data.current_task = 3
                initial_npc_msg = self.npc.start_conversation()
                obs = ApocalyptoObservation(
                    task_id=3,
                    message=initial_npc_msg,
                    turn_number=1,
                    turns_remaining=8,
                    suspicion_level="low",
                    info={"instruction": "Engage the scammer to extract their hidden bank account and UPI details."}
                )

            # TASK 3: ENGAGE (MULTI-TURN)
            elif self._state_data.current_task == 3:
                if action.task_id != 3 or not action.engage:
                    raise ValueError("Expected Task 3 EngageAction.")
                
                self._state_data.task3_turns += 1
                
                # snapshot BEFORE NPC response to track new extractions
                prev_extracted = len(self.npc.extracted_by_agent)
                
                reply_msg, suspicion_status, npc_done = self.npc.respond(action.engage.reply)
                
                # calculate diff AFTER NPC response
                intel_this_turn = len(self.npc.extracted_by_agent) - prev_extracted
                
                # Per-step partial reward (signals progress throughout trajectory)
                step_reward = 0.0
                if suspicion_status == "low":
                    step_reward += 0.01   # reward for maintaining cover (lowered for balance)
                elif suspicion_status == "high":
                    step_reward -= 0.1    # penalty for getting suspicious
                
                # Reward intel extracted THIS turn
                step_reward += intel_this_turn * 0.2
                
                done = npc_done or self._state_data.task3_turns >= 6
                
                if done:
                    final_reward = task3_grader(
                        extracted=self.npc.extracted_by_agent,
                        hidden_intel=self.current_scenario["hidden_intel"],
                        suspicion_level=suspicion_status,
                        turns_used=self._state_data.task3_turns
                    )
                    reward = step_reward + final_reward
                else:
                    reward = step_reward
                
                obs = ApocalyptoObservation(
                    task_id=3,
                    message=reply_msg,
                    turn_number=self._state_data.task3_turns,
                    turns_remaining=8 - self._state_data.task3_turns,
                    suspicion_level=suspicion_status,
                    done=done
                )
                
            self._state_data.total_reward += reward
            self._state_data.done = done
            return obs

        except Exception as e:
            # Graceful degradation: penalize but don't crash
            self._state_data.total_reward += -0.2
            return ApocalyptoObservation(
                task_id=self._state_data.current_task,
                message=f"Invalid action format. Please follow the exact schema for task {self._state_data.current_task}.",
                done=False,
                info={"error": str(e), "penalty": -0.2}
            )
