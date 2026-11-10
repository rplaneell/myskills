import sys, cv2, numpy as np, mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
video, model, out = sys.argv[1:4]
opts = vision.PoseLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path=model),
    running_mode=vision.RunningMode.VIDEO, num_poses=1,
    min_pose_detection_confidence=0.3, min_pose_presence_confidence=0.3, min_tracking_confidence=0.3)
lm = vision.PoseLandmarker.create_from_options(opts)
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS)
rows=[]; i=0
while True:
    ok, fr = cap.read()
    if not ok: break
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    r = lm.detect_for_video(img, int(i*1000/fps))
    a = np.full((33,4), np.nan)
    if r.pose_landmarks:
        for k,p in enumerate(r.pose_landmarks[0]):
            a[k]=[p.x*fr.shape[1], p.y*fr.shape[0], p.visibility, p.presence]
    rows.append(a); i+=1
np.save(out, np.array(rows)); print(i, 'frames', fps, 'fps; detected', int(np.sum(~np.isnan(np.array(rows)[:,0,0]))))
