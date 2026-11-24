"""Does the score see expansions coming? Replay history and check.

At every 2nd week, score every site using only data up to that week, then look
at which sites actually added a robot in the next `horizon` weeks. A useful
score ranks those sites near the top. Sites that just expanded are skipped,
since they are not candidates.

Also runs the simple version of the test from the pitch: compare the signals of
sites in the 8 weeks before they expanded with sites that did not expand.
"""
import json, os, random
from score import load_db, site_scores, CONFIG, FEATURES

HORIZON = CONFIG["horizon_weeks"]


def auc(pos, neg):
    """Chance a random expanding site outranks a random non-expanding one."""
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def run(db, top_k=10):
    last = db.execute("SELECT MAX(week) FROM weekly_activity").fetchone()[0]
    exps = [dict(r) for r in db.execute("SELECT site_id, week FROM expansions")]
    pos_scores, neg_scores, hits, flagged, snapshots = [], [], 0, 0, 0
    for as_of in range(16, last - HORIZON + 1):
        future = {e["site_id"] for e in exps if as_of < e["week"] <= as_of + HORIZON}
        recent = {e["site_id"] for e in exps if as_of - 12 < e["week"] <= as_of}
        ranked = [r for r in site_scores(db, as_of) if r["site_id"] not in recent]
        for r in ranked:
            (pos_scores if r["site_id"] in future else neg_scores).append(r["score"])
        top = ranked[:top_k]
        hits += sum(r["site_id"] in future for r in top)
        flagged += len(top)
        snapshots += 1
    base = len(pos_scores) / max(1, len(pos_scores) + len(neg_scores))
    precision = hits / max(1, flagged)

    # The 10 vs 10 comparison
    rnd = random.Random(1)
    expanded = [e for e in exps if e["week"] > 16][:10]
    before = [next(r for r in site_scores(db, e["week"] - 1) if r["site_id"] == e["site_id"]) for e in expanded]
    exp_sites = {e["site_id"] for e in exps}
    never = [s for s in [r["site_id"] for r in db.execute("SELECT site_id FROM sites")] if s not in exp_sites]
    control_sites = rnd.sample(never, min(10, len(never)))
    control = []
    for s in control_sites:
        wk = rnd.randint(16, last)
        control.append(next(r for r in site_scores(db, wk) if r["site_id"] == s))
    def mean(rows, f): return round(sum(float(r[f] or 0) for r in rows) / max(1, len(rows)), 3 if f in ('utilization','avg_uptime','assist_drop') else 1)
    comparison = {f: {"expanded": mean(before, f), "did_not": mean(control, f)} for f in FEATURES + ["score"]}

    return {"snapshots": snapshots, "horizon_weeks": HORIZON, "top_k": top_k,
            "auc": round(auc(pos_scores, neg_scores), 3) if pos_scores else None,
            "base_rate": round(base, 3), "precision_at_k": round(precision, 3),
            "lift": round(precision / base, 2) if base else None,
            "n_expansions_in_window": len(pos_scores),
            "ten_vs_ten": comparison, "n_expanded_compared": len(before), "n_control": len(control)}


if __name__ == "__main__":
    print(json.dumps(run(load_db()), indent=2))
