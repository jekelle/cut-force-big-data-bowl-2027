> Audit trail from the review rounds (dated). Kept for the record.

# BDB 2027 review checklist (Tue Oct 13 + Wed Oct 14)

Status as of Wed Oct 14 (writeup v-Oct14 pushed): SUBMITTED, Open Track, editable until Jan 6, 2027 6:59 PM EST.

## Live links
- Writeup: kaggle.com/competitions/nfl-big-data-bowl-2027/writeups/cut-force-the-combine-trait-the-stopwatch-misses
- Notebook (PRIVATE since Oct 13, Version 9 "Trench check + receivers to watch"): kaggle.com/code/jaykelley/cut-force-the-combine-trait-the-stopwatch-misses
- MUST switch notebook back to PUBLIC before Jan 6, 2027 6:59 PM EST (pass/fail rule). Reminder set for Sat Jan 2, 2027.
- Writeup is hidden from other competitors until the hackathon closes (Kaggle default)

## Tuesday: read for voice and football
- [ ] Read Kelley_CutForce_BDB2027_Review_Copy.pdf start to finish (7 pages)
- [ ] Mark any sentence that doesn't sound like me
- [ ] Football Applications: does the sideline paragraph read right? anything to add from Westfield work (no player names, no team data)
- [ ] Look at Figure 4 (Puka Nacua card): is it what a WR coach would want on one page?
- [x] Identity verification: no longer flagged on the competition page (Oct 13)

## Wednesday: numbers + polish
- [x] Notebook Version 5 confirmed (section 8b + card). Version 6 adds man vs zone (Oct 13)
- [x] (Oct 13, vs Version 7) Spot check: writeup numbers vs notebook outputs (targets +1.9 pts [0.5, 3.4], transfer r = 0.23, reliability 0.59, held-out log loss 0.4507 vs 0.4508, residual r = 0.33)
- [x] Figures: legend overlap fixed, Nacua labeled, darker gray text for contrast (Oct 13)
- [ ] Figures readable on phone and laptop (your eyes)
- [ ] Send edits to Claude, Claude updates Kaggle, re-confirm "Submitted!"

## Fixed already (do not undo)
- Combine scores standardized within drill AND draft class (2025 export differs)
- Game outcomes = regular season only
- BALL rows dropped from combine tracking
- Held-out check (leave one draft class out) reported honestly as the third limit
- 4 figures: Cut Force trace, transfer, targets, Nacua card
- Kaggle counter 2,178 incl. Appendix + References; main body about 1,880 (Appendix does not count per host)
- References section (APA) added Oct 13
- Player development application (3rd bullet) added Oct 13
- Gallery thumbnail crop fixed Oct 13
- Gold darkened to #B08400 (3.4:1 contrast), colorblind check passed (colorblind_check_card.png)
- Man vs zone: same effect in both (OR 1.13 each, interaction p = 0.72), written into limit 2
- Oct 14: judge-style review (6.4/10); fixed overclaims; added 4th limit (leverage: without Nacua +1.0 pts [-0.2, 2.3], P>0 = 0.94); measured-score effect (~7 targets)
- Oct 14: Appendix B (receivers to watch, incl. Mitchell 26.5%, low-CF early picks) and Appendix C (trench check: DL drill speed mostly = 40, r = -0.80)
- Main body about 1,985 words; Kaggle counter 2,916 incl. Appendices A-C + References
- Voice: no dashes, no semicolons, no first person, mean about 18 words per sentence
- Oct 14: Version 9 confirmed (trench numbers match Appendix C)
- Oct 14: Catapult data is NOT in the competition data (9 files, no wearables) and no public NFL Catapult set exists. Rebuilt wearable-style load (HSR, sprint, accel/decel efforts) from game tracking instead: notebook section 12, Appendix D, Figure 5. Local full run clean. Writeup pushed Oct 14 (Appendix D + Figure 5 live, "Submitted!" confirmed). Notebook Version 10 "Cut Force under load (wearable check)" ran clean (849s), section 12 matches Appendix D exactly, still private
- Oct 14: DB test (notebook section 13, Appendix E): DB Cut Force NOT a stable trait (Combine rel 0.28, game rel 0.13, transfer r = -0.05). 40 time predicts man separation (+0.28 yd per 0.1 s, p = 0.006). Mirror-lag reaction metric also unreliable (dev only, not in writeup). Pushed Oct 14: notebook Version 12 ran clean (1071s, all section 13 numbers match Appendix E, private); writeup updated with Appendix E, Submitted! confirmed. Version 11 was a separate run started from the editor
- Oct 20: item 38 sources pass LIVE after ChatGPT attack (3 of 4 taken: Johnston, force vs acceleration, Ward scope). Submitted! confirmed, 5 figures intact, main body 1,993 words. Backup writeup_pre_attack.md
- Oct 21: rules check (fewer than 10 tables+figures; was 11). Now 7 figs + 2 tables. Added Section 5 break phases (Figure 3 scorecard: decel, cut, accel, speed kept, DB), Appendix F equations (MathJax renders on Kaggle), Appendix G Tableau Combine context (Figure 7). Body 1,996 words. Writeup live, Submitted!. Notebook Version 15 'Break phases + equations' (section 14) started; local harness reproduced every phase number. Backups: writeup_pre_phases.md, cut_force_bdb2027_pre_phases.ipynb
- Oct 21: DB separation p corrected 0.42 -> 0.41 (notebook prints 0.415 from p just under 0.415; true 2-dp rounding is 0.41). Writeup text + Figure 3 image updated live, Submitted!

