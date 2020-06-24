import pygame
import numpy as np
from . import box_color
from .table import Table

class Box:
    size = 50
    boxes = []
    boxes_names = []

    def __init__(self, loc: tuple or list, table: Table, name=None):
        self.loc = np.array(
            loc)  # location of the box in table in Row x Columnn format, updated manually to allow for animation
        self.loc_xy = np.array([self.loc[1], self.loc[0]])  # location of the box in table in x-axis, y-axis format
        self.pxloc = self.size * self.loc_xy + table.loc  # pixel location of the box in table in Row x Columnn format
        self.table = table
        self.box_motion_bias_x = 0
        self.box_motion_bias_y = 0
        self.box_motion_bias = np.array((self.box_motion_bias_x, self.box_motion_bias_y))
        self.boxes.append(self)
        self.color = np.random.choice(list(box_color.keys()))

        if name is None:
            self.name = self.boxes_names[-1] + 1 if len(self.boxes_names) > 0 else 1
        else:
            if name in self.boxes_names:
                self.name = self.boxes_names[-1] + 1
                print(f"Box with name {name} already exists thus it was named {self.name}")
            else:
                self.name = name
        self.boxes_names.append(self.name)
        self.table.put(self, loc, insert=True)

    def render(self):
        box = [self.pxloc[0] + self.box_motion_bias_x, self.pxloc[1] + self.box_motion_bias_y, self.size, self.size]
        pygame.draw.rect(self.table.surface, box_color[self.color], box)
        self.write_text(str(self), 24, (50, 50, 50),
                        (self.pxloc[0] + 10 + self.box_motion_bias_x, self.pxloc[1] + 10 + self.box_motion_bias_y))

    @property
    def index(self):
        """Returns the immediate position of the box in the table, returns none if in hand"""
        return self.table.get_index(self)

    def top_is_clear(self):
        """Finds if its top is clear"""
        my_column = self.table.get_col(self.index[1])
        for b in my_column[:self.index[
            0]]:  # searching through the column until this box reaches to find if there is anything on top of it
            if b is not None:
                return False
        else:
            return True

    def write_text(self, text: str, size: int, color: tuple, loc: tuple):
        font = pygame.font.SysFont("comicsansms", size)
        text = font.render(text, True, color)
        self.table.surface.blit(text, loc)

    @classmethod
    def render_all_boxes(cls):
        for box in cls.boxes:
            box.render()

    def __repr__(self):
        return "B" + str(self.name)