from power_calculator_zimjing import power

def test_power():
    assert power(2, 3) == 8.0
    assert power(2.5, 2) == 6.25
    assert power(0, 0) == 1.0
    assert power(1, 0) == 1.0 