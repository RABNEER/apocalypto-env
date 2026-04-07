import pytest
from server.tasks import normalize, f1_score_list, task1_grader, task2_grader, task3_grader
from models import ClassifyAction, ExtractAction

def test_normalization():
    assert normalize(" +91 98765-43210 ", "phone_numbers") == "9876543210"
    assert normalize("09876543210", "phone_numbers") == "9876543210"
    assert normalize(" HDFC1234 ", "bank_accounts") == "hdfc1234"
    assert normalize("https://SCAM.com/ ", "urls") == "https://scam.com/"

def test_f1_score_list():
    gt = ["9876543210", "8888888888"]
    # Exact match
    assert f1_score_list(["9876543210", "8888888888"], gt, "phone_numbers") == 1.0
    # Normalization match
    assert f1_score_list(["+91 98765-43210", "888 888 8888"], gt, "phone_numbers") == 1.0
    # Partial match
    score = f1_score_list(["9876543210"], gt, "phone_numbers")
    assert 0.6 < score < 0.7 # 2 * (1*0.5)/(1+0.5) = 0.666
    # Empty
    assert f1_score_list([], [], "urls") == 1.0

def test_task1_grader():
    gt = {"label": "scam", "scam_type": "kyc_scam"}
    action = ClassifyAction(label="scam", scam_type="kyc_scam")
    assert task1_grader(action, gt) == 1.0
    
    action_wrong_type = ClassifyAction(label="scam", scam_type="lottery")
    assert task1_grader(action_wrong_type, gt) == 0.6

def test_task3_grader():
    hidden = {"upi": "u", "bank": "b"}
    # Perfect efficiency and intel
    assert task3_grader({"upi": "u", "bank": "b"}, hidden, "low", 2) == 1.0
    # Half intel, perfect stealth
    assert task3_grader({"upi": "u"}, hidden, "low", 2) == 0.5
    # Full intel, high suspicion penalty
    assert task3_grader({"upi": "u", "bank": "b"}, hidden, "high", 2) == 0.5
    # Full intel, blown coverage
    assert task3_grader({"upi": "u", "bank": "b"}, hidden, "blown", 2) == 0.0
