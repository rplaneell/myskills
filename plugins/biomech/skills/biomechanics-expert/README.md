# Cycling biomechanics from one side view video

A reusable pipeline and a Claude skill for analysing a cyclist's pedalling form and position from a single
side view video: joint angles per pedal stroke, traffic light scoring against common bike fit ranges with an
honest error band, fit advice (saddle height, saddle fore and aft, handlebar stack, reach), a frame size
estimate, and a polished illustrated report.

It was built from one real session (a rider on an indoor roller, three riding styles in 26 seconds) and the
report was written in Catalan. The text strings are in Catalan inside the scripts; see the adaptation guide.

## What is in here

| Path | What it is |
| --- | --- |
| `SKILL.md` | The skill: when to use it, the method, the rules, and the lessons learned |
| `pipeline/` | The working scripts, in the order listed in `pipeline/run_all.sh` |
| `docs/ADAPT_TO_A_NEW_VIDEO.md` | What to change for a different rider, video and language |
| `docs/REFERENCE_RANGES.md` | The reference ranges, error bands and score method |
| `.gitignore`, `.env.example` | Secrets and personal media safeguards |

## Honest status

* The scripts ran end to end on one video. They are not yet generalised: file paths, the rider height and the
  time ranges of each riding style are fixed inside them. The adaptation guide lists every place to change.
* Pose tracking used MediaPipe (Google). Sports2D (RTMPose model) installs but its model files come from hosts
  that were blocked in the session, so the two tool cross check is still to do on a machine with open access.
* Only the side facing the camera can be measured. The far leg is guessed by the model.
* Reference ranges are rules of thumb, not laws.

## Privacy and secrets

Videos, pose data, images and reports are excluded by `.gitignore`: they show a person's body. Keep API keys,
tokens and passwords only in a local `.env` file (API means application programming interface, the door a
program uses to talk to another service). This project needs none.

## Quick start

```bash
pip install mediapipe opencv-python scipy matplotlib pillow pandas
sudo apt install libegl1 libgles2      # MediaPipe needs these on a bare Linux machine
# put ride.mp4 and the MediaPipe pose_landmarker_heavy.task model where run_all.sh expects them
bash pipeline/run_all.sh
```
