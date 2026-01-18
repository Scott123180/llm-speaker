python3 transcript_quality_compare.py \ 
output/transcript_quality_local_v2_1766969894585.log \
output/transcript_quality_local_v3_1766970234517.log \
output/transcript_quality_local_v4_1767463895773.log 


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
- v4
  Entries: 37
  Successes: 11
  Success rate: 0.2973
  Average likeness: 0.8274
  Median likeness: 0.8303
- v5a
  python3 transcript_quality_parser.py output/transcript_quality_local_v5_1768050129262.log 
  Entries: 28
  Successes: 11
  Success rate: 0.3929
  Average likeness: 0.8424
  Median likeness: 0.8664

  Quality distribution (files per accuracy range):
  00-09% |  (0)
  10-19% |  (0)
  20-29% |  (0)
  30-39% | ##### (1)
  40-49% |  (0)
  50-59% | ##### (1)
  60-69% | ##### (1)
  70-79% | ################################### (7)
  80-89% | ################################### (7)
  90-99% | ######################################## (8)
  100% | ############### (3)

- v5b (second stage)
  Entries: 28
  Successes: 11
  Success rate: 0.3929
  Average likeness: 0.8482
  Median likeness: 0.8658

  Quality distribution (files per accuracy range):
  00-09% |  (0)
  10-19% |  (0)
  20-29% |  (0)
  30-39% |  (0)
  40-49% |  (0)
  50-59% | ########## (2)
  60-69% | ##### (1)
  70-79% | ################################### (7)
  80-89% | ################################### (7)
  90-99% | ######################################## (8)
  100% | ############### (3)

- llama 70 v5a
  python3 transcript_quality_parser.py output/transcript_quality_local_v5a_1768350869667.log 
  Entries: 46
  Successes: 18
  Success rate: 0.3913
  Average likeness: 0.8347
  Median likeness: 0.8417

  Quality distribution (files per accuracy range):
  00-09% |  (0)
  10-19% |  (0)
  20-29% |  (0)
  30-39% |  (0)
  40-49% | ### (1)
  50-59% | ##### (2)
  60-69% | ############# (5)
  70-79% | ########################### (10)
  80-89% | ########################### (10)
  90-99% | ######################################## (15)
  100% | ######## (3)

- llama 8b v6a
  python3 transcript_quality_parser.py output/transcript_quality_local_v6a_1768739986673.log 
  Entries: 39
  Successes: 16
  Success rate: 0.4103
  Average likeness: 0.8553
  Median likeness: 0.8642

  Quality distribution (files per accuracy range):
  00-09% |  (0)
  10-19% |  (0)
  20-29% |  (0)
  30-39% |  (0)
  40-49% | ### (1)
  50-59% |  (0)
  60-69% | ########## (3)
  70-79% | ########################### (8)
  80-89% | ##################################### (11)
  90-99% | ######################################## (12)
  100% | ############# (4)


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

Comparison: v2 -> v4
  Matched talks: 37
  Compared talks (with likeness): 37
  Improved: 31  Regressed: 6  Unchanged: 0
  Success->Fail: 2  Fail->Success: 6
  Avg delta: 0.2914  Median delta: 0.1757
  Top regressions (limit 10):
    24769: 0.9618 -> 0.7945 (delta -0.1673) status succeeded -> failed
    24525: 0.9088 -> 0.8303 (delta -0.0785) status succeeded -> failed
    26715: 0.6274 -> 0.5621 (delta -0.0653) status failed -> failed
    27058: 0.4898 -> 0.4360 (delta -0.0538) status failed -> failed
    27064: 0.7678 -> 0.7633 (delta -0.0045) status failed -> failed
    24795: 0.8583 -> 0.8538 (delta -0.0045) status failed -> failed
  Top improvements (limit 10):
    27030: 0.0296 -> 0.9092 (delta +0.8796) status failed -> succeeded
    27034: 0.0262 -> 0.8161 (delta +0.7899) status failed -> failed
    25443: 0.0209 -> 0.8028 (delta +0.7819) status failed -> failed
    25433: 0.0189 -> 0.7620 (delta +0.7431) status failed -> failed
    27032: 0.0235 -> 0.7543 (delta +0.7308) status failed -> failed
    26771: 0.0226 -> 0.7337 (delta +0.7111) status failed -> failed
    26749: 0.0246 -> 0.6914 (delta +0.6668) status failed -> failed
    26731: 0.1109 -> 0.7750 (delta +0.6641) status failed -> failed
    25843: 0.0282 -> 0.6644 (delta +0.6362) status failed -> failed
    26862: 0.1584 -> 0.7648 (delta +0.6064) status failed -> failed
