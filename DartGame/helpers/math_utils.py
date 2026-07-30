import numpy as np
import math

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360-angle
    return angle

def is_hand_open_strict(hand_lms):
    wrist = hand_lms.landmark[0]
    folded_fingers = 0
    finger_pairs = [(8, 6), (12, 10), (16, 14), (20, 18)]
    
    for tip_idx, pip_idx in finger_pairs:
        tip = hand_lms.landmark[tip_idx]
        pip = hand_lms.landmark[pip_idx]
        d_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        d_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
        if d_tip < d_pip:
            folded_fingers += 1
            
    return folded_fingers < 3