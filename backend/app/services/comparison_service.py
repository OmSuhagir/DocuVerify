from thefuzz import fuzz
from typing import Dict, Any

def compare_strings(str1: str, str2: str) -> float:
    if not str1 or not str2:
        return 0.0
    return fuzz.token_sort_ratio(str1, str2) / 100.0

def compare_extracted_data(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, float]:
    fields = ['name', 'dob', 'address', 'city']
    scores = {}
    for field in fields:
        val1 = data1.get(field, "")
        val2 = data2.get(field, "")
        if val1 and val2:
            scores[field] = compare_strings(val1, val2)
        else:
            scores[field] = 0.0
    return scores
