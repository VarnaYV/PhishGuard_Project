"""Single source of truth for URL features (used by notebook, training and Flask)."""
import ipaddress, math, re
from collections import Counter
from urllib.parse import urlparse

KEYWORDS = ["login","verify","verification","account","secure","security","update","password","credential",
            "banking","wallet","payment","confirm","authentication","unlock","recovery","signin","bonus","free","urgent"]
SUSPICIOUS_TLDS = {"xyz","top","click","link","work","tk","ml","ga","cf","gq"}   # configurable
SHORTENERS = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd"}           # configurable
MAX_LEN = 2048
FEATURE_NAMES = ["url_length","hostname_length","path_length","query_length","fragment_length","num_dots","num_slashes",
    "num_hyphens","num_underscores","num_digits","num_special_chars","num_query_params","num_subdirs","num_subdomains",
    "has_at","has_double_slash_in_path","has_percent","has_equals","has_ampersand","is_ip_host","entropy","is_https",
    "suspicious_tld","domain_length","domain_has_digits","domain_hyphens","keyword_count","is_shortener",
    "nonstandard_port","digit_ratio"]

class InvalidURLError(ValueError):
    """Raised for user-facing URL validation problems."""

def normalize_url(url):
    if not isinstance(url, str) or not url.strip():
        raise InvalidURLError("Please enter a URL.")
    url = url.strip()
    if len(url) > MAX_LEN:
        raise InvalidURLError(f"URL is too long (max {MAX_LEN} characters).")
    if re.search(r"\s", url):
        raise InvalidURLError("URL must not contain spaces.")
    if "://" not in url:
        url = "http://" + url
    p = urlparse(url)
    if p.scheme.lower() not in ("http", "https"):
        raise InvalidURLError(f"Unsupported URL scheme '{p.scheme}'. Only http/https are analysed.")
    try:
        host = p.hostname; p.port
    except ValueError:
        raise InvalidURLError("Malformed URL.")
    if not host:
        raise InvalidURLError("URL has no valid hostname.")
    return url

def is_ip(host):
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False

def entropy(s):
    if not s: return 0.0
    n = len(s)
    return -sum(c/n*math.log2(c/n) for c in Counter(s).values())

def split_host(host):
    """Return (subdomain_count, domain, tld). Handles simple co.uk-style suffixes."""
    if is_ip(host): return 0, host, ""
    labels = host.lower().split(".")
    if len(labels) < 2: return 0, labels[0], ""
    tld = labels[-1]; k = 2
    if len(labels) >= 3 and len(tld) == 2 and labels[-2] in {"co","com","org","net","gov","ac","edu"}:
        tld = ".".join(labels[-2:]); k = 3
    return max(len(labels)-k, 0), labels[-k], tld

def extract_features(url):
    """Return ordered dict of features (no network access, URL is never visited)."""
    url = normalize_url(url)
    p = urlparse(url); host = (p.hostname or "").lower()
    n_sub, domain, tld = split_host(host)
    low = url.lower()
    f = {
        "url_length": len(url), "hostname_length": len(host), "path_length": len(p.path),
        "query_length": len(p.query), "fragment_length": len(p.fragment), "num_dots": url.count("."),
        "num_slashes": url.count("/"), "num_hyphens": url.count("-"), "num_underscores": url.count("_"),
        "num_digits": sum(c.isdigit() for c in url), "num_special_chars": len(re.findall(r"[^A-Za-z0-9]", url)),
        "num_query_params": len([q for q in p.query.split("&") if q]), "num_subdirs": len([s for s in p.path.split("/") if s]),
        "num_subdomains": n_sub, "has_at": int("@" in url), "has_double_slash_in_path": int("//" in url.split("://",1)[1]),
        "has_percent": int("%" in url), "has_equals": int("=" in url), "has_ampersand": int("&" in url),
        "is_ip_host": int(is_ip(host)), "entropy": round(entropy(url), 4), "is_https": int(p.scheme.lower() == "https"),
        "suspicious_tld": int(tld.split(".")[-1] in SUSPICIOUS_TLDS), "domain_length": len(domain),
        "domain_has_digits": int(any(c.isdigit() for c in domain)), "domain_hyphens": domain.count("-"),
        "keyword_count": sum(k in low for k in KEYWORDS), "is_shortener": int(host.replace("www.","") in SHORTENERS),
        "nonstandard_port": int(p.port not in (None, 80, 443)),
        "digit_ratio": round(sum(c.isdigit() for c in url)/len(url), 4),
    }
    return {k: f[k] for k in FEATURE_NAMES}

def features_vector(url):
    return list(extract_features(url).values())
