import pygame
from itertools import permutations
from blocks_world.table import Table
from blocks_world.interface import Interface
from blocks_world.box import Box
pygame.font.init()

        
if __name__ == "__main__":
    t = Table((200, 200), (4, 6))
    interaface = Interface(t)
    # boxes = [Box((i, j), t) for i, j in [(3, 0), (3, 1), (3, 2), (2, 0), (2, 1), (2, 2), (1, 1), (1, 2), (0, 2)]]
    boxes = [Box((i, j), t) for i in range(4) for j in range(6)]
    boxes = {str(x): x for x in boxes}
    t.event_loop(interaface, boxes)
