"""Write docs/index.html: a static page (GitHub Pages) with the results embedded."""
import json

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Expansion Radar: a prototype for Tutor Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--ink:#16181D;--sub:#4A4F57;--mute:#5F6368;--line:#D9DCE1;--bg:#F7F8FA;--acc:#1F5BD8;--accbg:#EEF3FD;--warn:#8A5A00;--warnbg:#FFF6E0}
*{box-sizing:border-box}body{margin:0;font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--ink);background:#fff;line-height:1.5}
.wrap{max-width:1040px;margin:0 auto;padding:40px 24px 64px}
header .eyebrow{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:10px}
h1{font-family:'IBM Plex Sans Condensed',sans-serif;font-size:36px;line-height:1.1;margin:22px 0 10px}
h2{font-size:20px;margin:44px 0 6px}
p.lead{font-size:17px;color:#2B2E35;max-width:800px;margin:0}
.banner{margin:18px 0 0;background:var(--warnbg);color:var(--warn);border:1px solid #F0D9A0;border-radius:8px;padding:10px 14px;font-size:14px}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}
.step{border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:var(--bg)}
.step b{display:block;font-size:14px}.step span{font-size:13px;color:var(--sub)}
.step code{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--acc)}
.muted{color:var(--mute);font-size:14px;margin:0 0 12px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--mute);border-bottom:1.5px solid var(--ink);padding:8px 10px 8px 0}
td{border-bottom:1px solid var(--line);padding:9px 10px 9px 0;vertical-align:top}
tr.site{cursor:pointer}tr.site:hover td{background:var(--bg)}
.bar{height:8px;border-radius:4px;background:var(--line);width:140px;display:inline-block;vertical-align:middle;margin-right:8px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--acc)}
tr.detail td{background:var(--accbg);padding:14px 16px}
.note{font-size:14.5px;margin:0 0 10px}
.contrib{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:4px 18px;font-size:13px;color:var(--sub)}
.contrib div{display:flex;justify-content:space-between;gap:8px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:10px}
.card{border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.card .big{font-family:'IBM Plex Sans Condensed',sans-serif;font-size:30px;color:var(--acc)}
.card .small{font-size:13px;color:var(--sub)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.ws{border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:10px}
.ws h3{margin:0 0 4px;font-size:16px}
.ws ul{margin:6px 0 0;padding-left:18px;font-size:14px}
a{color:var(--acc)}
footer{margin-top:48px;border-top:1px solid var(--line);padding-top:12px;font-size:13px;color:var(--mute)}
@media(max-width:760px){.steps,.cards,.two{grid-template-columns:1fr}.bar{width:80px}}
</style></head><body><div class="wrap"><nav style="font-size:13px;margin:0 0 14px;color:#5F6368">Also for Tutor: <a href="packexpo/">PACK EXPO Southeast 2027 campaign plan</a> · <a href="carrier-partnership/">Workers' comp carrier partnership one-pager</a></nav>
<header>
<div class="eyebrow"><span>A prototype for Tutor Intelligence</span><span>Abdullah Usman · November 2026</span></div>
<h1>Expansion Radar: letting the fleet tell sellers where the next robot goes</h1>
<p class="lead">Nearly a third of the organizations that received Tutor robots in the past year were existing customers adding more. The robots already record the signals that come before that: hours worked past the booked shift, uptime, falling remote assists, idle lines next door. This prototype turns those signals into a weekly list for account owners, with a drafted note for each site and a backtest that checks whether the signals actually came before past expansions.</p>
<div class="banner"><b>All fleet data on this page is synthetic.</b> Account names are invented and the numbers come from a generator, so the results show that the pipeline works, not what predicts expansion at Tutor. The backtest is the tool for finding that out on real data.</div>
</header>

<h2>How it works</h2>
<div class="steps">
<div class="step"><b>1. Fleet + CRM tables</b><span>Weekly hours booked and worked, uptime, remote-assist share, changeovers; lines and sites per account.</span><br><code>schema.sql</code></div>
<div class="step"><b>2. Signals in SQL</b><span>Trailing 8-week window per site, computed as of any week so history can be replayed.</span><br><code>signals.sql</code></div>
<div class="step"><b>3. Score</b><span>Each signal scaled 0 to 1, weighted, summed to 0 to 100. Weights live in one config file.</span><br><code>score.py · config.json</code></div>
<div class="step"><b>4. Note for the AE</b><span>Template by default; Claude-written with <code>--llm</code>, using only the site's own numbers.</span><br><code>notes.py</code></div>
</div>

<h2>Sites flagged this week</h2>
<p class="muted" id="flagsub"></p>
<table><thead><tr><th>Site</th><th>Account</th><th>Task</th><th>Score</th></tr></thead><tbody id="flags"></tbody></table>

<h2>Does it see expansions coming? (backtest)</h2>
<p class="muted">Every week, every site is scored using only data up to that week, then checked against which sites added a robot in the next <span id="hz"></span> weeks. The same test runs on a control fleet where expansions are random: if the score looked good there too, it would be fooling us.</p>
<div class="cards" id="cards"></div>
<div class="two" style="margin-top:22px">
<div><h3 style="font-size:15px;margin:0 0 6px">The 10-site test from the pitch</h3>
<p class="muted">Signals in the 8 weeks before 10 expansions, against 10 sites that never expanded.</p>
<table><thead><tr><th>Signal</th><th>Before expanding</th><th>Never expanded</th></tr></thead><tbody id="ten"></tbody></table></div>
<div><h3 style="font-size:15px;margin:0 0 6px">What I'd do with real data</h3>
<ul style="font-size:14px;padding-left:18px;margin:6px 0">
<li>Run the 10-site comparison on real sites that did and didn't expand. If no signal separates them, stop here.</li>
<li>If some do, refit the weights on the full history and keep the ones that hold up in later months.</li>
<li>Pilot with two account owners for a quarter: how many flagged sites turned into a conversation, a quote, a second robot.</li>
<li>Track seller time saved, and hours added per flagged account, against accounts worked the usual way.</li>
</ul></div>
</div>

<div id="wswrap" style="display:none">
<h2>Where named customers run sites with no public Tutor deployment (real, public data)</h2>
<p class="muted">From public sources only, linked below. Tutor knows these accounts far better than any outside list; this is the kind of field the <code>open_sites</code> signal would pull from the CRM.</p>
<div id="ws"></div>
</div>

<footer>Code: <a href="https://github.com/Abdullah-coder25/tutor-expansion-radar">github.com/Abdullah-coder25/tutor-expansion-radar</a>. Run <code>python radar/run_all.py</code> to rebuild everything. Expansion share: The Robot Report, Nov 2026.</footer>
</div>
<script>
const R = __DATA__;
const pct = x => (x*100).toFixed(0)+'%';
document.getElementById('flagsub').textContent =
  `The 10 highest-scoring of ${R.n_sites} synthetic sites across ${R.n_accounts} accounts in week ${R.as_of_week}, leaving out sites that added a robot in the last 12 weeks. Click a row for the note and what drove the score.`;
const tb = document.getElementById('flags');
R.flagged.forEach((f,i) => {
  const tr = document.createElement('tr'); tr.className='site';
  tr.innerHTML = `<td>${f.site}</td><td>${f.account}</td><td>${f.task}</td><td><span class="bar"><i style="width:${f.score}%"></i></span>${f.score}</td>`;
  const d = document.createElement('tr'); d.className='detail'; d.style.display = i===0?'':'none';
  const s = R.all_sites.find(x=>x.site_id===f.site);
  d.innerHTML = `<td colspan="4"><p class="note">${f.note}</p><div class="contrib">
    <div><span>Hours worked vs booked</span><b>${f.hours_worked_vs_booked}</b></div>
    <div><span>Weeks over booked shift</span><b>${f.weeks_over_booked_shift}</b></div>
    <div><span>Uptime</span><b>${f.uptime}</b></div>
    <div><span>Remote assists, 8-wk change</span><b>${f.remote_assist_change_pts>0?'+':''}${f.remote_assist_change_pts} pts</b></div>
    <div><span>Similar lines, no robot</span><b>${f.similar_lines_without_robot}</b></div>
    <div><span>Other sites, no robots</span><b>${f.other_sites_without_robots}</b></div></div></td>`;
  tr.onclick = () => d.style.display = d.style.display ? '' : 'none';
  tb.appendChild(tr); tb.appendChild(d);
});
const B = R.backtest, C = R.control;
document.getElementById('hz').textContent = B.horizon_weeks;
document.getElementById('cards').innerHTML = `
 <div class="card"><div class="big">${B.auc}</div><div class="small">Chance an expanding site outranks a non-expanding one (AUC). 0.5 is a coin flip. Random-expansion control, average of ${C.n_fleets} fleets: <b>${C.auc}</b>.</div></div>
 <div class="card"><div class="big">${pct(B.precision_at_k)}</div><div class="small">Of the top ${B.top_k} flagged sites each week, share that expanded within ${B.horizon_weeks} weeks, vs <b>${pct(B.base_rate)}</b> for all sites.</div></div>
 <div class="card"><div class="big">${B.lift}x</div><div class="small">Lift over working sites at random, across ${B.snapshots} weekly snapshots. Control: <b>${C.lift}x</b>.</div></div>`;
const names = {utilization:'Hours worked vs booked',overtime_weeks:'Weeks over booked shift (of 8)',avg_uptime:'Uptime',assist_drop:'Drop in remote-assist share',changeovers:'SKU changeovers / week',similar_lines:'Similar lines, no robot',open_sites:'Other sites, no robots',score:'Score'};
const fmt = (k,v) => ['utilization','avg_uptime','assist_drop'].includes(k) ? (v*100).toFixed(1)+'%' : v;
document.getElementById('ten').innerHTML = Object.entries(B.ten_vs_ten).map(([k,v]) =>
  `<tr><td>${names[k]}</td><td>${fmt(k,v.expanded)}</td><td>${fmt(k,v.did_not)}</td></tr>`).join('');
if (R.whitespace && R.whitespace.length) {
  document.getElementById('wswrap').style.display='';
  document.getElementById('ws').innerHTML = R.whitespace.map(c => `<div class="ws"><h3>${c.customer}</h3>
   <div class="muted" style="margin:0">${c.summary||''}</div><ul>
   ${(c.tutor_known_sites||[]).map(s=>`<li><b>Tutor known:</b> ${s.site} (<a href="${s.url}">source</a>)</li>`).join('')}
   ${(c.other_sites||[]).map(s=>`<li>${s.site}${s.work?': '+s.work:''} (<a href="${s.url}">source</a>)</li>`).join('')}
   </ul></div>`).join('');
}
</script></body></html>"""


def build_page(results, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("__DATA__", json.dumps(results, default=float)))
