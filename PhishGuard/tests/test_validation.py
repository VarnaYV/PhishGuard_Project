import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.risk_engine import assess, level
def test_levels():
    assert level(30)[0] == "LOW RISK" and level(31)[0] == "MEDIUM RISK" and level(61)[0] == "HIGH RISK" and level(81)[0] == "CRITICAL RISK"
def test_disagreement_flag():
    from src.feature_extraction import extract_features
    r = assess(0.95, extract_features("https://github.com"))
    assert r["disagreement"] is True and 0 <= r["score"] <= 100
