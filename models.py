import numpy as np
import pygame

color = {
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'blue': (0, 0, 255),
    'red': (255, 0, 0)
}

class Table:
    def __init__(self, loc, size):
        self.size = np.array(size)  # size of the table in Rows x Columns
        self.box_size = 50  # size in pixels
        self.pxsize = self.box_size * self.size  # size of the table in pixels
        self.loc = np.array(loc)  # location of the table in pixels
        self.table = np.empty(size, dtype=object)  # the 2D np array that is the table
        self.ylim = self.loc[1]
        self.xlim = self.loc[0]
        self.surface = None
        self.in_hand = None  # shows weather there is something in the hand
        self.hand_motion_bias_x = 0  # these var is used to move the hand
        self.hand_motion_bias_y = 0
        self.hand_motion_bias = (self.hand_motion_bias_x, self.hand_motion_bias_y)
        self.hand_loc = np.array((0, 0))  # means its 50 pixels above the table on its first column

        # The xy format is a format in which values mean (got this units in x-axis, go this units in y-axis) while row x column format means
        # (go this many rows in the table, go this many columns in the table)

    def get_col(self, column):
        """Returns the requested column from the table"""
        return self.table[:, column]   

    def get_row(self, row): 
        """Returns the requested row from the table"""
        return self.table[row]
    
    def get_element(self, element: tuple or list or np.array):
        """Returns the requested element from the table"""
        return self.table[element[0], element[1]]
    
    def get_index(self, element):  # Also means loc/ocation in the table
        """Returns the index for element from the table in Row x Column format"""
        for i, row in enumerate(self.table):
            for j, e in enumerate(row):
                if e == element:
                    return (i, j)
    
    def put(self, box, location, insert=False):
        """takes the box from its current location if available
         and puts it at location in the table if possible. Returns nothing. if insert is True, the box is simply put in the table"""
        if insert:
            self.table[location] = box
            return

        box_index = self.get_index(box)
        if self.table[box_index] is None:
            raise IndexError(f"No box at {location} to carry.")
        else: self.table[box_index] = None

        if self.table[location] is not None:
            raise IndexError(f"Another box: {self.table[location]} already at {location}.")
        else: self.table[location] = box
    
    def create_table_structure(self):
        """Creates the structure of the table and returns it for the render function to render it"""
        height_1 = self.box_size * self.size[1]
        width_1 = self.box_size * self.size[0]

        line_1 = [self.loc, (self.loc[0], self.loc[1] + height_1)]  # [start_pos, end_pos]

        line_2 = [line_1[1], (line_1[1][0] + width_1, line_1[1][1])]

        line_3 = [line_2[1], (self.loc[0] + width_1, self.loc[1])]

        return line_1, line_2, line_3
    
    def render(self):
        """Renders the Table and the Hand to self.surface"""
        # Table
        table_line_1, table_line_2, table_line_3 = self.create_table_structure()
        pygame.draw.line(self.surface, color['green'], *table_line_1, 4)
        pygame.draw.line(self.surface, color['green'], *table_line_2, 4)
        pygame.draw.line(self.surface, color['green'], *table_line_3, 4)

        # Hand
        hand_line_1, hand_line_2, hand_line_3, hand_line_4 = self.create_hand_structure()
        pygame.draw.line(self.surface, color['red'], *hand_line_1, 4)
        pygame.draw.line(self.surface, color['red'], *hand_line_2, 4)
        pygame.draw.line(self.surface, color['red'], *hand_line_3, 4)
        pygame.draw.line(self.surface, color['red'], *hand_line_4, 4)
    
    def create_hand_structure(self):
        """Creates the structure of hand and returns it for the render function to render it"""
        height_1 = 25
        height_2 = 25
        width_1 = 50
        height = height_1 + height_2

        line_1 = [ (self.loc[0] + int(width_1/2), self.loc[1] - self.box_size - height),
         (self.loc[0] + int(width_1/2), self.loc[1] - self.box_size - height_2) ]
        line_1 = np.array(line_1)
        line_1 += np.array(self.hand_motion_bias)

        line_2 = np.array([ (line_1[0][0] - int(width_1/2), line_1[1][1]), (line_1[0][0] + int(width_1/2), line_1[1][1]) ])

        line_3 = np.array([ line_2[0], (line_2[0][0], line_2[0][1] + height_2) ])
        line_4 = np.array([ line_2[1], (line_2[1][0], line_2[1][1] + height_2) ])
        # All these lines are converted to arrays so that they can be multiplied by other arrays or scalars

        return line_1, line_2, line_3, line_4

    def move_hand(self, magnitude, direction):
        if direction in ['R', 'r']:
            direction_int = (1, 0)  # Means add to bias x but not y
        elif direction in ['L', 'l']:
            direction_int = (-1, 0)  # Means subtract from bias x but not y
        elif direction in ['U', 'u']:
            direction_int = (0, -1)
        elif direction in ['D', 'd']:
            direction_int = (0, 1)
        
        direction_int = np.array(direction_int)
        step_size = 1
        for _ in range(0, magnitude, step_size):
            if self.in_hand:  # if the hand is holding something that will move with the Hand
                self.in_hand.box_motion_bias_x += step_size * direction_int[0]
                self.in_hand.box_motion_bias_y += step_size * direction_int[1]

            self.hand_motion_bias += step_size * direction_int
            self.surface.fill(color['black'])
            Box.render_all_boxes()
            self.render()
            pygame.display.update()
        
        # This is the motion of hand in the grid/table via hand_loc. The above is graphical motion
        x = int(magnitude / self.box_size * direction_int[0])
        y = int(magnitude / self.box_size * direction_int[1])
        self.hand_loc += np.array([x, y])
    
    def attach_to_hand(self, box):
        """Takes a box from the table and puts it in in_hand variable"""
        self.table[box.loc] = None
        self.in_hand = box
    
    def un_attach_from_hand(self):
        """Takes the box in in_hand variable and puts it back in the table at location hand_loc.
        Remember: this function zeros all the motion biases and updates the loc"""
        self.table[self.hand_loc] = self.in_hand
        self.in_hand.loc = self.hand_loc
        self.in_hand = None

    def pick_up(self, box):
        """Picks up a box"""
        box_loc = self.get_index(box)
        x = self.box_size * (box_loc[0] - self.hand_loc[0])  # got this magnitude in direction dir1
        dir1 = 'R' if x >= 0 else 'L'
        x = abs(x)
        y = 75 + self.box_size * box_loc[1]
        dir2 = 'D'
        y = abs(y)
        self.move_hand(x, dir1)
        self.move_hand(y, dir2)
        self.attach_to_hand(box)
        self.move_hand(y, 'U')
    
    def put_down(self, location):
        """Puts down the box in in_hand variable at hand_loc"""
        location = [location[1], location[0]]  # Converting co-ordinates from row x column to (x-axis, y-axis)
        if self.in_hand is None:
            raise ValueError("No Box in hand to move!")

        x = self.box_size * (location[0] - self.hand_loc[0])
        dir1 = 'R' if x >= 0 else 'L'
        x = abs(x)

        y = 75 + self.box_size * location[1]
        dir2 = 'D'
        y = abs(y)

        self.move_hand(x, dir1)
        self.move_hand(y, dir2)
        self.un_attach_from_hand()
        self.move_hand(y, 'U')

    def event_loop(self):
        self.surface = pygame.display.set_mode((800, 600))
        # self.move_hand(75, 'D')
        # self.attach_to_hand(Box.boxes[0])
        # self.move_hand(75, 'U')
        # self.move_hand(50, 'R')
        # self.move_hand(75, 'D')
        # self.un_attach_from_hand(Box.boxes[0])
        # self.move_hand(75, 'U')
        # self.move_hand(50, 'L')
        self.move_hand(100, 'R')
        self.pick_up(Box.boxes[0])
        self.put_down([3, 5])
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.surface.fill(color['black'])
            Box.render_all_boxes()
            self.render()
            
            pygame.display.update()


