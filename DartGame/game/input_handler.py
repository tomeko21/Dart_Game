import threading
import cv2
import mediapipe as mp
import numpy as np
import time
import os
import joblib
import math
from collections import deque
from config.consts import *
from helpers.math_utils import calculate_angle, is_hand_open_strict
from helpers.data_utils import extract_features

class SmartController:
    def __init__(self, use_camera=True):
        self.use_camera = use_camera
        self.running = True
        self.current_frame = None
        
        # States
        self.holding_dart = False
        self.holding_hand = None
        self.pickup_timers = {"Left": 0.0, "Right": 0.0}
        self.pickup_lock_hand = None
        self.pickup_loss_counter = {"Left": 0, "Right": 0}
        
        self.motion_buffer = deque(maxlen=SEQ_LEN)
        self.aim_history = deque(maxlen=10)
        self.cooldown_timer = 0
        self.safety_lock_timer = 0

        # Only in camera mode
        if self.use_camera:
            self._init_camera_resources()
        else:
            self.cap = None
            self.thread = None
            self.ai_model = None

    def _init_camera_resources(self):
        # Mediapipe config
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5)
        
        # Camera Setup
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # AI load
        self._load_ai_assets()

        # Start Camera Thread
        self.thread = threading.Thread(target=self._update_camera, daemon=True)
        self.thread.start()

    def _update_camera(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
            else:
                time.sleep(0.01)

    def _load_ai_assets(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        assets_dir = os.path.join(project_root, 'assets')
        model_path = os.path.join(assets_dir, 'moj_najlepszy_model.pkl')
        scaler_path = os.path.join(assets_dir, 'moj_scaler.pkl')
        
        try:
            self.ai_model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print("AI: System gotowy.")
        except:
            print("AI: Błąd ładowania modeli!")
            self.ai_model = None

    def process(self):
        if not self.use_camera or self.current_frame is None:
            return None, {}
            
        frame = self.current_frame.copy()
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h_screen, w_screen, _ = frame.shape
        current_time = time.time()
        
        data = {"aim": None, "progress_left": 0.0, "progress_right": 0.0,
                "action": "WAIT", "skeleton": None, "ai_confidence": 0.0}

        pose_res = self.pose.process(rgb)
        

        hands_res = None 
        if not self.holding_dart:
            hands_res = self.hands.process(rgb)
            
        frame_flipped = cv2.flip(frame, 1)

        if not pose_res.pose_landmarks:
            self.holding_dart = False
            return frame_flipped, data
        
        lm = pose_res.pose_landmarks.landmark

        # Pickup
        if not self.holding_dart:
            IDX_MAP = {
                "Right": {"w": 16, "h": 24},
                "Left":  {"w": 15, "h": 23}
            }
            
            for side in ["Left", "Right"]:
                if self.pickup_lock_hand and self.pickup_lock_hand != side: continue

                idx = IDX_MAP[side]
                wx, wy = lm[idx['w']].x, lm[idx['w']].y
                hx, hy = lm[idx['h']].x, lm[idx['h']].y
                
                in_zone = (abs(wy - hy) < HIP_TOLERANCE_Y) and (abs(wx - hx) < HIP_TOLERANCE_X)
                
                is_hand_valid = False
                if in_zone and hands_res and hands_res.multi_hand_landmarks:
                    for hand_lms in hands_res.multi_hand_landmarks:
                        if math.hypot(hand_lms.landmark[0].x - wx, hand_lms.landmark[0].y - wy) < 0.15:
                            if is_hand_open_strict(hand_lms): 
                                is_hand_valid = True
                            break

                if is_hand_valid and current_time > self.cooldown_timer:
                    self.pickup_loss_counter[side] = 0
                    if self.pickup_timers[side] == 0:
                        self.pickup_timers[side] = current_time
                        self.pickup_lock_hand = side
                else:
                    self.pickup_loss_counter[side] += 1
                    if self.pickup_loss_counter[side] > 10:
                        self.pickup_timers[side] = 0.0
                        if self.pickup_lock_hand == side: self.pickup_lock_hand = None

                if self.pickup_timers[side] > 0:
                    prog = min((current_time - self.pickup_timers[side]) / PICKUP_DURATION, 1.0)
                    data[f"progress_{side.lower()}"] = prog
                    
                    if prog >= 1.0:
                        self.holding_dart, self.holding_hand = True, side
                        self.pickup_timers = {"Left": 0.0, "Right": 0.0}
                        self.pickup_lock_hand = None
                        self.safety_lock_timer = current_time + 1.0
                        self.motion_buffer.clear()
                        self.aim_history.clear()
                        data["action"] = "PICKUP"

        # Throw
        if self.holding_dart:
            side = self.holding_hand
            
            features = extract_features(lm, side)
            self.motion_buffer.append(features)
            
            idx_w, idx_s, idx_e = (16, 12, 14) if side == "Right" else (15, 11, 13)
            
            def to_screen(idx):
                return int((1.0 - lm[idx].x) * w_screen), int(lm[idx].y * h_screen)

            target_pos = to_screen(idx_w)
            self.aim_history.append(target_pos)
            
            data["aim"] = (int(np.mean([p[0] for p in self.aim_history])), 
                           int(np.mean([p[1] for p in self.aim_history])))
            data["skeleton"] = (to_screen(idx_s), to_screen(idx_e), target_pos)
            
            # AI
            if self.ai_model and len(self.motion_buffer) == SEQ_LEN:
                input_scaled = self.scaler.transform(np.array(self.motion_buffer).flatten().reshape(1, -1))
                proba = self.ai_model.predict_proba(input_scaled)[0]
                data["ai_confidence"] = proba[1]
                
                if current_time > self.safety_lock_timer and proba[1] >= AI_CONFIDENCE_THRESHOLD:
                    data["action"] = "THROW"
                    self.cooldown_timer = current_time + THROW_COOLDOWN
                    self.holding_dart = False

        return frame_flipped, data

    def close(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        
        if self.cap:
            self.cap.release()
            
        if self.use_camera:
            self.pose.close()
            self.hands.close()