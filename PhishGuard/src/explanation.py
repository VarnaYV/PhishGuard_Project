import pandas as pd
from src.feature_extraction import FEATURE_NAMES

def feature_contributions(bundle, vec, top=6):
    """Model-agnostic explanation: change in P(phishing) when a feature is replaced by its training median."""
    m = bundle["model"]; base = m.predict_proba(pd.DataFrame([vec], columns=FEATURE_NAMES))[0][1]; out = []
    for i, n in enumerate(FEATURE_NAMES):
        v2 = list(vec); v2[i] = bundle["medians"][n]
        d = base - m.predict_proba(pd.DataFrame([v2], columns=FEATURE_NAMES))[0][1]
        if abs(d) > 0.005: out.append({"feature": n, "value": vec[i], "impact": round(float(d)*100, 1)})
    return sorted(out, key=lambda c: -abs(c["impact"]))[:top]
