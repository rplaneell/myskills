# Reference ranges, error and score

Ranges are common bike fit rules of thumb. None is a law, and the rider's body, style and goals matter.

| Measure | Green | Amber | Error used | Note |
| --- | --- | --- | --- | --- |
| Knee extension at the bottom | 145 to 155 degrees | 140 to 160 | 5 degrees | About 25 to 35 degrees of knee bend (Holmes 1994; Bini 2011 review) |
| Hip angle at the top | above 45 degrees | 38 to 45 | 5 degrees | Depends on flexibility |
| Torso angle | 30 to 45 degrees | 20 to 55 | 3 degrees | Lower is more aerodynamic |
| Elbow angle | 150 to 170 degrees | 130 to 175 | 5 degrees | Soft bend of about 10 to 30 degrees |
| Shoulder angle | 80 to 100 degrees | 70 to 110 | 5 degrees | About 90 degrees |
| Ankle range of motion | 15 to 35 degrees | 10 to 45 | 8 degrees | Typically 20 to 30 |
| Cadence | 80 to 100 rpm | 70 to 110 | 2 rpm | rpm is revolutions per minute |
| Pelvis bounce | below 15 mm | 15 to 30 | 8 mm | Screening threshold, not published |
| Knee over ball of foot at 3 o'clock | within 30 mm | within 60 | 35 mm | Weak evidence, large error |

Published pose estimation studies on cycling report errors of roughly 3 to 10 degrees at hip and knee, and
worse at the ankle. Differences smaller than the error must not be turned into conclusions.

**Score out of 100.** Each measure scores 1 for green, 0.5 for amber and 0 for red, weighted (knee extension 3,
hip angle 2, cadence 1.5, elbow 1.5, the rest 1 or 0.5). The interval comes from 3000 simulations in which each
measure is shifted by a random error (the error value is treated as roughly a 95 percent bound) and the 5th
to 95th percentile is reported. Inspired by the VeloLens idea of a quality score from smoothness, cadence,
knee extension and posture stability. Standing riding is not scored.

**Fit conversions** (`fit_numbers.py`). One millimetre of saddle height moves the knee by about 0.6 degrees,
10 mm of handlebar height moves the torso and hip by about 1.2 degrees, and 10 mm of reach changes the elbow
by about 6 degrees. These come from segment lengths and simple geometry, with about 8 percent error.
