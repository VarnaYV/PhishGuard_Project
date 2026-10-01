# Testing
`python -m pytest -q` runs feature, validation, risk-engine and prediction tests (10 sample URLs incl. IP, shortener, special-character, Unicode and invalid inputs). No URL is ever fetched. Prediction tests are skipped if no model is trained.
