"""Generate a SYNTHETIC robot fleet so the pipeline can run end to end.

Nothing here is Tutor data. Account names are invented. The generator hides a
"readiness" value per site that makes some sites more likely to expand, and the
observable signals are noisy reflections of it. SIGNAL controls how much
readiness actually drives expansion. At SIGNAL = 0 expansions are random and the
backtest should find nothing, which is the check that the method isn't just
finding what it was told to find.
"""
import argparse, csv, os, random, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

INDUSTRIES = ["Contract packager", "Cosmetics co-man", "Snack maker", "3PL", "Beverage co-packer", "Household goods"]
TASKS = ["Palletizing", "Depalletizing", "Case picking", "Kitting", "Pack-out"]


def build(n_accounts=40, weeks=104, signal=0.8, seed=7):
    rnd = random.Random(seed)
    accounts, sites, activity, expansions = [], [], [], []
    site_id = 0
    for a in range(1, n_accounts + 1):
        acct = f"A{a:02d}"
        n_sites_total = rnd.choice([1, 1, 2, 2, 3, 4, 6])
        accounts.append({"account_id": acct, "account_name": f"Synthetic Account {a:02d}",
                         "industry": rnd.choice(INDUSTRIES), "sites_total": n_sites_total})
        for s in range(rnd.randint(1, min(2, n_sites_total))):
            site_id += 1
            sid = f"S{site_id:03d}"
            sites.append({"site_id": sid, "account_id": acct, "task": rnd.choice(TASKS),
                          "robots_start": rnd.choice([1, 1, 1, 2, 3]),
                          "similar_lines_without_robot": rnd.choice([0, 0, 1, 1, 2, 3, 4]),
                          "scheduled_hours_per_week": rnd.choice([40, 80, 120])})
    for site in sites:
        readiness = rnd.random()
        robots = site["robots_start"]
        assist = rnd.uniform(0.25, 0.6)
        last_exp = -99
        for w in range(1, weeks + 1):
            readiness = min(1, max(0, readiness + rnd.gauss(0.01, 0.05)))
            sched = site["scheduled_hours_per_week"] * robots
            util = min(1.35, max(0.3, 0.55 + 0.6 * readiness + rnd.gauss(0, 0.12)))
            billed = round(sched * util, 1)
            uptime = round(min(0.999, max(0.85, 0.93 + 0.06 * readiness + rnd.gauss(0, 0.02))), 3)
            assist = max(0.03, assist - 0.001 - 0.003 * readiness + rnd.gauss(0, 0.008))
            changeovers = max(0, int(rnd.gauss(6 + 6 * readiness, 3)))
            activity.append({"site_id": site["site_id"], "week": w, "robots": robots,
                             "scheduled_hours": sched, "billed_hours": billed, "uptime": uptime,
                             "tutor_assist_share": round(assist, 3), "sku_changeovers": changeovers})
            drive = signal * (readiness * 2.2 + 0.4 * min(site["similar_lines_without_robot"], 3) / 3) + (1 - signal) * 1.2
            p = 1 / (1 + math.exp(-(drive - 2.3) * 3)) * 0.12
            if w - last_exp > 12 and w > 8 and rnd.random() < p:
                robots += 1
                last_exp = w
                readiness *= 0.5
                expansions.append({"site_id": site["site_id"], "week": w, "robots_added": 1})
    return accounts, sites, activity, expansions


def write(rows, name):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", type=float, default=0.8, help="0 = expansions are random, 1 = driven by readiness")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    accounts, sites, activity, expansions = build(signal=a.signal, seed=a.seed)
    for rows, name in [(accounts, "accounts.csv"), (sites, "sites.csv"),
                       (activity, "weekly_activity.csv"), (expansions, "expansions.csv")]:
        write(rows, name)
    print(f"{len(accounts)} accounts, {len(sites)} sites, {len(activity)} site-weeks, {len(expansions)} expansions (signal={a.signal})")
