#!/usr/bin/env bash
# Order of the pipeline. The scripts still use fixed paths (see docs/ADAPT_TO_A_NEW_VIDEO.md).
set -e
W=/mnt/user-data/working; P="$(cd "$(dirname "$0")" && pwd)"
mkdir -p $W/scripts $W/mp /home/user/ride_analysis/{images,video,data,report}
cp $P/*.py $W/scripts/
# 1. put the video at $W/ride.mp4 and the MediaPipe model at $W/mp/pose_landmarker_heavy.task
python3 $W/scripts/extract_mp.py $W/ride.mp4 $W/mp/pose_landmarker_heavy.task $W/mp/landmarks.npy
python3 $W/scripts/analyse2.py        # smoothing, crank phase, strokes, per stroke metrics
python3 $W/scripts/metrics.py         # reference ranges, traffic lights, score with simulated error
python3 $W/scripts/fit_numbers.py     # mm per degree conversions for the fit advice
for s in pro1 pro2 pro3 pro3b pro4; do python3 $W/scripts/$s.py; done   # the 21 figures
python3 $W/scripts/video.py           # annotated video and GIF
python3 $W/scripts/export_data.py     # CSV files
python3 $W/scripts/report.py          # HTML report (then print to PDF with Chromium)
