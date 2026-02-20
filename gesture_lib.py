import math

# ==========================================
#  CONSTANTS & IDs
# ==========================================

ID_THUMBS_UP = 0
ID_INDEX_U      = 1
ID_VICTORY_U    = 2
ID_NICE         = 3
ID_QUAD         = 4
ID_OPEN_PALM    = 5
ID_INDEX_D      = 6
ID_INDEX_L      = 7
ID_INDEX_R      = 8
ID_VICTORY_D    = 9
ID_VICTORY_L    = 10
ID_VICTORY_R    = 11
ID_SPIDEY       = 12

# =========================
#  GESTURE DEFINITIONS
# =========================

def thumbs_up_fx(norm_dict, global_coords, queue_fx):
    
    if norm_dict[8] < 0.5 and norm_dict[12] < 0.5 and norm_dict[16] < 0.5 and norm_dict[20] < 0.7 and norm_dict[4] > 1:
        queue_fx(ID_THUMBS_UP)

def index_up_fx(norm_dict, global_coords, queue_fx):
    
    if norm_dict[8] > 0.8 and all(norm_dict[i] < 0.7 for i in [12, 16, 20]) and norm_dict[4] < 0.5 and global_coords[5][1] > global_coords[8][1]:
        queue_fx(ID_INDEX_U)

def victory_fx(norm_dict, global_coords, queue_fx):
   
    if all(norm_dict[i] > 0.8 for i in [8, 12]) and all(norm_dict[i] < 0.6 for i in [16, 20])  and norm_dict[4] < 0.5 and global_coords[5][1] > global_coords[8][1]:
        queue_fx(ID_VICTORY_U)

def nice_fx(norm_dict, global_coords, queue_fx):

    if all(norm_dict[i] < 0.7 for i in [8]) and all(norm_dict[i] > 0.8 for i in [12, 16, 20]):
        queue_fx(ID_NICE)

def quad_fx(norm_dict, global_coords, queue_fx):
    
    if all(norm_dict[i] > 0.8 for i in [8, 12, 16, 20]) and norm_dict[4] < 0.5:
        queue_fx(ID_QUAD)

def open_palm_fx(norm_dict, global_coords, queue_fx):
    
    if all(norm_dict[i] > 0.8 for i in [8, 12, 16, 20]) and norm_dict[4] > 1:
        queue_fx(ID_OPEN_PALM)

def spidey_fx(norm_dict, global_coords, queue_fx):

    if all(norm_dict[i] > 0.8 for i in [8, 20]) and all(norm_dict[i] < 0.5 for i in [4, 12, 16]):
        queue_fx(ID_SPIDEY)

def index_down_fx(norm_dict, global_coords, queue_fx):

    if norm_dict[8] > 0.8 and all(norm_dict[i] < 0.7 for i in [12, 16, 20]) and norm_dict[4] < 0.5 and global_coords[5][1] > global_coords[8][1]:
        queue_fx(ID_INDEX_U)

def index_left_fx(norm_dict, global_coords, queue_fx):

    dx = global_coords[8][0] - global_coords[5][0] ; dy = global_coords[8][1] - global_coords[5][1]
    horizontal = abs(dx)>abs(dy)
    if norm_dict[8] > 0.8 and all(norm_dict[i] < 0.7 for i in [12, 16, 20]) and norm_dict[4] < 0.5 and horizontal and dx<0 :
        queue_fx(ID_INDEX_L)

def index_right_fx(norm_dict, global_coords, queue_fx):

    dx = global_coords[8][0] - global_coords[5][0] ; dy = global_coords[8][1] - global_coords[5][1]
    horizontal = abs(dx)>abs(dy)
    if norm_dict[8] > 0.8 and all(norm_dict[i] < 0.7 for i in [12, 16, 20]) and norm_dict[4] < 0.5 and horizontal and dx>0:
        queue_fx(ID_INDEX_R)

def victory_down_fx(norm_dict, global_coords, queue_fx):

    dx = global_coords[8][0] - global_coords[5][0] ; dy = global_coords[8][1] - global_coords[5][1]
    horizontal = abs(dx)>abs(dy)
    if all(norm_dict[i] > 0.8 for i in [8, 12]) and all(norm_dict[i] < 0.6 for i in [16, 20])  and norm_dict[4] < 0.5 and global_coords[5][1] < global_coords[8][1]:
        queue_fx(ID_VICTORY_D) 


def victory_left_fx(norm_dict, global_coords, queue_fx):

    dx = global_coords[8][0] - global_coords[5][0] ; dy = global_coords[8][1] - global_coords[5][1]
    horizontal = abs(dx)>abs(dy)
    if all(norm_dict[i] > 0.8 for i in [8, 12]) and all(norm_dict[i] < 0.6 for i in [16, 20])  and norm_dict[4] < 0.5 and horizontal and dx<0:
        queue_fx(ID_VICTORY_L)

def victory_right_fx(norm_dict, global_coords, queue_fx):

    dx = global_coords[8][0] - global_coords[5][0] ; dy = global_coords[8][1] - global_coords[5][1]
    horizontal = abs(dx)>abs(dy)
    if all(norm_dict[i] > 0.8 for i in [8, 12]) and all(norm_dict[i] < 0.6 for i in [16, 20])  and norm_dict[4] < 0.5 and horizontal and dx>0:
        queue_fx(ID_VICTORY_R)