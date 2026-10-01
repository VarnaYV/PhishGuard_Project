"""Risk = 0.6*ML probability(0-100) + 0.4*heuristic score(0-100, capped). Levels: 0-30 low, 31-60 medium, 61-80 high, 81-100 critical."""
W_ML, W_HEUR = 0.6, 0.4
RULES = [  # (key, risk-factor label, pass label, weight, predicate)
 ("ip","IP-based hostname","No IP-based hostname",30,lambda f:f["is_ip_host"]),
 ("http","HTTP instead of HTTPS","HTTPS enabled",15,lambda f:not f["is_https"]),
 ("tld","Suspicious TLD","TLD not on suspicious list",15,lambda f:f["suspicious_tld"]),
 ("kw","Suspicious keyword combination (2+)","No suspicious keyword combination",20,lambda f:f["keyword_count"]>=2),
 ("sub","Multiple subdomains (3+)","Normal subdomain count",15,lambda f:f["num_subdomains"]>=3),
 ("len","Excessive URL length (>75)","Normal URL length",10,lambda f:f["url_length"]>75),
 ("at","'@' character in URL","No '@' in URL",15,lambda f:f["has_at"]),
 ("hy","Many hyphens in domain (2+)","Normal domain structure",10,lambda f:f["domain_hyphens"]>=2),
 ("short","URL shortener (destination hidden)","Not a known shortener",10,lambda f:f["is_shortener"]),
 ("spec","Abnormal special characters","Normal special-character usage",5,lambda f:f["num_special_chars"]>15),
]

def level(s):
    return ("LOW RISK","safe") if s<=30 else ("MEDIUM RISK","warn") if s<=60 else ("HIGH RISK","danger") if s<=80 else ("CRITICAL RISK","danger")

def assess(prob, f):
    hits = [(k,l,w) for k,l,_,w,p in RULES if p(f)]; h = min(100, sum(w for *_,w in hits))
    score = round(W_ML*prob*100 + W_HEUR*h); lvl, cls = level(score)
    verdict = "LIKELY LEGITIMATE" if score<=30 else "POTENTIALLY SUSPICIOUS" if score<=60 else "LIKELY PHISHING"
    keys = {k for k,_,_ in hits}
    return {"score":score,"level":lvl,"cls":cls,"verdict":verdict,"heuristic":h,"risk_factors":[l for _,l,_ in hits],
            "checks":[{"name":(l if k in keys else pl),"pass":k not in keys} for k,l,pl,_,_ in RULES],
            "disagreement":abs(prob*100-h)>40}
