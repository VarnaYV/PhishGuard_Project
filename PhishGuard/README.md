# PhishGuard — AI/ML-Based Phishing URL Detection, Risk Analysis & Explainable Cybersecurity System

A defensive, educational tool. It analyses URL **strings only** (never visits them) and reports LEGITIMATE / SUSPICIOUS / PHISHING with a risk score, model probability and an explanation. It cannot guarantee that any URL is safe.

## Features
30 lexical/structural/domain features · 4 models compared (LR, Decision Tree, Random Forest, XGBoost if installed) · stratified, de-duplicated split · explainable risk score · per-URL feature contributions · SQLite scan history · dark SOC-style dashboard · printable report (Print → Save as PDF).

## Architecture
`URL → validate/normalise → extract_features (shared by notebook & app) → model.predict_proba → risk_engine (rules) → explanation → result page`

**Risk score** = `0.6 × ML probability(0–100) + 0.4 × heuristic score(0–100, capped)`. Bands: 0–30 low, 31–60 medium, 61–80 high, 81–100 critical. If ML and heuristics disagree by >40 points, the page says so.
**Explanation** = rule-based risk factors + model-agnostic contributions (change in phishing probability when a feature is replaced by its training median).

## Folder structure
`app.py` (Flask) · `config.py` · `train.py` · `make_sample_dataset.py` · `src/` (feature_extraction, preprocessing, model_utils, prediction, risk_engine, explanation) · `templates/` · `static/` · `dataset/` · `models/` · `notebooks/` · `tests/` · `docs/`

## Installation (Windows PowerShell, Python 3.10+)
```powershell
cd PhishGuard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

## Jupyter / model training
```powershell
jupyter notebook
```
Open `notebooks/PhishGuard_ML_Training.ipynb` (or open it in VS Code with the Jupyter extension, select the `venv` kernel) and **Run All**. Cell 13 saves `models/phishguard_model.joblib` and `models/metrics.json`; restart Flask to load a new model. CLI alternative: `python train.py [path/to/dataset.csv]`.
If no model exists, the app shows: *"Model not trained yet. Please run: notebooks/PhishGuard_ML_Training.ipynb"*.

## Dataset
`dataset/sample_dataset.csv` is **synthetic** (see `dataset/README.md`). Replace it with a real dataset and adjust `URL_COL`/`LABEL_COL` in `config.py` (0 = legitimate, 1 = phishing).

## ML evaluation
The bundled model was trained on the synthetic sample, where the classes are easily separable, so it scores ~1.00 on its own test split. **This says nothing about real-world accuracy.** Train on a real dataset and read the figures from the notebook / *Model Insights* page. Precision, recall, F1, ROC-AUC, FPR, FNR and confusion matrices are all computed at run time. False negatives matter most in security because a missed phishing link can lead to credential theft.

## Testing
```powershell
python -m pytest -q
```

## Example URLs
`https://www.wikipedia.org/` · `http://192.168.4.7/login/verify` · `http://secure-login-paypal-verify.xyz/account` · `https://bit.ly/abc123` · `example.com/login` (all synthetic/harmless; never visited).

## Screenshots
_Add your screenshots here._

## Security considerations
No network requests are made for submitted URLs; input is validated (scheme, length, whitespace); stack traces are hidden; history stays in a local SQLite file.

## Limitations
URL-only analysis (no page content, WHOIS/DNS, reputation); the synthetic sample is not representative; brand-impersonation detection is keyword-based; shortened links hide destinations.

## Future improvements
Real datasets + cross-validation, SHAP, optional isolated DNS/WHOIS/SSL checks, character-level deep models, browser extension.

## Disclaimer
Results are statistical estimates, not guarantees. Use for education and defensive awareness only.
