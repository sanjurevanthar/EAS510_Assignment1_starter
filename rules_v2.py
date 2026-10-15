"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).
"""
import cv2
import numpy as np

import rules
from rules import _gray

#: Import the original rules and append your new one.
RULES = rules.RULES + ("rule4_edges",)

def rule4_edges(target, input_path):
    """ORB feature matching + RANSAC: robust to crop, resize, brightness."""
    out = {"rule": 4, "name": "Edges", "fired": False, "score": 0,
           "out_of": 10, "note": "Inliers 0", "metric": 0.0}
    try:
        orb = cv2.ORB_create(nfeatures=1000)
        ka, da = orb.detectAndCompute(_gray(input_path), None)
        kb, db = orb.detectAndCompute(_gray(target["path"]), None)
        if da is None or db is None:
            return out

        pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
        good = [p[0] for p in pairs
                if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]

        inliers = 0
        if len(good) >= 4:
            src = np.float32([ka[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst = np.float32([kb[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
            if mask is not None:
                inliers = int(mask.sum())

        out["metric"] = round(min(1.0, inliers / 40), 3)
        out["note"] = f"Inliers {inliers}"
        if inliers >= 15:
            out["fired"] = True
            out["score"] = int(round(out["out_of"] * out["metric"]))
    except Exception:
        pass
    return out
