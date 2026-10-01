import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from src.feature_extraction import extract_features, is_ip, InvalidURLError, FEATURE_NAMES

URLS = ["https://www.google.com","https://github.com/user/repo","http://secure-login-paypal-verify.xyz/account","http://192.168.1.10/login",
        "https://bit.ly/abc123","http://a.b.c.d.example.top/x","https://example.com/a?b=1&c=2%20d","http://user@evil-example.tk/","https://münchen.de/straße","http://example.com:8080/"]
def test_all_urls_extract_in_order():
    for u in URLS: assert list(extract_features(u)) == FEATURE_NAMES
def test_ip_detection():
    assert extract_features("http://192.168.1.10/login")["is_ip_host"] == 1
    assert extract_features("http://example.com/192.168.1.10")["is_ip_host"] == 0 and is_ip("::1")
def test_https():
    assert extract_features("https://a.com")["is_https"] == 1 and extract_features("http://a.com")["is_https"] == 0
def test_keywords_and_tld():
    f = extract_features("http://secure-login-paypal-verify.xyz/account")
    assert f["keyword_count"] >= 3 and f["suspicious_tld"] == 1 and extract_features("https://github.com")["keyword_count"] == 0
def test_shortener_and_subdomains():
    assert extract_features("https://bit.ly/x")["is_shortener"] == 1
    assert extract_features("http://a.b.c.d.example.top/x")["num_subdomains"] == 4
def test_length_and_special():
    assert extract_features("http://user@x.tk/")["has_at"] == 1 and extract_features("https://a.com")["url_length"] == 13
def test_missing_scheme_ok():
    assert extract_features("example.com/login")["is_https"] == 0
@pytest.mark.parametrize("bad", ["", "   ", "ftp://x.com", "http://", "javascript:alert(1)", "http://a b.com", "http://" + "a"*3000 + ".com"])
def test_invalid(bad):
    with pytest.raises(InvalidURLError): extract_features(bad)
