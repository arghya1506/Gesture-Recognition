import math

# Internal Persistent State (Static-like memory)
# Using Lists for Norm Data (1D) and Dicts for Global (2D)
ema_norm_data = [0.0] * 21
ema_global_data = {i: (0, 0) for i in range(21)}

# Tuning Constants
ALPHA_NORM = 0.25   
ALPHA_GLOBAL = 0.5

def get_normalized_landmarks(hand_landmarks, h, w):
    """
    Centroid-Logic: Landmark 9 (Middle MCP) is the origin (0,0).
    Distances are scaled by the Wrist-to-Knuckle (0-9) length.
    """
    # 1. Capture the 'Anchor' (Knuckle 9)
    m_mcp = hand_landmarks.landmark[9]
    m_x, m_y = m_mcp.x * w, m_mcp.y * h
    
    # 2. Capture the 'Wrist' (Landmark 0) for Scale
    wrist = hand_landmarks.landmark[0]
    wr_x, wr_y = wrist.x * w, wrist.y * h
    
    # 3. Calculate Scaling Factor (Palm Length)
    scaling_factor = math.sqrt((m_x - wr_x)**2 + (m_y - wr_y)**2)
    if scaling_factor == 0: scaling_factor = 0.001
        
    norm_list = []

    # 4. Normalize landmarks relative to the PALM CENTER (9)
    for i in range(21):
        lm = hand_landmarks.landmark[i]
        lm_x, lm_y = lm.x * w, lm.y * h
        
        # Distance from point 'i' to Center '9'
        raw_dist = math.sqrt((lm_x - m_x)**2 + (lm_y - m_y)**2)
        
        norm_dist = raw_dist / scaling_factor
        norm_list.append(round(norm_dist, 4))
        
    return norm_list

def get_cartesian_landmarks(hand_landmarks, h, w):
    cartesian_coords = {}
    for i in range(21):
        lm = hand_landmarks.landmark[i]
        cartesian_coords[i] = (int(lm.x * w), int(lm.y * h))
    return cartesian_coords

def get_refined_data(hand_landmarks, h, w):
    global ema_norm_data, ema_global_data
    
    # 1. Capture Raw Data
    raw_norm = get_normalized_landmarks(hand_landmarks, h, w)
    raw_global = get_cartesian_landmarks(hand_landmarks, h, w)
    
    # 2. INITIALIZATION CHECK (Prevents "Slide-in" effect)
    # Check index 9 (Anchor). In new logic, norm dist of 9 is always 0.0.
    # So we check index 0 (Wrist), which should be exactly 1.0.
    # If previous state is 0.0, it's uninitialized.
    if ema_norm_data[0] == 0.0: 
        ema_norm_data = list(raw_norm)
        ema_global_data = raw_global
        return ema_norm_data, ema_global_data
    
    # 3. Apply EMA to Normalized Data (List)
    for i in range(21):
        ema_norm_data[i] = (ALPHA_NORM * raw_norm[i]) + ((1 - ALPHA_NORM) * ema_norm_data[i])
        
    # 4. Apply EMA to Global Coordinates (Dict)
    for i in range(21):
        curr_x, curr_y = raw_global[i]
        prev_x, prev_y = ema_global_data[i]
        
        new_x = (ALPHA_GLOBAL * curr_x) + ((1 - ALPHA_GLOBAL) * prev_x)
        new_y = (ALPHA_GLOBAL * curr_y) + ((1 - ALPHA_GLOBAL) * prev_y)
        ema_global_data[i] = (int(new_x), int(new_y))
        
    return ema_norm_data, ema_global_data