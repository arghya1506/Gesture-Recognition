import cv2
import mediapipe as mp
import time
import math
import statistics
from pynput.keyboard import Key, Controller as Keyboardcontroller
from pynput.mouse import Controller as MouseController
import data_proc_lib as dp  
import gesture_lib as gl    

keyboard = Keyboardcontroller()
mouse = MouseController()

# ==========================================
#  HARDWARE & MEDIAPIPE SETUP
# ==========================================
WINDOW_NAME = "SmartAir VLC Controller" 

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 360)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) 

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1, 
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
# ==========================================
#  GLOBAL STATE
# ==========================================
flag = False 
level_ptr = 0 
QUEUE_CAPACITY = 4
gesture_queue = [] 
prev_time = 0
last_execution_time = 0
COOLDOWN_DURATION = 1 
last_vol_val = 30

# ==========================================
#  LATENCY PROFILER LOGIC (UPDATED)
# ==========================================
class LatencyProfiler:
    def __init__(self):
        self.start_time = 0

    def start_total_timer(self):
        # Starts only if not already running to track the whole queue sequence
        if self.start_time == 0:
            self.start_time = time.perf_counter()

    def end_and_report(self, gesture_id):
        if self.start_time == 0: return
        total_latency = (time.perf_counter() - self.start_time) * 1000
        print(f"--- [TOTAL SYSTEM LATENCY] ID: {gesture_id} | Delay: {total_latency:.2f} ms ---")
        self.start_time = 0 # Reset for next gesture sequence

profiler = LatencyProfiler()

