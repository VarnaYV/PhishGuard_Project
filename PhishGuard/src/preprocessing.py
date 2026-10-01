import numpy as np, pandas as pd
from pathlib import Path
from config import DATASET, URL_COL, LABEL_COL
from src.feature_extraction import features_vector, FEATURE_NAMES, InvalidURLError

def load_dataset(path=DATASET, url_col=URL_COL, label_col=LABEL_COL):
    """Load CSV -> columns url,label (0=legit,1=phishing); drop bad rows and duplicate URLs."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Dataset not found: {path}. See dataset/README.md")
    df = pd.read_csv(path).rename(columns={url_col: "url", label_col: "label"})[["url", "label"]].dropna()
    df["url"] = df["url"].astype(str).str.strip()
    return df.drop_duplicates(subset="url").reset_index(drop=True)

def build_matrix(df):
    rows, labels = [], []
    for u, y in zip(df["url"], df["label"]):
        try: rows.append(features_vector(u)); labels.append(int(y))
        except InvalidURLError: continue
    return pd.DataFrame(rows, columns=FEATURE_NAMES), np.array(labels)
