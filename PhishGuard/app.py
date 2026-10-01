import logging, sqlite3
from datetime import datetime
from flask import Flask, render_template, request
import config
from src.feature_extraction import InvalidURLError
from src.prediction import analyze_url
import json

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

def db():
    config.DB.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(config.DB)
    c.execute("CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY, ts TEXT, url TEXT, verdict TEXT, cls TEXT, score INT, conf REAL)")
    return c

def stats():
    with db() as c:
        rows = c.execute("SELECT cls, COUNT(*) FROM scans GROUP BY cls").fetchall()
    d = dict(rows); acc = None
    if config.METRICS.exists():
        m = json.loads(config.METRICS.read_text()); acc = m["results"][m["best_model"]]["accuracy"]
    return {"total": sum(d.values()), "safe": d.get("safe", 0), "warn": d.get("warn", 0), "danger": d.get("danger", 0),
            "acc": None if acc is None else f"{acc*100:.1f}%"}

@app.route("/")
def index():
    return render_template("index.html", s=stats(), model_ready=config.MODEL.exists(), error=None)

@app.route("/scan", methods=["POST"])
def scan():
    url = request.form.get("url", "")
    try:
        r = analyze_url(url)
    except (InvalidURLError, FileNotFoundError) as e:
        return render_template("index.html", s=stats(), model_ready=config.MODEL.exists(), error=str(e)), 400
    except Exception:
        app.logger.exception("Analysis failed")
        return render_template("index.html", s=stats(), model_ready=True, error="Analysis failed. Please check the URL and try again."), 500
    with db() as c:
        c.execute("INSERT INTO scans(ts,url,verdict,cls,score,conf) VALUES(?,?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), r["url"][:300], r["verdict"], r["cls"], r["score"], r["confidence"]))
    return render_template("result.html", r=r)

@app.route("/history")
def history():
    with db() as c:
        rows = c.execute("SELECT ts,url,verdict,cls,score,conf FROM scans ORDER BY id DESC LIMIT 100").fetchall()
    return render_template("history.html", rows=rows)

@app.route("/insights")
def insights():
    m = json.loads(config.METRICS.read_text()) if config.METRICS.exists() else None
    return render_template("insights.html", m=m)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
