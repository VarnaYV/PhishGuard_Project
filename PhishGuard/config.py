from pathlib import Path
BASE = Path(__file__).resolve().parent
DATASET = BASE / "dataset" / "sample_dataset.csv"
MODEL = BASE / "models" / "phishguard_model.joblib"
METRICS = BASE / "models" / "metrics.json"
DB = BASE / "reports" / "history.db"
URL_COL, LABEL_COL = "url", "label"   # change if your dataset uses other column names
