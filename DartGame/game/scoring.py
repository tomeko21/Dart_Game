import math
from config.consts import *

#do poprawy wyskalowac z tarcza (najpierw poprawic zdjecie tarczy)
def calculate_score(x, y, board_center):
    cx, cy = board_center
    d = math.hypot(x-cx, y-cy)
    
    if d <= R_BULLSEYE: return 50
    if d <= R_OUTER_BULL: return 25
    if d > R_OUTER_RING_END: return 0
    
    ang = (math.degrees(math.atan2(y-cy, x-cx)) + 99) % 360
    val = SECTOR_VALUES[int(ang//18)]
    
    if R_INNER_RING_START <= d <= R_INNER_RING_END: return val * 3
    if R_OUTER_RING_START <= d <= R_OUTER_RING_END: return val * 2
    return val