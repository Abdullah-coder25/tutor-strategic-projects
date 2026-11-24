"""Load the tables into SQLite, compute each site's signals, and score them 0 to 100."""
import csv, json, os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = json.load(open(os.path.join(HERE, "config.json")))
SIGNALS_SQL = open(os.path.join(HERE, "signals.sql")).read()
FEATURES = list(CONFIG["weights"].keys())


def load_db(data_dir=os.path.join(ROOT, "data")):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(open(os.path.join(HERE, "schema.sql")).read())
    for table in ["accounts", "sites", "weekly_activity", "expansions"]:
        path = os.path.join(data_dir, "weekly_activity.csv" if table == "weekly_activity" else f"{table}.csv")
        rows = list(csv.DictReader(open(path)))
        if not rows:
            continue
        cols = list(rows[0].keys())
        db.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                       [tuple(r[c] for c in cols) for r in rows])
    return db


def normalize(name, value):
    lo, hi = CONFIG["caps"][name]
    if value is None:
        return 0.0
    return max(0.0, min(1.0, (float(value) - lo) / (hi - lo)))


def score_rows(rows, weights=None):
    weights = weights or CONFIG["weights"]
    total = sum(weights.values())
    out = []
    for r in rows:
        d = dict(r)
        parts = {f: normalize(f, d[f]) for f in FEATURES}
        d["score"] = round(100 * sum(parts[f] * weights[f] for f in FEATURES) / total, 1)
        d["contributions"] = {f: round(100 * parts[f] * weights[f] / total, 1) for f in FEATURES}
        out.append(d)
    return sorted(out, key=lambda x: -x["score"])


def site_scores(db, as_of):
    return score_rows(db.execute(SIGNALS_SQL, {"as_of": as_of}).fetchall())


if __name__ == "__main__":
    db = load_db()
    last = db.execute("SELECT MAX(week) FROM weekly_activity").fetchone()[0]
    for r in site_scores(db, last)[:10]:
        print(f"{r['site_id']}  {r['account_name']:<22} {r['task']:<14} score {r['score']}")
