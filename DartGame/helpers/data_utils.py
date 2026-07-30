import numpy as np
from helpers.math_utils import calculate_angle

def extract_features(lm, hand_side):
    def v(i): return np.array([lm[i].x, lm[i].y, lm[i].z])

    if hand_side == "Right":
        idx_s, idx_e, idx_w = 12, 14, 16 
        idx_h_same = 24
        mirror_x = 1.0
    else: 
        idx_s, idx_e, idx_w = 11, 13, 15
        idx_h_same = 23
        mirror_x = -1.0
        
    s, e, w = v(idx_s), v(idx_e), v(idx_w) 
    center_hip = (v(23) + v(24)) / 2.0
    
    torso_size = np.linalg.norm(s - center_hip)
    if torso_size == 0: torso_size = 1.0

    # Normalizacja
    def norm(p):
        res = (p - center_hip) / torso_size
        res[0] *= mirror_x
        return res

    n_s, n_e, n_w = norm(s), norm(e), norm(w) 
    ang_elbow = calculate_angle([s[0], s[1]], [e[0], e[1]], [w[0], w[1]])  
    h_same = v(idx_h_same)
    ang_shoulder = calculate_angle([h_same[0], h_same[1]], [s[0], s[1]], [e[0], e[1]])

    return [
        n_s[0], n_s[1], n_s[2], 
        n_e[0], n_e[1], n_e[2], 
        n_w[0], n_w[1], n_w[2], 
        ang_elbow, ang_shoulder
    ]