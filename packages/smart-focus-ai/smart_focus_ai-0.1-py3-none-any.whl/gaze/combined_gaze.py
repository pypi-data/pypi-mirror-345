# # src/gaze/combined_gaze.py

# import numpy as np
# from src.gaze.face_mesh import FaceMeshDetector
# # from src.gaze.blink_detector import BlinkDetector
# from src.gaze.gaze_estimator import GazeEstimator
# from src.gaze.smoother import DirectionSmoother

# class CombinedGazeDetector:
#     """
#     Utilise deux GazeEstimator (horizontal + vertical) + smoothing
#     pour déterminer si l’utilisateur regarde le centre de l’écran.
#     """
#     def __init__(self, face_mesh: FaceMeshDetector):
#         self.fm = face_mesh

#         # 1) calibration horizontale (axis=0)
#         cal_h = {
#             "Right":  (-0.31, +0.03),
#             "Center": (+0.03, +0.17),
#             "Left":   (+0.17, +0.25),
#         }
#         self.ge_h = GazeEstimator(calibration_ranges=cal_h,
#                                   momentum=0.8, axis=0)

#         # 2) calibration verticale (axis=1)
#         cal_v = {
#             "Up":     (-float("inf"), -0.05),
#             "Center": (-0.05, -0.04),
#             "Down":   (-0.04, float("inf")),
#         }
#         self.ge_v = GazeEstimator(calibration_ranges=cal_v,
#                                   momentum=0.8, axis=1)

#         # smoothing
#         self.h_smoother = DirectionSmoother(window_size=5)
#         self.v_smoother = DirectionSmoother(window_size=5)

#     def is_gazing(self, frame) -> bool:
#         lm = self.fm.process(frame)
#         if lm is None:
#             return False

#         dir_h = self.ge_h.estimate(frame, lm) or "None"
#         dir_v = self.ge_v.estimate(frame, lm) or "None"
#         smoother_h = self.h_smoother.update(dir_h)
#         smoother_v = self.v_smoother.update(dir_v)

#         # Focus si l’un des axes est centré
#         return (smoother_h == "Center") or (smoother_v == "Center")



# src/gaze/combined_gaze.py

import numpy as np
from src.gaze.face_mesh import FaceMeshDetector
from src.gaze.gaze_estimator import GazeEstimator
from src.gaze.smoother import DirectionSmoother

class CombinedGazeDetector:
    """
    Combine deux GazeEstimator (horiz + vert) + smoothing pour
    déterminer si l’utilisateur regarde le centre de l’écran.
    """
    def __init__(self, face_mesh: FaceMeshDetector):
        self.fm = face_mesh

        # Plages de calibration horizontale
        cal_h = {
            "Right":  (-0.31, +0.03),
            "Center": (+0.03, +0.17),
            "Left":   (+0.17, +0.25),
        }
        self.ge_h = GazeEstimator(calibration_ranges=cal_h,
                                  momentum=0.8, axis=0)

        # Plages de calibration verticale
        cal_v = {
            "Up":     (-float("inf"), -0.05),
            "Center": (-0.05, -0.04),
            "Down":   (-0.04, float("inf")),
        }
        self.ge_v = GazeEstimator(calibration_ranges=cal_v,
                                  momentum=0.8, axis=1)

        # Smoothers
        self.h_smoother = DirectionSmoother(window_size=5)
        self.v_smoother = DirectionSmoother(window_size=5)

    def is_gazing(self, frame) -> bool:
        lm = self.fm.process(frame)
        if lm is None:
            return False

        # --- estimation & smoothing ---
        dir_h     = self.ge_h.estimate(frame, lm) or "None"
        dir_v     = self.ge_v.estimate(frame, lm) or "None"
        smoother_h = self.h_smoother.update(dir_h)
        smoother_v = self.v_smoother.update(dir_v)

        # Focus si l’un des axes est centré
        return (smoother_h == "Center") or (smoother_v == "Center")
