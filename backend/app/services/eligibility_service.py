from typing import Tuple

def determine_eligibility(overall_score: float) -> Tuple[bool, str]:
    if overall_score >= 0.99:
        return True, "Verified – Eligible for passport application"
    elif overall_score >= 0.90 and overall_score <0.99:
        return False, "Minor discrepancies – Manual review recommended"
    elif overall_score >= 0.80 and overall_score <0.90:
        return False, "Major discrepancies – Manual review recommended"
    else:
        return False, "Verification failed – Not eligible"
