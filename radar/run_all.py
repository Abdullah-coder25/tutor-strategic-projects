"""One command: generate the synthetic fleet, score today's sites, backtest, write notes, build the page.

    python radar/run_all.py            # template notes
    python radar/run_all.py --llm      # Claude-written notes (needs ANTHROPIC_API_KEY)
"""
import argparse, csv, json, os, tempfile
import generate_synthetic as gen
from score import load_db, site_scores, CONFIG
from backtest import run as backtest
from notes import write_notes
from build_site import build_page

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def save(rows_by_name, folder):
    os.makedirs(folder, exist_ok=True)
    for name, rows in rows_by_name.items():
        with open(os.path.join(folder, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)


def fleet(signal, seed, folder):
    acc, sites, act, exp = gen.build(signal=signal, seed=seed)
    save({"accounts.csv": acc, "sites.csv": sites, "weekly_activity.csv": act, "expansions.csv": exp}, folder)
    return load_db(folder)


def control_runs(seeds=(7, 11, 23, 31, 47)):
    """Average the backtest over several random-expansion fleets so one lucky draw can't mislead."""
    runs = [backtest(fleet(0.0, s, tempfile.mkdtemp())) for s in seeds]
    avg = lambda k: round(sum(r[k] for r in runs) / len(runs), 3)
    return {"auc": avg("auc"), "precision_at_k": avg("precision_at_k"), "lift": round(avg("lift"), 2), "n_fleets": len(seeds)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--llm", action="store_true"); a = ap.parse_args()

    db = fleet(0.8, 7, os.path.join(ROOT, "data"))
    last = db.execute("SELECT MAX(week) FROM weekly_activity").fetchone()[0]
    recent = {r[0] for r in db.execute("SELECT site_id FROM expansions WHERE week > ?", (last - 12,))}
    ranked = [r for r in site_scores(db, last) if r["site_id"] not in recent]
    flagged = ranked[:10]  # the weekly list: top 10, same as the backtest checks

    results = {
        "as_of_week": last,
        "n_sites": db.execute("SELECT COUNT(*) FROM sites").fetchone()[0],
        "n_accounts": db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0],
        "weights": CONFIG["weights"],
        "flagged": write_notes(flagged, use_llm=a.llm),
        "all_sites": [{k: r[k] for k in ("site_id", "account_name", "task", "score")} for r in ranked],
        "backtest": backtest(db),
        # Same test on a fleet where expansions are random. If the score "works" here too, it's fooling us.
        "control": control_runs(),
    }
    ws = os.path.join(ROOT, "data", "whitespace.json")
    results["whitespace"] = json.load(open(ws)) if os.path.exists(ws) else []
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    json.dump(results, open(os.path.join(ROOT, "docs", "results.json"), "w"), indent=2, default=float)
    build_page(results, os.path.join(ROOT, "docs", "index.html"))
    bt, c = results["backtest"], results["control"]
    print(f"{len(flagged)} sites flagged of {len(ranked)}. Backtest AUC {bt['auc']} (random-expansion control {c['auc']}), "
          f"top-{bt['top_k']} precision {bt['precision_at_k']} vs base rate {bt['base_rate']}.")
