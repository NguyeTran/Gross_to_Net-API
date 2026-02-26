import pytest
from calculator import calculate_gross_to_net

# --- TEST PHƯƠNG PHÁP HIỆN HÀNH ---
def test_hien_hanh_no_dependents():
    """Lương 20tr, đóng BH trên 20tr, không người phụ thuộc"""
    # BH = 20tr * 10.5% = 2.1tr
    # TNCT = 20tr - 2.1tr = 17.9tr
    # TNTT = 17.9tr - 11tr (GTGC) = 6.9tr
    # Thuế = 5tr*5% + (6.9tr-5tr)*10% = 250k + 190k = 440k
    # Net = 20tr - 2.1tr - 440k = 17,460,000
    result = calculate_gross_to_net(20_000_000, 20_000_000, 0, 'hien_hanh')
    assert result['net'] == 17460000.0
    assert result['thue_tncn'] == 440000.0

def test_hien_hanh_with_dependents():
    """Lương 20tr, 2 người phụ thuộc"""
    # TNTT = 17.9tr - 11tr - (2 * 4.4tr) = 17.9tr - 19.8tr = -1.9tr -> TNTT = 0
    # Thuế = 0 -> Net = 20tr - 2.1tr = 17,900,000
    result = calculate_gross_to_net(20_000_000, 20_000_000, 2, 'hien_hanh')
    assert result['thue_tncn'] == 0
    assert result['net'] == 17900000.0

# --- TEST PHƯƠNG PHÁP 2026 ---
def test_2026_method():
    """Lương 30tr, đóng BH trên 30tr, 0 người phụ thuộc"""
    # BH = 3.15tr -> TNCT = 26.85tr
    # TNTT = 26.85tr - 15.5tr = 11.35tr
    # Thuế (Bậc 2): 11.35tr * 10% - 500k = 1.135tr - 500k = 635k
    result = calculate_gross_to_net(30_000_000, 30_000_000, 0, '2026')
    assert result['thue_tncn'] == 635000.0

# --- TEST THUẾ TOÀN PHẦN (10%) ---
def test_toan_phan_over_2m():
    """Thu nhập vãng lai trên 2tr"""
    # TNCT = 5tr -> Thuế = 5tr * 10% = 500k
    result = calculate_gross_to_net(5_000_000, 0, 0, 'toan_phan')
    assert result['thue_tncn'] == 500000.0

def test_toan_phan_under_2m():
    """Thu nhập vãng lai dưới 2tr -> Không thuế"""
    result = calculate_gross_to_net(1_500_000, 0, 0, 'toan_phan')
    assert result['thue_tncn'] == 0

# --- TEST CÁC TRƯỜNG HỢP BIÊN ---
def test_zero_salary():
    result = calculate_gross_to_net(0, 0, 0, 'hien_hanh')
    assert result['net'] == 0

def test_negative_salary():
    result = calculate_gross_to_net(-1000, 0, 0, 'hien_hanh')
    assert result['net'] <= 0