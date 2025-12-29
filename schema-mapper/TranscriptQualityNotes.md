biosdaddy@biosdaddy:~/git/llm-speaker/schema-mapper$ python3 transcript_quality_compare.py output/transcript_quality_local_v2_1766969894585.log output/transcript_quality_local_v3_1766970234517.log
Version summaries:
- v2
  Entries: 77
  Successes: 10
  Success rate: 0.1299
  Average likeness: 0.4760
  Median likeness: 0.5399
- v3
  Entries: 54
  Successes: 18
  Success rate: 0.3333
  Average likeness: 0.8017
  Median likeness: 0.8096

Comparison: v2 -> v3
  Matched talks: 54
  Compared talks (with likeness): 54
  Improved: 49  Regressed: 5  Unchanged: 0
  Success->Fail: 2  Fail->Success: 11
  Avg delta: 0.3026  Median delta: 0.1939
  Top regressions (limit 10):
    24769: 0.9618 -> 0.7080 (delta -0.2538) status succeeded -> failed
    24526: 0.9942 -> 0.7837 (delta -0.2105) status succeeded -> failed
    24778: 0.9947 -> 0.9045 (delta -0.0902) status succeeded -> succeeded
    26715: 0.6274 -> 0.5417 (delta -0.0857) status failed -> failed
    24795: 0.8583 -> 0.8538 (delta -0.0045) status failed -> failed
  Top improvements (limit 10):
    27035: 0.0490 -> 0.8692 (delta +0.8202) status failed -> failed
    25843: 0.0282 -> 0.8221 (delta +0.7939) status failed -> failed
    27034: 0.0262 -> 0.8079 (delta +0.7817) status failed -> failed
    27032: 0.0235 -> 0.7952 (delta +0.7717) status failed -> failed
    27303: 0.0280 -> 0.7941 (delta +0.7661) status failed -> failed
    26749: 0.0246 -> 0.7888 (delta +0.7642) status failed -> failed
    25433: 0.0189 -> 0.7651 (delta +0.7462) status failed -> failed
    25807: 0.0255 -> 0.7689 (delta +0.7434) status failed -> failed
    26771: 0.0226 -> 0.7185 (delta +0.6959) status failed -> failed
    27030: 0.0296 -> 0.7223 (delta +0.6927) status failed -> failed