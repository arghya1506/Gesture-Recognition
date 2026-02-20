import cv2
import mediapipe as mp
import time
import math
import sys

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Camera Check
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not found.")
    sys.exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_time = 0
frame_count = 0

def get_normalized_landmarks(hand_landmarks, h, w):
    m_mcp = hand_landmarks.landmark[9]
    m_x, m_y = m_mcp.x * w, m_mcp.y * h
    
    wrist = hand_landmarks.landmark[0]
    wr_x, wr_y = wrist.x * w, wrist.y * h
    
    s = math.sqrt((m_x - wr_x)**2 + (m_y - wr_y)**2)
    if s == 0: s = 0.001
        
    norm_data = []
    for i in range(21):
        lm = hand_landmarks.landmark[i]
        lm_x, lm_y = lm.x * w, lm.y * h
        dist = math.sqrt((lm_x - m_x)**2 + (lm_y - m_y)**2)
        norm_data.append((i, dist / s))
        
    return norm_data

def get_cartesian_landmarks(hand_landmarks, h, w):
    coords = {}
    for i in range(21):
        lm = hand_landmarks.landmark[i]
        coords[i] = (int(lm.x * w), int(lm.y * h))
    return coords

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    if res.multi_hand_landmarks:
        for hand_lms in res.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape

            norm = get_normalized_landmarks(hand_lms, h, w)
            glob = get_cartesian_landmarks(hand_lms, h, w)

            # Throttled Printing (Every 10 frames)
            if frame_count % 10 == 0:
                print("-" * 30)
                print(f"{'ID':<4} | {'Norm (Ref:9)':<12} | {'Global':<10}")
                print("-" * 30)
                for i, val in norm:
                    gx, gy = glob[i]
                    print(f"{i:<4} | {val:<12.4f} | ({gx},{gy})")
                print("="*30)

            for i in range(21):
                gx, gy = glob[i]
                cv2.putText(frame, str(i), (gx, gy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time else 0
    prev_time = curr_time
    frame_count += 1

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    cv2.imshow("Data Logger", frame)

    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()