class Box:
    size = 50
    boxes = []
    boxes_names = []
    def __init__(self, loc: tuple or list, table: Table, name=None):
        self.loc = np.array(loc)  # location of the box in table in Row x Columnn format, updated manually to allow for animation
        self.loc_xy = np.array([self.loc[1], self.loc[0]])  # location of the box in table in x-axis, y-axis format
        self.pxloc = self.size * self.loc_xy + table.loc  # pixel location of the box in table in Row x Columnn format
        self.table = table
        self.box_motion_bias_x = 0
        self.box_motion_bias_y = 0
        self.box_motion_bias = np.array((self.box_motion_bias_x, self.box_motion_bias_y))
        self.boxes.append(self)
        if name is None:
            self.name = self.boxes_names[-1] + 1 if len(self.boxes_names) > 0 else 1
        else: 
            if name in self.boxes_names:
                self.name = self.boxes_names[-1] + 1
                print(f"Box with name {name} already exists thus it was named {self.name}")
            else: self.name = name
        self.boxes_names.append(self.name)
        self.table.put(self, loc, insert=True)

    def render(self):
        box = [self.pxloc[0] + self.box_motion_bias_x, self.pxloc[1] + self.box_motion_bias_y, self.size, self.size]
        pygame.draw.rect(self.table.surface, color['blue'], box)
    
    @property
    def index(self):
        """Return s the immediate position of the box in the table, returns none if in hand"""
        return self.table.get_index(self)
    
    def top_is_clear(self):
        """Finds if its top is clear"""
        my_column = self.table.get_col(self.index[1])
        for b in my_column[:self.index[0]]:  # searching through the column until this box reaches to find if there is anything on top of it
            if b is not None:
                return False
        else:
            return True
    
    def find_space(self, goal_seq):
        """Finds an empty slot in the table such that the slot is not on of the ones in goal_seq(Goal sequence)"""
        

    @classmethod
    def render_all_boxes(cls):
        for box in cls.boxes:
            box.render()
    
    def __repr__(self):
        return "Box " + str(self.name)
    
    

if __name__ == "__main__":
    t = Table((200, 200), (6, 4))
    boxes = [Box((i, j), t) for i, j in [(0, 0), (1, 0)]]
    # print(t.table)
    # print(boxes[0].top_is_clear())
    t.event_loop()
    # TODO Figure out the actual move of hand from hand_loc to some other co-ordinates in the move_hand function
