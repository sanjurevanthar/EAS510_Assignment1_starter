# EAS 510 - Assignment 1: Digital Forensics Apprentice

A rule-based expert system that matches modified images back to their originals.

This is the **starter repository** for Project 1. Two repositories matter:

| Repository | Role |
|------------|------|
| `delveccj/EAS510_Assignment1_starter` (this repo) | Your **code** lives here. You will fork it, work in your fork, and push your final submission here. |
| `delveccj/EAS510_Assignment1` | The **dataset** (read-only). Clone it for the images; never commit it to your fork. |

## Setup on your Codio box

```bash
# 1. Fork this repo on GitHub, then in your box:
git clone https://github.com/YOUR-USERNAME/EAS510_Assignment1_starter.git
cd EAS510_Assignment1_starter

# 2. Clone the read-only dataset as a sibling folder (images live there):
cd ~/workspace
git clone https://github.com/delveccj/EAS510_Assignment1.git

# 3. Install dependencies:
cd ~/workspace/EAS510_Assignment1_starter
python3 -m pip install -r requirements.txt

# 4. Point this box at YOUR fork (run once):
./setup_git.sh
```

## Repository layout

```
forensics_detective.py   SimpleDetector: register targets + find_best_match
rules.py                 Rule functions (Rule 1: Metadata, Rule 2: Histogram, Rule 3: Template)
test_system.py           Runs the detector over the data folders and writes results_*.txt
scripts/check_output_format.py   Validates a results file against the required format
setup_git.sh, submit.sh  One-time setup + commit/push helper ("backup button")
```

## The task in one paragraph

Implement three interpretable rules (metadata, color histogram, template matching)
that combine into a 0-100 confidence score. Run your system on `modified_images/`
and `random/` and save the full output as `results_v1.txt`. In Phase 2, run on
`hard/`, diagnose a systematic failure, add a **Rule 4**, and save
`results_v1_hard.txt` and `results_v2.txt`. Full instructions are in the Codio guide
and in the assignment PDF in UBLearns.

## Running

```bash
# Phase 1 (easy + random) -> results_v1.txt
python3 test_system.py --modified --random --output results_v1.txt

# Phase 1 on hard cases -> results_v1_hard.txt
python3 test_system.py --hard --output results_v1_hard.txt

# Phase 2 (everything) -> results_v2.txt
python3 test_system.py --modified --hard --random --output results_v2.txt

# Validate any results file against the required format:
python3 scripts/check_output_format.py results_v1.txt
```

The data folders are resolved from a sibling clone of `EAS510_Assignment1`.
If your data is elsewhere, pass `--data-dir /path/to/EAS510_Assignment1`.

## Output format (do not alter)

```
Processing: modified_image_01.jpg
Rule 1 (Metadata): FIRED - Size ratio 0.85 -> 20/30 points
Rule 2 (Histogram): FIRED - Correlation 0.92 -> 25/30 points
Rule 3 (Template): FIRED - Match score 0.76 -> 30/40 points
Final Score: 75/100 -> MATCH to original_03.jpg
```

## Backup doctrine

Your Codio box can be reset at any time. **Your fork on GitHub is the only safe
copy.** After every milestone run `./submit.sh "describe what you did"`. A box
restart never touches GitHub.

## My Reflection:

## 1. Observed weakness in V1: what failed and why

The main reason for the failure of v1 is on the cropped and resized images. On these images the rule 3 scores 0/40 and rule and 2 barely reaches 40+ combined, which is less than the threshold.

### Improvement on phase 1:

I modified the rule 1 implementation, helping the cropped and resized images to reach the threshold. Originally rule 1 uses meta data and award score to the images with how similar file size are and how much of the original's pixel area the suspect holds. In case of cropped and resized images the average fell below 0.6 and get 0 for 30 as the resulting score.

Improved rule asks 3 questions:
1. same width same size -> +15, suggesting a full-frame copy
2. if different image format(+15), in case of smaller file(+10) - suggesting a format change or compression of file
3. if not same size and suspect smaller by width and length(+20) - created specifically for cropped images

This increased accuracy from 32/60 to 39/60 for easy modified images. In case of hard images, it holds more cropped and resized images for which this improvement is not enough.

