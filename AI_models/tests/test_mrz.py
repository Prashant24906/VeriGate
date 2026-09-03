import pytest
from app.ocr.mrz import calculate_mrz_check_digit, parse_td3_mrz


def test_mrz_check_digit_calculation():
    """Test 7-3-1 weighting check digit algorithm."""
    # Test passport number check digit
    # 'A1234567' -> (10*7 + 1*3 + 2*1 + 3*7 + 4*3 + 5*1 + 6*7 + 7*3) = 70+3+2+21+12+5+42+21 = 176 % 10 = 6
    assert calculate_mrz_check_digit("A1234567") == 6
    assert calculate_mrz_check_digit("990815") == 4


def test_parse_td3_mrz_valid():
    """Test parsing standard TD3 passport MRZ lines."""
    line1 = "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "A1234567<6IND9908150M3008150<<<<<<<<<<<<<<0"
    
    result = parse_td3_mrz(line1, line2)
    
    assert result["mrz_detected"] is True
    assert result["document_type"] == "P"
    assert result["issuing_country"] == "IND"
    assert result["full_name"] == "DOE JOHN"
    assert result["passport_number"] == "A1234567"
    assert result["nationality"] == "IND"
    assert result["dob"] == "15/08/1999"
    assert result["gender"] == "M"
    assert result["expiry"] == "15/08/2030"
    assert result["overall_mrz_valid"] is True
