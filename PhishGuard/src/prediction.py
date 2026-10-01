import pandas as pd
from urllib.parse import urlparse
from src.feature_extraction import FEATURE_NAMES, extract_features, normalize_url, split_host
from src.model_utils import load_bundle
from src.risk_engine import assess
from src.explanation import feature_contributions
_bundle = None

def get_bundle():
    global _bundle
    if _bundle is None: _bundle = load_bundle()
    return _bundle

def analyze_url(url):
    """validate -> features (same code as training) -> ML -> risk -> explanation. Never fetches the URL."""
    b = get_bundle(); url = normalize_url(url)
    feats = extract_features(url); vec = list(feats.values())
    prob = float(b["model"].predict_proba(pd.DataFrame([vec], columns=FEATURE_NAMES))[0][1]); r = assess(prob, feats); p = urlparse(url); conf = max(prob, 1-prob)
    return {"url": url, "domain": p.hostname, "protocol": p.scheme, "tld": split_host(p.hostname)[2], "prob": round(prob*100,1),
            "ml_label": "Phishing" if prob>=0.5 else "Legitimate", "confidence": round(conf*100,1),
            "confidence_level": "HIGH" if conf>=.9 else "MEDIUM" if conf>=.7 else "LOW",
            "features": feats, "model_name": b["model_name"], "contrib": feature_contributions(b, vec), **r}
