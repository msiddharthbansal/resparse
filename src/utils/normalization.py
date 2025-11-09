def normalize_jif(jif: float, max_jif: float = 100.0) -> float:
    return min (jif / max_jif, 1.0)

def calculate_recency_score(publication_year: int, current_year: int = 2025) -> float:
    age = current_year - publication_year
    
    if age <= 0:
        return 1.0
    elif age == 1:
        return 0.9
    elif age == 2:
        return 0.7
    elif age == 3:
        return 0.5
    elif age <= 5:
        return 0.3
    else:
        return 0.1