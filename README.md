# Expansion Radar

A prototype for Tutor Intelligence: use the robot fleet's own data to tell account owners which customer sites are ready for another robot, with a drafted note for each and a backtest that checks whether the signals actually came before past expansions.

**Live page:** https://abdullah-coder25.github.io/tutor-strategic-projects/

> **All fleet data here is synthetic.** Account names are invented and the numbers come from `radar/generate_synthetic.py`. The results show the pipeline works end to end. They say nothing about what predicts expansion at Tutor; the backtest is how you'd find that out on real data.

## Also in this repo

Two more pieces for Tutor, served from the same GitHub Pages site:

- **[PACK EXPO Southeast 2027 campaign plan](https://abdullah-coder25.github.io/tutor-strategic-projects/packexpo/)** (`docs/packexpo/`): a ready-to-run plan for Atlanta, April 12 to 14, 2027, with a ProMat second stop. It covers 57 target accounts, pre-show emails, a three-day meeting grid, an on-floor playbook, a follow-up tracker with CSV export, budget math and sources.
- **[Workers' comp carrier partnership brief](https://abdullah-coder25.github.io/tutor-strategic-projects/carrier-partnership/)** (`docs/carrier-partnership/`): how carriers' loss-control teams could refer Tutor to the plants with the most hand lifting, while Tutor keeps the direct sale.

Contact names on these pages are public names and titles only; last names from Apollo's free search are masked.

## Why

Nearly a third of the organizations that received Tutor robots in the past 12 months were existing customers installing more ([The Robot Report, Nov 2026](https://www.therobotreport.com/?p=590098)). The robots already log the signals that tend to come before that, such as running past their booked hours, high uptime and fewer remote assists. Today that data likely sits with engineering while expansion runs through relationships.

## How it works

| Step | File | What it does |
|---|---|---|
| Tables | `radar/schema.sql` | Weekly fleet activity plus CRM fields (similar lines in the plant, other sites per account) |
| Signals | `radar/signals.sql` | Trailing 8-week signals per site as of any week, so history can be replayed |
| Score | `radar/score.py`, `radar/config.json` | Scales each signal 0 to 1, weights them, sums to 0 to 100 |
| Backtest | `radar/backtest.py` | Scores every site each week using only past data, then checks who expanded in the next 8 weeks |
| Notes | `radar/notes.py` | Writes the account owner's note. Template by default; `--llm` has Claude write it from the same numbers |
| Page | `radar/build_site.py` | Builds `docs/index.html` for GitHub Pages |

## Run it

```
python radar/run_all.py          # standard library only
python radar/run_all.py --llm    # optional: pip install anthropic, set ANTHROPIC_API_KEY
```

## Reading the backtest honestly

The same backtest also runs on control fleets where expansions are random. A score that looks good there too is fooling you. On the synthetic data, the score ranks expanding sites above others about 75% of the time (AUC 0.75) against about 54% on the random controls. Two signals (remote-assist drop, other open sites) don't separate expanders in this data, which is the kind of finding that would change the weights.

## With real data, I'd

1. Run the 10-site comparison on real sites that did and didn't expand. If no signal separates them, stop.
2. If some do, refit the weights on the full history and keep only what holds up in later months.
3. Pilot with two account owners for a quarter and count conversations, quotes and robots added from flagged sites.