def anchored_control_loop(cap, hands, mode):
    """
    mode "Y_SCROLL": Vertical scrolling for playlists.
    mode "X_SEEK": Horizontal seeking (Left/Right keys) for timeline.
    """
    anchor_pos = None
    dead_zone = 30  # Pixels around center where nothing happens
    last_action_time = time.time()

    print(f">>> {mode} Mode Active. Anchor established.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # 320x240 capture is highly recommended here for <200ms latency
        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if res.multi_hand_landmarks:
            hand_lms = res.multi_hand_landmarks[0]
            # Tracking Landmark 9 (Middle MCP)
            curr_x = int(hand_lms.landmark[9].x * w)
            curr_y = int(hand_lms.landmark[9].y * h)

            if anchor_pos is None:
                anchor_pos = (curr_x, curr_y)
                continue

            # --- DYNAMIC CALCULATION ---
            dx = curr_x - anchor_pos[0]
            dy = anchor_pos[1] - curr_y # Inverted for intuitive UP movement

            # Determine deviation based on mode
            deviation = dy if mode == "Y_SCROLL" else dx
            
            if abs(deviation) > dead_zone:
                # Calculate Delay: Higher deviation = Lower delay (Faster)
                # Max delay 0.5s (slow), Min delay 0.05s (fast)
                delay = max(0.05, 0.5 - (abs(deviation) / (w/2)) * 0.8)
                
                if (time.time() - last_action_time) > delay:
                    execute_pynput_action(mode, deviation)
                    last_action_time = time.time()

            # --- EXIT CONDITION ---
            # Use a Fist (Distance between 9 and 12) to lock and exit
            if abs(hand_lms.landmark[12].y - hand_lms.landmark[9].y) < 0.1:
                print(">>> Action Locked.")
                break
                
            # Visuals: Center Anchor and Deviation Line
            cv2.circle(frame, anchor_pos, dead_zone, (255, 255, 255), 1)
            cv2.line(frame, anchor_pos, (curr_x, curr_y), (0, 255, 0), 2)
        
        cv2.imshow(WINDOW_NAME, frame)
        if cv2.waitKey(1) & 0xFF == 27: break

def execute_pynput_action(mode, deviation):
    if mode == "Y_SCROLL":       
        key = Key.up if deviation > 0 else Key.down
        with keyboard.pressed(Key.ctrl): keyboard.press(key) ; keyboard.release(key)
        
    elif mode == "X_SEEK":
        key = Key.right if deviation > 0 else Key.left
        with keyboard.pressed(Key.ctrl) : keyboard.press(key) ; keyboard.release(key)

# ==========================================
#  HELPER FUNCTIONS
# ==========================================
def draw_status_overlay(frame, level, fps):
    status_color = (0, 0, 255) if level == 0 else (0, 255, 0)
    cv2.putText(frame, f"SCANNING AT LEVEL: {level}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

def action_fx(gesture_id):
    global flag, level_ptr, last_execution_time
    current_time = time.time()
    
    if (current_time - last_execution_time) < COOLDOWN_DURATION:
        return 
    
    # ID 0: Toggle System (Lock/Unlock)
    if gesture_id == gl.ID_THUMBS_UP:
        flag = not flag
        print(f"|| SYSTEM TOGGLED: {flag} ||")
        last_execution_time = current_time
        return

    # Level 1 Actions
    #play/pause+ subsections
    if level_ptr == 1:
        last_execution_time = current_time 
        if gesture_id == gl.ID_INDEX_U: two_one_inf_loop_fx(cap, hands)
        elif gesture_id == gl.ID_VICTORY_U: two_two_inf_loop_fx(cap, hands)
        elif gesture_id == gl.ID_NICE: two_three_inf_loop_fx(cap, hands)
        elif gesture_id == gl.ID_QUAD: two_four_inf_loop_fx(cap, hands)
        elif gesture_id == gl.ID_OPEN_PALM: keyboard.press(Key.space) ; keyboard.release(Key.space)

        level_ptr = 1
        flag = True
    # Level 2.1 Actions

    # open palm= dynamic time seeking, index right/left=seeking +-10s, victory right/left=+-1min
    # spidey=reset,nice= quit/exit
    if level_ptr == 2.1:
        last_execution_time = current_time 
        if gesture_id == gl.ID_OPEN_PALM: 
            anchored_control_loop(cap, hands, "X_SEEK")
        elif gesture_id == gl.ID_NICE: keyboard.press('s') ; keyboard.release('s')
            
        elif gesture_id == gl.ID_SPIDEY: 
            # 1. Stop playback
            keyboard.press('s')
            keyboard.release('s')
            time.sleep(0.3)  # Professional pause for VLC to reset its buffer  
            # 2. Go to first item in playlist (Home key)
            keyboard.press(Key.home)
            keyboard.release(Key.home)
            time.sleep(0.2)       
            # 3. Play again
            keyboard.press(Key.space)
            keyboard.release(Key.space)
            print(">>> SYSTEM RESET: Playlist restarted from item 1.")
            
        elif gesture_id == gl.ID_INDEX_R: 
            keyboard.press(Key.right)
            keyboard.release(Key.right)
        elif gesture_id == gl.ID_INDEX_L: 
            keyboard.press(Key.left)
            keyboard.release(Key.left)    
        elif gesture_id == gl.ID_VICTORY_R:
            with keyboard.pressed(Key.ctrl): 
                keyboard.press(Key.right)
                keyboard.release(Key.right)      
        elif gesture_id == gl.ID_VICTORY_L:
            with keyboard.pressed(Key.ctrl): 
                keyboard.press(Key.left)
                keyboard.release(Key.left)
        
        level_ptr = 2.1
        flag = True
    # Level 2.2 Actions

    # spidey= mute, open palm= dynamic volume control, victory left/right= playback speed control
    if level_ptr == 2.2:
        last_execution_time = current_time 
        if gesture_id == gl.ID_SPIDEY: keyboard.press('m') ; keyboard.release('m')
        elif gesture_id == gl.ID_VICTORY_R: keyboard.press(']') ; keyboard.release(']')
        elif gesture_id == gl.ID_VICTORY_L: keyboard.press('[') ; keyboard.release('[')
        elif gesture_id == gl.ID_OPEN_PALM: anchored_control_loop(cap, hands,"Y_SCROLL")
    
        level_ptr = 2.2
        flag = True
    # Level 2.3 Actions

    # pointed index=prev/next,victory=loop, spidy=shuffle,open palm= miniplayer
    if level_ptr == 2.3:
        last_execution_time = current_time 
        if gesture_id == gl.ID_INDEX_L: keyboard.press('p') ; keyboard.release('p')
        elif gesture_id == gl.ID_INDEX_R: keyboard.press('n') ; keyboard.release('n')
        elif gesture_id == gl.ID_VICTORY_U: keyboard.press('l') ; keyboard.release('l')
        elif gesture_id == gl.ID_SPIDEY: 
          with keyboard.pressed(Key.ctrl): keyboard.press('s') ; keyboard.release('s')
        elif gesture_id == gl.ID_OPEN_PALM: 
            with keyboard.pressed(Key.ctrl): keyboard.press('l'); keyboard.release('l')
            time.sleep(0.7)
            with keyboard.pressed(Key.ctrl): keyboard.press('l'); keyboard.release('l')
            time.sleep(0.3)
        level_ptr = 2.3
        flag = True
    # Level 2.4 Actions
    # NICE= Screenshot,VICTORY= screenrecording
    # OPEN PALM= fullscreen toggle,SPIDEY= aspect ratio
    if level_ptr == 2.4:
        last_execution_time = current_time 
        if gesture_id == gl.ID_NICE: 
            with keyboard.pressed(Key.shift):  keyboard.press('s') ; keyboard.release('s')
        elif gesture_id == gl.ID_SPIDEY: keyboard.press('a') ; keyboard.release('a')
        elif gesture_id == gl.ID_OPEN_PALM: keyboard.press('f') ; keyboard.release('f')
        elif gesture_id == gl.ID_VICTORY_U:
            with keyboard.pressed(Key.shift): keyboard.press('r') ; keyboard.release('r')
def queue_fx(gesture_id):
    global gesture_queue    
    
    # Start the system timer as soon as the first frame enters the queue
    if not gesture_queue:
        profiler.start_total_timer()

    if gesture_queue:
        if gesture_id != 0 and all(x == 0 for x in gesture_queue):
            gesture_queue.clear()
            profiler.start_total_timer() # Reset timer for the new actual gesture
        elif gesture_id == 0 and all(x != 0 for x in gesture_queue):
            gesture_queue.clear()

    gesture_queue.append(gesture_id)

    if len(gesture_queue) >= QUEUE_CAPACITY:
        try:
            med_val = int(statistics.median(gesture_queue))
            print(f"\n>>> QUEUE: {gesture_queue} | MEDIAN: {med_val}")
            
            # REPORT TOTAL LATENCY: Includes 4-frame capture + processing + queue wait
            profiler.end_and_report(med_val)
            
            action_fx(med_val) 
        except statistics.StatisticsError:
            pass
        gesture_queue.clear()
# ==========================================
#  INFERENCE LOOPS
# ==========================================

def common_loop_logic(cap, hands, level_val, gesture_funcs):
    global flag, level_ptr, prev_time
    level_ptr = level_val
    
    while flag:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            
            # 1. Pipeline: Get Smoothed Data
            norm_dict, global_coords = dp.get_refined_data(hand_landmarks, h, w)
            
            # 2. Draw Skeleton
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 3. Check Gestures
            for func in gesture_funcs:
                # Passing 'frame' for debug drawing
                func(norm_dict, global_coords, queue_fx)

        # 4. FPS & Status
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        draw_status_overlay(frame, level_ptr, fps)

        cv2.imshow(WINDOW_NAME, frame)
        if cv2.waitKey(1) & 0xFF == 27:
            flag = False
            break

def two_one_inf_loop_fx(cap, hands):
    # Level 2.1: Volume/Media Controls
    funcs = [ gl.open_palm_fx,gl.spidey_fx, gl.index_left_fx, gl.index_right_fx ,
             gl.victory_left_fx, gl.victory_right_fx, gl.thumbs_up_fx,gl.nice_fx]
    common_loop_logic(cap, hands, 2.1, funcs)

def two_two_inf_loop_fx(cap, hands):
    # Level 2.2: Brightness/Zoom
    funcs = [gl.spidey_fx, gl.open_palm_fx,
             gl.victory_left_fx, gl.victory_right_fx,  gl.thumbs_up_fx]
    common_loop_logic(cap, hands, 2.2, funcs)

def two_three_inf_loop_fx(cap, hands):
    # Level 2.3
    funcs = [ gl.open_palm_fx, gl.index_left_fx, gl.index_right_fx, gl.spidey_fx, gl.thumbs_up_fx] 
    common_loop_logic(cap, hands, 2.3, funcs)

def two_four_inf_loop_fx(cap, hands):
    # Level 2.4
    funcs = [ gl.open_palm_fx,gl.victory_fx,gl.spidey_fx, gl.nice_fx ,gl.thumbs_up_fx]
    common_loop_logic(cap, hands, 2.4, funcs)

def one_inf_loop_fx(cap, hands):
    # Level 1: Main Menu
    funcs = [gl.open_palm_fx, gl.index_up_fx, gl.victory_fx, gl.nice_fx, gl.quad_fx, gl.thumbs_up_fx]
    common_loop_logic(cap, hands, 1, funcs)

# ==========================================
#  MAIN ENTRY (Level 0)
# ==========================================

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        norm_dict, global_coords = dp.get_refined_data(hand_landmarks, h, w)
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Level 0 only listens for Unlock (Thumbs Up)
        gl.thumbs_up_fx(norm_dict, global_coords, queue_fx)

    # State Transition
    if flag:
        one_inf_loop_fx(cap, hands)
        flag = False # Reset to locked when returning
        level_ptr = 0
    
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time else 0
    prev_time = curr_time
    draw_status_overlay(frame, 0, fps)

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()