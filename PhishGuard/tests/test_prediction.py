import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest, config
from src.prediction import analyze_url
pytestmark = pytest.mark.skipif(not config.MODEL.exists(), reason="Train the model first (python train.py)")
def test_output_structure():
    r = analyze_url("http://secure-login-paypal-verify.xyz/account")
    assert 0 <= r["score"] <= 100 and r["verdict"] and r["contrib"] is not None
def test_phishing_vs_legit_ordering():
    assert analyze_url("http://192.168.4.7/login/verify")["score"] > analyze_url("https://www.wikipedia.org/")["score"]
