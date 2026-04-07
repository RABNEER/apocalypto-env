import pytest
from server.scammer_sim import ScammerNPC

def test_scammer_initialization():
    scenario = {"id": "test", "hidden_intel": {"upi_id": "u1", "bank_account": "b1"}}
    npc = ScammerNPC(scenario)
    assert npc.suspicion_level == "low"
    assert "Hello" in npc.start_conversation()

def test_scammer_suspicion_triggers():
    scenario = {"id": "test", "hidden_intel": {"upi_id": "u1"}}
    npc = ScammerNPC(scenario)
    
    # 0 triggers
    assert npc.suspicion_level == "low"
    
    # 1 trigger
    _, level, done = npc.respond("I will call the police.")
    assert level == "medium"
    assert not done
    
    # 2 triggers
    _, level, done = npc.respond("Is this a fraud?")
    assert level == "high"
    assert not done
    
    # 3 triggers
    _, level, done = npc.respond("Who are you reporting me to?")
    assert level == "blown"
    assert done

def test_scammer_intel_reveal():
    scenario = {"id": "test", "hidden_intel": {"upi_id": "u1", "bank_account": "b1"}}
    npc = ScammerNPC(scenario)
    
    messages = []
    # Requesting intel first time
    msg1, level, done = npc.respond("What is your UPI?")
    messages.append(msg1)
    assert len(npc.revealed_keys) == 1
    assert not done
    
    # Requesting intel second time
    msg2, level, done = npc.respond("Give me your bank details.")
    messages.append(msg2)
    assert len(npc.revealed_keys) == 2
    assert done
    
    combined_msg = " ".join(messages)
    assert "u1" in combined_msg
    assert "b1" in combined_msg
