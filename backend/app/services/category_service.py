import itertools
from typing import List, Dict, Any, Tuple
from .comparison_service import compare_strings

def compare_category_data(data1: Dict[str, Any], data2: Dict[str, Any], fields: List[str]) -> Dict[str, float]:
    scores = {}
    for field in fields:
        val1 = data1.get(field, "")
        val2 = data2.get(field, "")
        if val1 and val2:
            scores[field] = compare_strings(val1, val2)
        else:
            scores[field] = 0.0
    return scores

def verify_session_documents(docs: List[Any]) -> Tuple[float, List[Any], Dict[str, float]]:
    comparisons = []
    category_scores = {"IDENTIFICATION": 0.0, "ADDRESS": 0.0, "NON_ECR": 0.0}
    
    id_docs = [d for d in docs if d.category == "IDENTIFICATION"]
    addr_docs = [d for d in docs if d.category == "ADDRESS"]
    non_ecr_docs = [d for d in docs if d.category == "NON_ECR"]
    
    # Calculate category specific base scores
    def get_avg_for_docs(doc_list, fields):
        if len(doc_list) <= 1: return 1.0
        avgs = []
        for d1, d2 in itertools.combinations(doc_list, 2):
            s = compare_category_data(d1.extracted_data or {}, d2.extracted_data or {}, fields)
            vals = [v for k, v in s.items() if (d1.extracted_data or {}).get(k) and (d2.extracted_data or {}).get(k)]
            if vals: avgs.append(sum(vals)/len(vals))
        return sum(avgs)/len(avgs) if avgs else 0.0

    category_scores["IDENTIFICATION"] = get_avg_for_docs(id_docs, ["name", "dob"])
    category_scores["ADDRESS"] = get_avg_for_docs(addr_docs, ["address", "city"])
    
    if non_ecr_docs and id_docs:
        v1 = (id_docs[0].extracted_data or {}).get("name", "")
        v2 = (non_ecr_docs[0].extracted_data or {}).get("candidate_name", "") or (non_ecr_docs[0].extracted_data or {}).get("name", "")
        if v1 and v2:
            category_scores["NON_ECR"] = compare_strings(v1, v2)
        else:
            category_scores["NON_ECR"] = 0.0
    else:
        category_scores["NON_ECR"] = 1.0

    # Global Pairwise Comparisons
    global_avg_scores = []
    pairs = list(itertools.combinations(docs, 2))
    
    fields_to_check = ["name", "dob", "address", "city"]
    
    for d1, d2 in pairs:
        scores = {}
        d1_data = d1.extracted_data or {}
        d2_data = d2.extracted_data or {}
        
        for field in fields_to_check:
            val1 = d1_data.get(field, "")
            val2 = d2_data.get(field, "")
            
            if field == "name":
                if not val1: val1 = d1_data.get("candidate_name", "")
                if not val2: val2 = d2_data.get("candidate_name", "")
                
            if val1 and val2:
                scores[field] = compare_strings(val1, val2)
                
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            
            cat_label = "CROSS_CATEGORY"
            if d1.category == d2.category:
                cat_label = d1.category
                
            comparisons.append({
                "doc1_id": d1.id,
                "doc2_id": d2.id,
                "category": cat_label,
                "field_scores": scores,
                "average_score": avg_score
            })
            global_avg_scores.append(avg_score)
            
    global_score = sum(global_avg_scores) / len(global_avg_scores) if global_avg_scores else 1.0
    
    return global_score, comparisons, category_scores

def determine_final_eligibility(global_score: float, category_scores: Dict[str, float]) -> Tuple[bool, str]:
    all_passed = (
        category_scores["IDENTIFICATION"] >= 0.90 and 
        category_scores["ADDRESS"] >= 0.80 and 
        category_scores["NON_ECR"] >= 0.95
    )
    
    if global_score >= 0.85 and all_passed:
        return True, "Verified – Eligible for passport application"
    elif global_score >= 0.70:
        return False, "Minor discrepancies – Manual review recommended"
    else:
        return False, "Verification failed – Not eligible"