- Nov 2: Appendix H (ten break definitions + player-level leave-one-class-out, Tables H1 and H2) pushed to the writeup, plus one sentence in Section 7 limit 3. Submitted! confirmed. Backup writeup_pre_appH.md. Phase II course paper (TESM-S 501) carries the same analysis as Figure 6 and Table 3
- Nov 2: notebook v16 (cut_force_bdb2027_v16.ipynb in submission/) adds Section 15 (Appendix H code, dry-run matched every H1/H2 number) and Section 16 (Plotly interactive versions of Figures 2, 3, 4, 6, 7). NOT yet imported to Kaggle: the Chrome extension cannot upload from the Desktop folder. Jay imports it (File > Import Notebook > Browse) and runs Save & Run All, then confirms Section 15 output matches Appendix H (transfer column will use the regular-season game score, n = 82)
- Nov 2: Appendix H r-with-40 signs corrected live (integrated -0.07, duration -0.14, acceleration out -0.06)
- Nov 2: staff round on the Phase II paper and writeup. Perplexity verified all 12 references as real; took 2 fixes (Ward 2018 pages 2072-2084 per Crossref; DOIs added for PyMC, Brown 1910, Efron and Morris, Seabold and Perktold, Spearman 1904 and 1910). Grok football brain: 3 of 4 taken (value "at the break" softened to "much of", drill-conditions limitation added, separation null tied to perceived openness and QB trust). Gemini equation check errored twice, deferred; Claude checked E1 to E10 by hand against the notebook code, no faults. ChatGPT attacked the new sections, 4 of 4 taken. Writeup live and Submitted! with the reference fixes and the intro wording change
- Nov 2: DB separation p aligned to 0.41 in the paper (was 0.42)

- Nov 3: Kaggle notebook Version 16 ran clean (16m 49s, no tracebacks); five Plotly figures render in Section 16.
- Nov 3: Section 15 numbers differ from the old Appendix H (regular season only: transfer n = 82, targets n = 62, folds 28/19/15). Live Kaggle writeup Appendix H rewritten to match the notebook. Pooled held-out RMSE 4.59 base, 4.67 primary, 4.51 first break. Local writeup.md updated; old copy in writeup_pre_v16.md.
- OPEN: Phase II paper (Canvas Attempt 2), Figure 6, Table 3, companion page, and deck still carry the earlier numbers (105 receivers, folds 32/26/17, pooled 4.08/4.24/4.14).
- Nov 3 (later): paper, Figure 6, Table 3, companion page, and deck all rebuilt from the notebook v16 numbers. Canvas Attempt 3 submitted Nov 3 3:32pm. OPEN item above is closed.

