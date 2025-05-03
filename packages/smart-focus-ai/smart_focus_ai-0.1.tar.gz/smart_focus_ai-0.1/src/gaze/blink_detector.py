# src/gaze/blink_detector.py

import numpy as np

class BlinkDetector:
    # indices Mediapipe pour l’œil gauche (similaire pour droit si besoin)
    LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144] 
    RIGHT_EYE_IDX = [263, 387, 385, 362, 380, 373]
    EAR_THRESH = 0.2     # à ajuster par rapport à tes tests
    CONSEC_FRAMES = 2    # nombre de frames consécutives où l'oeil doit être fermé
                        
    def __init__(self):
        self.counter = 0        # compte frames fermés
        self.blink_count = 0    # nombre total de clignements
        self.eye_closed = False

    @staticmethod
    def eye_aspect_ratio(pts):
        # pts: array shape (6,2)
        A = np.linalg.norm(pts[1] - pts[5])
        B = np.linalg.norm(pts[2] - pts[4])
        C = np.linalg.norm(pts[0] - pts[3])
        return (A + B) / (2.0 * C)

    def update(self, frame, landmarks, fm):
        """
        Appeler à chaque frame avec :
          - frame: image
          - landmarks: resultat de fm.process()
          - fm: instance de FaceMeshDetector pour transformer en pixels
        Retourne self.blink_count
        """
        # récupère les 6 points de l’œil gauche
        pts = np.array([
            fm.landmark_to_pixel(frame, landmarks.landmark[i])
            for i in self.LEFT_EYE_IDX
        ], dtype=np.float32)

        ear = self.eye_aspect_ratio(pts)

        if ear < self.EAR_THRESH:
            self.counter += 1
        else:
            # si on passe de « fermé » assez longtemps à « ouvert », on incrémente
            if self.counter >= self.CONSEC_FRAMES:
                self.blink_count += 1
            self.counter = 0

        return self.blink_count