From this file "results_v1_hard.txt", we can see that amoung 19/60 rejected hard images, all the 19 were crop or resize variants. Here in all 19 rejections, the score given by the rule 3 is 0/40.
Eg: for a image original_00__crop_keep70__bright__compress__q40__v2.jpg
rule 1: 20
rule 2: 27
rule 3: 0

### Main Reason?

Rule 3 Failure for the Cropped and resized variants.

### Why this failure?

In rule 3, it uses cv2.matchTemplate which slides the suspect over original, looking for same pixels at the same scale. So incase of any change in size(resize, crop) makes the match collapse. Hence resulting in the "0" score for the image pairs.

Rule 1 doesnot handles the images well, it just check for 3 different conditions just to handle the cropped and rescaled variants, it tells us how a file may be changed but it does not tell us if that is the same image. So this would mislead the system.

So, Rule 3 cannot handle change or scaled images and rule 1 gives same points to similar meta data images and rule 2 gives color only. 

So from the above no rule confirms about the SHAPE, STRUCTURE  or the CONTENT of the picture. It is this reason makes v1 weak.



## 2. Design decision for V2: what Rule 4 is and why you chose it

Rule 4 checks the shape and structure of images, it uses ORB feature matching for the comparison. ORB cpmpares images by small patterns, not by the pixel positions, so it works for the crop and resized images.

### How does it work?
 1. Find the ORB keypoints(corners) from the both suspect and original images, say upto 1000 points.
 2. Now compare the keypoints between the two images to find pairs that look similar.
 3. Keep the pair only if it is better than the next best option(ratio test)
 4. Use RANSAC(Random Sample Consensus) to check which pairs agree on the same overall movement between the images.
 5. The good pairs are called inliers.
 6. Now the rule checks for 15 inliers to count and 40+ would give full score.

### why ORB?
 1. In Croped and Resized images, ORB matches by the keypoints, so the cropped area still matches the same keypoints in the original.
 2. For brightness and compression, ORB compares the nearby pixels with each other, so the overall brightness change cancels out and the fingerprint of the keypoint remains unchanged.
 3. The ratio test and RANSAC removes unclear matches, it is less likely to produce the 15 inliers so, this rule is safe.
   
### why to choose ORB instead of SIFT?
ORB is fast than SIFT and it is simple and easy to implement using OpenCV

## 3. Effect of the change: accuracy before/after on easy vs hard

### Accuracy on Easy:

### Dataset                                       Before(P1)                            After(P2)

    1. Easy - modified(before improving)(60)       32(53%)                             NA
    2. Easy - modified(after Rule 1 improve)(60)   39(65%)                             43(72%)
    3. Easy - random                               15/15 reject                        15/15 reject

### Accuracy on Hard:

### Dataset                                       Before(P1)                            After(P2)

    1. Hard(60)                                    41(68%)                              51(85%)

### Did Accuracy improve? 
Yes it got improved by almost 10%. Since the weightage of rule 4 is only 10, it did not affect the overall score much, resulting in a little improvement in the accuracy.

In the hard set the accuracy improved a lot(+17%) because it contains more crop and resized images which is effectively handled by rule 4. 
Eg: 
we have "original_00__crop_keep70__bright__compress__q40__v2.jpg" score = 47(REJECTED) in phase 1.
In phase 2 it went to score = 50(MATCHED) with 277 ORB inliers.


## 4. Trade-offs: what new costs or risks did Rule 4 introduce

There is not much risk added due to the addition of rule 4, but there is a few trade-offs.

1. Execution Time:
   The execution time of the all 4 rule execution has been increased, because the ORB is recalculated for every image pair. So incase of 1000 to million images, it would consume few hours to days.
2. Hardcoded Values:
   The limits for the inliers(15, 40), 0.75 test ratio and the 5 pixel RANSAC tolerence are the fixed values specifically for this dataset. This is a major drawback as this rule cannot be used for any similar datasets.
3. Edge Cases Failure:
   In case of plain and cropped images, the rule finds hard to find the inliers(less than 15). Hence looses the score for the rule 4 and getting rejected(Increasing False Negatives).
4. Score of Rule4:
   The score of rule 4 has no less impact, apart from the edge cases, this is a good criteria for comparison(shape and structure). Improving the score from 10 to 25 might help in increasing the accuracy.


## License

Apache 2.0. See `LICENSE`.