- Nov 5: Section 16's Plotly charts were blank in Kaggle's saved viewer (Version 17). The viewer loads require.js, so the inline plotly.js (2.35.2) registered as an AMD module and every chart threw "Plotly is not defined". Reproduced locally with plotly.js 2.35.2 and require.js 2.1.10, fixed by hiding `define` while the bundle loads. Charts also drew at about 600 px inside an 870 px column, so they now refit once the page loads.
- Nov 5: v18 adds Section 17 (break replay: writes the animated Figure 1 GIF to /kaggle/working/fig1_cut_force.gif, plus a Play and slider version with a 0.5 g scale arrow), Section 18 (Cut Force explorer: every receiver against draft pick, 40 or 3-cone, color = targets per route, class filter), Section 19 (NFL route maps: the 4 highest and 3 lowest Combine Cut Force receivers with 300+ regular-season breaking routes, breaks colored by raw Cut Force, route-type legend). Kaggle Version 18 ran clean (11m 49s): all 8 Plotly charts render in the saved viewer, no console errors, transfer r = 0.23 (n = 82) unchanged, 4,208 routes for the 7 mapped receivers. v19 = the refit fix and two-line route-map titles: Kaggle Version 19 'Charts refit to full width, tidier titles' ran clean (19m 10s), all 8 charts render at the full column width, same numbers, still private.
- Nov 5: Writeup Figure 1 is now the animated GIF (same caption, last frame = the static figure, held 5 s, 0.6x speed, 124 frames, 0.55 MB). The code line now reads "Notebook Sections 16 to 19 are interactive: five figures with hover, a break replay, a receiver explorer, and NFL route maps." (21 words, was 23). Submitted! confirmed, 7 images. Backup writeup_pre_viz.md. ChatGPT attack: analysis/viz/viz_attack_record.md (taken: scale arrow, adjusted vs raw labels, directional corner labels; not taken: renaming force, a static copy beside the GIF).
- Still the pass/fail item: switch the notebook to PUBLIC before Jan 6, 2027 6:59 PM EST (Kaggle says the attached private notebook becomes public when the competition ends, but the rule asks for an attached public notebook).

- Nov 5 (evening): full data audit. The live writeup matched writeup.md line for line, and every number was checked against Kaggle Version 19 plus a rerun of the notebook code on this Mac (scripts in analysis/audit/). Fixed live, Update Submission, Submitted! confirmed, 7 figures load, equations render, main body 1,968 words (was 1,977):
  - 3-cone r -0.07 -> -0.06 (r = -0.0647)
  - leave-one-out odds ratio range 1.12 to 1.16 -> 1.15 (max 1.1549)
  - "Others above 1.5 SD sit at or below the 16.9% median" was false (Noel 17.8, Pearsall 17.7) -> "with NFL routes sit between 13.9% and 17.8%, around the 16.9% median"
  - "only the first-break variant lowers held-out error" was false (speed kept -0.03) -> "lowers it the most, but only in the 2023 class"; Appendix H the same
  - Figure 1 caption now gives each rep's Cut Force (0.71, 0.60), not the peak frame (0.61)
  - "most defenders" (Appendix E uses 90 rookie DBs); peak definitions "correlate with the primary" (0.94 to 0.99)
  - ChatGPT: "the Bayesian estimate is more certain because it corrects for drill noise" was wrong and is gone (the noise model rescales the slope, P(>0) is 0.99 on both scales)
  - Gemini (equations, the Nov 2 deferral is closed): theta in radians, Decel and Accel floored at zero, Cut Force window |t-k| <= 3, method of moments, one-reliability approximation
  - Grok: "likely because early picks receive volume for the rest of their profile"; fourth-quarter dip cannot separate fatigue from play calling
  - Perplexity: Nacua All-Pro now cites the AP's own story (Maaddi, 2026), not the WTOP copy; 2021 excluded from Appendix G (no Combine workouts)
