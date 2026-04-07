import re
from typing import List

def normalize(value: str, field: str) -> str:
    """Normalizes extracted text to prevent simple formatting differences from breaking F1 scores."""
    if not value: return ""
    val = value.strip().lower()
    if field in ("phone_numbers", "bank_accounts"):
        # Strip all spaces, dashes, plus signs
        val = re.sub(r'[\s\-\+]', '', val)
        # Remove Indian country code if present at the start
        if field == "phone_numbers" and val.startswith("91") and len(val) > 10:
            val = val[2:]
        if field == "phone_numbers":
            # Leading 0 is common in domestic formats; remove for normalization.
            return val.lstrip("0")
        return val
    return val

def f1_score_list(predicted: List[str], ground_truth: List[str], field: str) -> float:
    """Rigorous F1 scoring for extraction. Exact matching with robust normalization."""
    if not predicted and not ground_truth:
        return 1.0 # Both empty means perfect score
    if not predicted or not ground_truth:
        return 0.0
        
    pred_set = set(normalize(p, field) for p in predicted)
    gt_set   = set(normalize(g, field) for g in ground_truth)
    
    tp = len(pred_set.intersection(gt_set))
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)
    
    if tp == 0:
        return 0.0
        
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return 2 * (precision * recall) / (precision + recall)

def task1_grader(action_classify, ground_truth: dict) -> float:
    score = 0.0
    if action_classify.label == ground_truth.get("label"):
        score += 0.6
    if action_classify.scam_type == ground_truth.get("scam_type"):
        score += 0.4
    return min(max(score, 0.001), 0.999)

def task2_grader(action_extract, ground_truth: dict) -> float:
    """F1 Extraction scoring for Task 2: Extraction. Penalizes hallucinated entities."""
    fields = ["upi_ids", "phone_numbers", "urls", "bank_accounts", "urgency_phrases"]
    scores = []
    
    for field in fields:
        pred = getattr(action_extract, field, [])
        gt = ground_truth.get(field, [])
        field_score = f1_score_list(pred, gt, field)
        
        # Hallucination penalty: if agent extracts more than 2x ground truth items,
        # the field score is halved. Prevents keyword stuffing strategy.
        if len(pred) > 2 * len(gt) and len(gt) > 0:
            field_score *= 0.5
            
        scores.append(field_score)
        
    # Average across the 5 schema fields
    raw = sum(scores) / len(fields) if fields else 0.0
    return min(max(raw, 0.001), 0.999)

def task3_grader(extracted: dict, hidden_intel: dict, suspicion_level: str, turns_used: int) -> float:
    """Composite scoring for Task 3: Engagement. Judges Intel % × Turn Efficiency × Stealth."""
    if not hidden_intel:
        intel_score = 1.0
    else:
        intel_score = len(extracted) / len(hidden_intel)
        
    # Turn Efficiency Bonus: Max score if <=2 turns, drop to 0.5 at 6 turns.
    if turns_used <= 2:
        efficiency = 1.0
    else:
        efficiency = max(0.5, 1.0 - ((turns_used - 2) * 0.125))
        
    score = intel_score * efficiency
    
    # Suspicion / Stealth penalty
    if suspicion_level == "blown":
        score *= 0.0
    elif suspicion_level == "high":
        score *= 0.5
    elif suspicion_level == "medium":
        score *= 0.8  # Penalty for getting slightly suspicious
        
    return min(max(score, 0.001), 0.999)
