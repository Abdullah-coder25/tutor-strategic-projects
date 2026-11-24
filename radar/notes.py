"""Turn a flagged site into the note an account executive would get.

Default is a plain template so the repo runs with no keys. With --llm and an
ANTHROPIC_API_KEY set, the same facts go to Claude to write the note instead.
The model only sees the numbers below; it is told not to add any.
"""
import json, os

LABELS = {
    "utilization": "runs past its booked hours",
    "overtime_weeks": "has gone over its booked shift most weeks",
    "avg_uptime": "has been reliable",
    "assist_drop": "is needing remote help less often",
    "changeovers": "handles frequent SKU changeovers",
    "similar_lines": "sits next to similar lines with no robot",
    "open_sites": "belongs to a customer with other sites and no robots there",
}


def facts(r):
    return {
        "site": r["site_id"], "account": r["account_name"], "industry": r["industry"], "task": r["task"],
        "score": r["score"],
        "hours_worked_vs_booked": f"{r['utilization']:.0%}",
        "weeks_over_booked_shift": f"{int(r['overtime_weeks'])} of 8",
        "uptime": f"{r['avg_uptime']:.1%}",
        "remote_assist_change_pts": round(-100 * (r["assist_drop"] or 0), 1),
        "similar_lines_without_robot": r["similar_lines"],
        "other_sites_without_robots": r["open_sites"],
        "top_drivers": [LABELS[k] for k, _ in sorted(r["contributions"].items(), key=lambda x: -x[1])[:2]],
    }


def template_note(f):
    ask = ("a second robot on this line" if f["similar_lines_without_robot"] == 0
           else f"a robot on one of the {f['similar_lines_without_robot']} similar lines nearby")
    extra = (f" The account also runs {f['other_sites_without_robots']} other site(s) without robots, worth a question on the call."
             if f["other_sites_without_robots"] else "")
    return (f"{f['account']} ({f['task'].lower()}): worked {f['hours_worked_vs_booked']} of booked hours, "
            f"over the booked shift {f['weeks_over_booked_shift']} weeks, uptime {f['uptime']}, "
            f"remote assists {f['remote_assist_change_pts']:+} pts over 8 weeks. "
            f"Mainly flagged because it {f['top_drivers'][0]} and {f['top_drivers'][1]}. "
            f"Suggested ask: {ask}.{extra}")


def llm_note(f):
    import anthropic  # optional dependency
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=200,
        messages=[{"role": "user", "content":
                   "Write a 2-3 sentence note to an account executive suggesting an expansion conversation. "
                   "Use only these facts, add no numbers of your own, no em dashes:\n" + json.dumps(f)}])
    return msg.content[0].text.strip()


def write_notes(rows, use_llm=False):
    out = []
    for r in rows:
        f = facts(r)
        f["note"] = llm_note(f) if use_llm and os.environ.get("ANTHROPIC_API_KEY") else template_note(f)
        out.append(f)
    return out
