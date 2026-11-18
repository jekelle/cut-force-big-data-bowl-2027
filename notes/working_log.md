> Working log kept during the build, in order. Numbers here are the ones at each date and were superseded as the work went on. The writeup and the notebook carry the final figures.

# BDB 2027 working notes (internal, not the writeup)

## Pipeline done
- Data downloaded + unzipped on Mac: ~/Downloads/bdb2027/
- Rookie WR frames pulled from game tracking (2023 to 2025): ~/Downloads/bdb2027/reduced/
- Combine: 107 WRs, 10 route drills with a real break
- NFL: 55,659 breaking routes (OUT, IN, POST, CORNER, CROSS, SLANT, HITCH) from 104 rookie WRs

## Metric: Cut Force
Peak lateral (centripetal) acceleration at the break, in g. speed x turn rate, smoothed, top 3 frames around the break.

## What holds up so far
- Stable trait: cross-drill split-half reliability 0.56 (decel, re-accel, speed kept: all under 0.21, dropped)
- Transfers: Combine Cut Force vs NFL Cut Force (route + entry speed adjusted) r = 0.22 (p = 0.02), n = 105. Corrected for reliability (Combine 0.56, NFL 0.65) about 0.36
- New info: Cut Force basically uncorrelated with 3-cone (-0.01), shuttle (-0.03), 40 (0.03), 10-yd split (0.06), weight (-0.05), NGS athleticism (0.05)

## Not settled yet
- Link to on-field value. Raw separation at pass forward is driven by size/role (weight r = -0.44), so it needs alignment (slot vs wide) and role controls before Cut Force can be judged against it
- Next: alignment from snap position, separation measured just after the break, EPA per target, Bayesian hierarchical model (player random effects)

## Round 2 (Oct 10)
- Alignment from snap position: outside = within 13 yd of sideline, slot = further in (bimodal, clean split)
- Separation at pass forward: Cut Force does NOT predict it, even with slot + route + coverage + cushion controls. Size dominates (weight r = -0.44 to -0.51). Dropping separation as the main outcome
- Targets per route run (TPRR, players with 100+ routes, n = 71 to 76):
  - Combine Cut Force r = +0.29 (p = 0.01). 40, weight, NGS athleticism all near 0. Draft pick r = -0.25
  - With draft pick, slot share, weight, 40 controls: +0.007 TPRR per SD (p = 0.11), bootstrap 95% CI -0.003 to 0.017, incremental R2 0.027
  - Thirds: low 16.1%, mid 18.0%, high 18.9% TPRR
- EPA per target r = +0.18 (p = 0.11), YAC over expected r = +0.20 (p = 0.09)
- Read: real, new, transferable trait; production link suggestive, not proven at n = 71
- Next: play-level hierarchical model (target ~ player Cut Force + route + slot + coverage + down/dist + draft capital, player random effects) for more power; then charts + draft writeup

## Round 3 (Oct 10): research done, draft built
- Combine rows: BALL entity carries the WR's nfl_id. Now filtered to PLAYER only (numbers didn't change, but it's explicit now). Reps standardized within drill before averaging
- Combine reliability 0.56. Transfer r = 0.26 (p = 0.008), game reliability 0.52 (odd/even), corrected r about 0.47
- Play-level Bayesian hierarchical logit (PyMC), 42,806 routes, player random intercepts, latent Cut Force w/ measurement error:
  +1.4 pts TPRR per SD (95% CrI 0.2 to 2.6), P(>0) = 0.99, about 7 targets per 500 routes. Cluster-robust GLM check OR 1.11 (p = 0.078)
- EPA/target +0.072 (p = 0.051), YACOE +0.27 yd/catch (p = 0.015), snaps/season +0.32 log (p = 0.081, draft slot controlled)
- Separation: no (slightly negative, p = 0.05). Effect not specific to breaking routes (interaction p = 0.26)
- Sensitivity: first-break-only versions keep the TPRR link (r 0.27 to 0.32)
- Hook: Puka Nacua (pick 177) = #2 Cut Force in the sample, All-Pro
- Files: submission/writeup.md (1,944 words, voice checked), 4 figs + 2 tables, cut_force_bdb2027.ipynb (runs end to end, ~6 min)
- To do before Jan 6: Jay edits writeup, upload notebook to Kaggle + make public, attach writeup, submit (Jay's OK needed)

## Oct 20: historical Combine context (filed, NOT in the writeup)
- Added analysis/nflverse_combine_2000_2026.csv (nflverse combine release, PFR-sourced, 2000 to 2026, 8,968 rows) and analysis/combine_context.py
- Kaggle WR classes 2023 to 2025 vs WR pool 2000 to 2022: 40 4.47 vs 4.51 (35th pct), vertical 36.6 vs 35.3 (69th), broad 125.4 vs 120.8 (81st), weight 197 vs 202
- Read: the Cut Force sample is a lighter, more explosive cohort than the historical WR pool. Candidate 40-word limitation if main-body words ever free up. Writeup untouched (at 2,000 cap, submitted Oct 20)
