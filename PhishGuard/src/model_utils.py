import json, logging, joblib, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
import config
from src.feature_extraction import FEATURE_NAMES
from src.preprocessing import load_dataset, build_matrix
log = logging.getLogger(__name__)

def get_models():
    models = {"Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
              "Decision Tree": DecisionTreeClassifier(max_depth=8, random_state=42),
              "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)}
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(n_estimators=200, max_depth=5, eval_metric="logloss", random_state=42)
    except ImportError: pass
    return models

def evaluate(model, X, y):
    pred = model.predict(X); prob = model.predict_proba(X)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0), "f1": f1_score(y, pred, zero_division=0),
            "roc_auc": roc_auc_score(y, prob) if len(set(y)) > 1 else None,
            "fpr": fp/(fp+tn) if fp+tn else 0.0, "fnr": fn/(fn+tp) if fn+tp else 0.0,
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]}

def split_data(X, y, seed=42):
    """Stratified split. URLs are de-duplicated in load_dataset, so no URL is in both train and test."""
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)

def train_and_save(path=config.DATASET):
    X, y = build_matrix(load_dataset(path))
    Xtr, Xte, ytr, yte = split_data(X, y)
    results, fitted = {}, {}
    for name, m in get_models().items():
        m.fit(Xtr, ytr); fitted[name] = m; results[name] = evaluate(m, Xte, yte)
    best = max(results, key=lambda n: (results[n]["f1"], results[n]["recall"], n == "Random Forest"))
    imp = dict(sorted(zip(FEATURE_NAMES, map(float, fitted["Random Forest"].feature_importances_)), key=lambda kv: -kv[1]))
    bundle = {"model": fitted[best], "model_name": best, "features": FEATURE_NAMES, "medians": Xtr.median().to_dict()}
    config.MODEL.parent.mkdir(exist_ok=True); joblib.dump(bundle, config.MODEL)
    config.METRICS.write_text(json.dumps({"best_model": best, "results": results, "feature_importance": imp,
                                          "n_train": len(Xtr), "n_test": len(Xte)}, indent=2))
    return results, best, imp

def load_bundle():
    if not config.MODEL.exists():
        raise FileNotFoundError("Model not trained yet. Please run: notebooks/PhishGuard_ML_Training.ipynb (or python train.py)")
    return joblib.load(config.MODEL)
