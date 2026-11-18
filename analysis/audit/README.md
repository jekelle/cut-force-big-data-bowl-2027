# Data audit, 5 November 2026

Scripts that reran the notebook code on this Mac to check every number in the Kaggle writeup.

- extract.py: copies the receiver and defensive back rows of each game_tracking file into a pickle (run once per season: python3 extract.py 2023).
- stage.py: runs the notebook (v19) in stages from those pickles. g1 = sections 1 to 4, g2 = 5, 7, 8 and 10, g3 = 6b leave-one-out, g4 = 12 load, g5 = 13 DBs, g6 = 11 trench plus the peak-definition correlations, g7 = the joint phase model with the NFL season.
- stage20.py: the same against v20 (t20 and t20b test the changed cells).
- season_fix.py: refits the clustered logits with the NFL season from games.csv instead of the game_id year.

The pickles and state files stay in the shell's scratch folder, not here. Results are in REVIEW_CHECKLIST.md (5 November) and in the vault note Rounds/2026-11-05 Cut Force data audit.md.
