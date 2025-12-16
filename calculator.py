def cal_tax_now (tntt: float) -> float:
    if tntt <= 0: 
        return 0.0
    tax_brackets = [
        (5_000_000, 0.05, 0),
        (10_000_000, 0.10, 250_000),
        (18_000_000, 0.15, 750_000),
        (32_000_000, 0.20, 1_650_000),
        (52_000_000, 0.25, 3_250_000),
        (80_000_000, 0.30, 5_850_000),
    ]

    tax = 0.0
    for limit, rate, deduction in tax_brackets:
        if tntt <= limit:
            tax = tntt * rate - deduction
            return max(0, tax)
    tax = tntt * 0.35 - 9_850_000
    return max(0, tax)

def calculate_tax_2026(tntt: float) -> float:
    if tntt <= 0:
        return 0.0
    tax_bracket_2026 = [
        (10_000_000, 0.05, 0),
        (30_000_000, 0.10, 500_000),
        (60_000_000, 0.20, 3_500_000),
        (100_000_000, 0.30, 9_500_000),
    ]

    tax = 0.0
    for limit, rate, deduction in tax_bracket_2026:
        if tntt <= limit:
            tax = tntt * rate - deduction
            return max(0, tax)
        
    tax = tntt * 0.35 - 14_500_000
    return max(0, tax)

def calculate_gross_to_net (
        gross_salary: float,
        insurance_base: float,
        num_dependents: int = 0,
        tax_method: str = 'hien_hanh') -> dict:
    BH_rate = 0.105  
    thue_tncn = 0.0
    tntt = 0.0

    bh_contribution = insurance_base * BH_rate
    tnct = gross_salary - bh_contribution
    if tax_method == '2026':
        GTGC = 15_500_000
        GTGC_DEPENDENTS = 6_200_000
        total_GTGC = GTGC + num_dependents*GTGC_DEPENDENTS
        tntt = max(0, tnct - total_GTGC)
        thue_tncn = calculate_tax_2026(tntt)
    elif tax_method == 'toan_phan':
        if tnct >= 2_000_000:
            thue_tncn = tnct * 0.1
        else:
            thue_tncn = 0
    else:
        GTGC =  11_000_000
        GTGC_DEPENDENTS = 4_400_000
        total_GTGC = GTGC + GTGC_DEPENDENTS*num_dependents
        tntt = max(0, tnct - total_GTGC)
        thue_tncn = cal_tax_now(tntt)
    
    net_salary = gross_salary - bh_contribution - thue_tncn

    return {
        "gross": round(gross_salary, 2),
        "bao hiem base": round(insurance_base, 2),
        "net": round(net_salary, 2),
        "bh": round(bh_contribution, 2),
        "tnct": round(tnct, 2),
        "tntt": round(tntt, 2),
        "thue_tncn": round(thue_tncn, 2),
        "tax_method_used": tax_method
    }