- Nov 5: notebook Version 20 "NFL season control, extra printed checks" ran clean (16m 57s, 8 charts at full width, no tracebacks, still private). The logit's season dummies now use games.csv (the game_id year put January games in the next season): OR 1.13 unchanged, p 0.064 -> 0.062, without Nacua p 0.21 -> 0.20, breaking-route interaction 0.89 -> 0.88. Intro now says Figure 7 and Appendix G use public nflverse data. New prints: DL and OL drill counts (114, 121), load quintiles (top quintile 408 high speed yards), peak-variant r with the primary (0.98, 0.99, 0.94), replay legend (0.71, 0.60). Local copy cut_force_bdb2027_v20.ipynb. Backup writeup_pre_audit.md.
- OPEN for Phase III: the Phase II paper (Canvas Attempt 4), the companion page and the deck still carry 3-cone -0.07, leave-one-out 1.16, logit p 0.064 and 0.21, "only definition that lowers", "agree with each other" and "peaks at 0.60 g".
- Still the pass/fail item: switch the notebook to PUBLIC before Jan 6, 2027 6:59 PM EST (reminder Jan 2).
- Nov 5 (later): the OPEN for Phase III item above is closed. Phase II paper corrected (abstract, Figure 1 caption, 3-cone -0.06, p 0.062, Maaddi citation, Results and Phase III wording, leave-one-out 1.15) and resubmitted, Canvas Attempt 5 at 1:41 PM. A last read against the Version 20 run log then fixed Section 4 (the notebook runs in about 17 minutes, not six: 1016.8 s) and the Figure 6 caption ("Kaggle notebook", since it stays private until January): Canvas Attempt 6 at 1:51 PM, not late. ChatGPT attacked the paper wording: 1 of 3 taken (turn duration "does not transfer (r = -0.08)"). Companion page and deck refreshed (deck: 3-cone, p 0.062, Figure 1 caption, the ten-definition slide); the class PPTX files had none of the stale lines. The Phase II supporting zip now carries Version 20.

- Nov 12: v21 "Every figure interactive, all 107 receivers". Notebook: Section 16 opens with a table of where each writeup figure's interactive version is and adds interactive Figures 3, 6 and 7; new Section 20 has the Cut Force card and the highest Cut Force rep for all 107 receivers, picked from a menu. Kaggle Version 21 ran clean (19m 32s): 13 Plotly charts render in the saved viewer at full width, no tracebacks, same numbers (transfer r = 0.23, p = 0.041, n = 82; logit OR 1.133, p = 0.062; replay legend 0.71 and 0.60). Local copy cut_force_bdb2027_v21.ipynb; build scripts in analysis/viz/v21_*.py.
- Nov 12: writeup Figure 7 is now fig7_combine.png (two panels from public nflverse data, 2000 to 2026 without 2021), replacing the Tableau screenshot. New caption; Appendix G sentence now "In the stopwatch view, players group by position and size."; code line now "Every figure has an interactive version in the notebook (Sections 16 to 20), including a Cut Force card and a break replay for all 107 receivers." Update Submission, Submitted! confirmed, 7 figures load, main body about 1,985 words. Backup writeup_pre_v21.md. ChatGPT attack: 3 taken (n on the population labels, "highest Cut Force rep" for "sharpest", fuller Panel A caption and a softer Appendix G sentence), bundling the nflverse file not taken. Vault: Rounds/2026-11-12 Cut Force interactive v21.md.
- Nov 12: the notebook is PUBLIC (Share > Public > Save, about 18:25 UTC, on Jay's ask). A signed-out browser opened it and all 13 charts rendered; the writeup still shows Submitted! with the notebook attached. The pass/fail item above is closed. The Jan 2 reminder stays as a last check.

- Nov 18: Phase III prep. Notebook Version 22 "Big Data Bowl section map, discussion, limitations" saved with Save & Run All: markdown only (a contents table mapping the 20 notebook sections onto the 7 Big Data Bowl rubric sections, Section 1 Motivation after the title, divider headers before notebook 1, 7, 10 and 16, and Sections 5 Discussion, 6 Limitations and future work, 7 References and reproducibility at the end). No code changed. Local copy cut_force_bdb2027_v22.ipynb.
- Nov 18: one-page Professional Summary for Phase III (optional 5 pts): Kelley_PhaseIII_CutForce_Summary.pdf in School/TESM 501 Master/Phase 1-3 Project/Phase III/. Numbers from writeup.md (Version 20/21 audit).
- Phase III Canvas: due Fri Dec 11, 2026 5pm, 75 pts, submission types Text / Web URL / Upload, unlimited attempts. Plan: Upload the summary PDF and paste the public notebook URL in the comment. Individual work, so no contribution narrative.
- OPEN: confirm Version 22 ran clean (13 charts, no tracebacks) and the public page shows "Version 22 of 22" with the new section headers.

- Nov 18: Version 23 (plain-language axis labels and legends) and Version 24 (inline figures at 220 dpi) ran clean. Figures 2, 3 and 4 in writeup/figures are the Version 24 renders.