---

python3 transcript_quality_compare.py output/transcript_quality_local_v4_1767463895773.log output/transcript_quality_local_v5b_1768050814804.log 
Version summaries:
- v4
  Entries: 37
  Successes: 11
  Success rate: 0.2973
  Average likeness: 0.8274
  Median likeness: 0.8303
- v5b
  Entries: 28
  Successes: 11
  Success rate: 0.3929
  Average likeness: 0.8482
  Median likeness: 0.8658

Comparison: v4 -> v5b
  Matched talks: 26
  Compared talks (with likeness): 26
  Improved: 11  Regressed: 12  Unchanged: 3
  Success->Fail: 1  Fail->Success: 2
  Avg delta: 0.0076  Median delta: 0.0000
  Top regressions (limit 10):
    27064: 0.7633 -> 0.5994 (delta -0.1639) status failed -> failed
    26864: 0.7645 -> 0.6421 (delta -0.1224) status failed -> failed
    26869: 0.9387 -> 0.8680 (delta -0.0707) status succeeded -> failed
    26771: 0.7337 -> 0.7159 (delta -0.0178) status failed -> failed
    25342: 0.8790 -> 0.8636 (delta -0.0154) status failed -> failed
    26709: 0.9340 -> 0.9244 (delta -0.0096) status succeeded -> succeeded
    27032: 0.7543 -> 0.7493 (delta -0.0050) status failed -> failed
    24769: 0.7945 -> 0.7920 (delta -0.0025) status failed -> failed
    26757: 0.9996 -> 0.9977 (delta -0.0019) status succeeded -> succeeded
    26711: 0.8846 -> 0.8832 (delta -0.0014) status failed -> failed
  Top improvements (limit 10):
    27058: 0.4360 -> 0.7668 (delta +0.3308) status failed -> failed
    24525: 0.8303 -> 0.9738 (delta +0.1435) status failed -> succeeded
    26749: 0.6914 -> 0.7488 (delta +0.0574) status failed -> failed
    27041: 0.8995 -> 0.9258 (delta +0.0263) status failed -> succeeded
    27030: 0.9092 -> 0.9286 (delta +0.0194) status succeeded -> succeeded
    27063: 0.8465 -> 0.8591 (delta +0.0126) status failed -> failed
    24798: 0.9903 -> 0.9964 (delta +0.0061) status succeeded -> succeeded
    27029: 0.7320 -> 0.7370 (delta +0.0050) status failed -> failed
    24781: 0.9350 -> 0.9384 (delta +0.0034) status succeeded -> succeeded
    26707: 0.8217 -> 0.8244 (delta +0.0027) status failed -> failed
---
python3 transcript_quality_compare.py output/transcript_quality_local_v5a_1768050129262.log output/transcript_quality_local_v5b_1768050814804.log 
Version summaries:
- v5
  Entries: 28
  Successes: 11
  Success rate: 0.3929
  Average likeness: 0.8424
  Median likeness: 0.8664
- v5b
  Entries: 28
  Successes: 11
  Success rate: 0.3929
  Average likeness: 0.8482
  Median likeness: 0.8658

Comparison: v5 -> v5b
  Matched talks: 28
  Compared talks (with likeness): 28
  Improved: 3  Regressed: 12  Unchanged: 13
  Success->Fail: 0  Fail->Success: 0
  Avg delta: 0.0058  Median delta: 0.0000
  Top regressions (limit 10):
    26864: 0.6549 -> 0.6421 (delta -0.0128) status failed -> failed
    26869: 0.8717 -> 0.8680 (delta -0.0037) status failed -> failed
    27063: 0.8608 -> 0.8591 (delta -0.0017) status failed -> failed
    25433: 0.7636 -> 0.7619 (delta -0.0017) status failed -> failed
    24525: 0.9753 -> 0.9738 (delta -0.0015) status succeeded -> succeeded
    26757: 0.9991 -> 0.9977 (delta -0.0014) status succeeded -> succeeded
    27034: 0.8179 -> 0.8168 (delta -0.0011) status failed -> failed
    26749: 0.7498 -> 0.7488 (delta -0.0010) status failed -> failed
    27041: 0.9262 -> 0.9258 (delta -0.0004) status succeeded -> succeeded
    26712: 0.9996 -> 0.9993 (delta -0.0003) status succeeded -> succeeded
  Top improvements (limit 10):
    24526: 0.3803 -> 0.5672 (delta +0.1869) status failed -> failed
    24769: 0.7915 -> 0.7920 (delta +0.0005) status failed -> failed
    26771: 0.7158 -> 0.7159 (delta +0.0001) status failed -> failed
