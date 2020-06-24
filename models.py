import numpy as np
import pygame
import re
pygame.font.init()

color = {
    'green': (0, 255, 0),
    'bg': (201, 145, 127),
    'red': (255, 0, 0),  
}

box_color = {
    'crimson': (237, 20, 61),
    'blue': (0, 129, 255),
    'dark_purple': (0, 19, 36),
    'sky_orange': (200, 172, 168),
    'orange': (245, 67, 27),
    'blueish' : (42, 39, 117),
    'pinky' : (218, 66, 136)
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
        self.goal_tree = []
        self.clock = pygame.time.Clock()

        # The xy format is a format in which values mean (got this units in x-axis, go this units in y-axis) while row x column format means
        # (go this many rows in the table, go this many columns in the table)

    def get_col(self, column):
        """Returns the requested column from the table"""
        return self.table[:, column].copy()   

    def get_row(self, row): 
        """Returns the requested row from the table"""
        return self.table[row].copy()
    
    def get_element(self, element: tuple or list or np.array):
        """Returns the requested element from the table"""
        return self.table[element[0], element[1]]
    
    def get_index(self, element):
        """Returns the index for element from the table in Row x Column format"""
        for i, row in enumerate(self.table):
            for j, e in enumerate(row):
                if e == element:
                    return (i, j)
    
    def put(self, box, location, insert=False):
        """takes the box from its current location if available
         and puts it at location in the table if possible. Returns nothing. if insert is True, the box is simply put in the table"""
        if insert:
            self.table[location[0], location[1]] = box
            return

        box_index = self.get_index(box)
        if self.table[box_index[0], box_index[1]] is None:
            raise IndexError(f"No box at {location} to carry.")
        else: self.table[box_index[0], box_index[1]] = None

        if self.table[location[0], location[1]] is not None:
            raise IndexError(f"Another box: {self.table[location[0], location[1]]} already at {location}.")
        else: self.table[location[0], location[1]] = box
    
    def create_table_structure(self):
        """Creates the structure of the table and returns it for the render function to render it"""
        height_1 = self.box_size * self.size[0]
        width_1 = self.box_size * self.size[1]

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
        step_size = 5
        for _ in range(0, magnitude, step_size):
            self.clock.tick(300)
            # print(self.clock.get_fps())
            if self.in_hand:  # if the hand is holding something that will move with the Hand
                self.in_hand.box_motion_bias_x += step_size * direction_int[0]
                self.in_hand.box_motion_bias_y += step_size * direction_int[1]

            self.hand_motion_bias += step_size * direction_int
            self.surface.fill(color['bg'])
            Box.render_all_boxes()
            self.render()
            pygame.display.update()
        
        # This is the motion of hand in the grid/table via hand_loc. The above is graphical motion
        x = int(magnitude / self.box_size * direction_int[0])
        y = int(magnitude / self.box_size * direction_int[1])
        self.hand_loc += np.array([x, y])
    
    def attach_to_hand(self, box):
        """Takes a box from the table and puts it in in_hand variable"""
        self.in_hand = box
        self.table[box.index[0], box.index[1]] = None
   
    def un_attach_from_hand(self):
        """Takes the box in in_hand variable and puts it back in the table at location hand_loc.
        Remember: this function zeros all the motion biases and updates the loc"""
        self.table[self.hand_loc[1]-1, self.hand_loc[0]] = self.in_hand
        self.in_hand.loc = self.hand_loc
        self.in_hand = None

    def pick_up(self, box):
        """Picks up a box"""
        box_loc = self.get_index(box)  # location in (row x column) format
        box_loc = (box_loc[1], box_loc[0])  # location in (x-axis, y-axis) format

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

    def find_space(self, goal_seq):
        """Finds an empty slot in the table such that the slot is not on of the ones in goal_seq(Goal sequence).
        Goal sequence has two elements. column numbers of the places where we dont want the box to go.
        Returns the empty slot in (Row x Column) format"""
        for i in range(self.size[1]):
            if i in goal_seq:
                continue
            column = self.get_col(i)
            for j, element in enumerate(column):
                if element is not None:
                    if j == 0:
                        break
                    return (j-1, i)

                elif j == len(column)-1:
                    return (j, i)
        else:
            raise Exception("No more space!")

    def clear_top(self, box, goal_sequence):
        """This function clears the top of box graphically and logically.
        First it find all boxes above it, finds space for them to move to and then moves. it dosent move boxes to column numbers
         in goal sequence because other useful blocks will go there"""
        self.goal_tree.append(['clt', str(box)])  # An entry in the goal tree to later be able to track the actions
        box_column = list(self.get_col(box.index[1]))
        box_row = box_column[:box.index[0]]
        boxes_above = [x for x in box_row if x]
        for b in boxes_above:
            self.pick_up(b)
            space = self.find_space(goal_sequence)
            self.put_down(space)
            self.goal_tree.append(['move', [str(b), str(list(space))]])  # What happened in this loop is called a move, it can be a different method and this is an entry to track moves

    def put_on(self, box_1, box_2):
        """Puts box_1 on top of box_2 if possible.
        First it clears the top of box_1 and then that of box_2 and then puts box_1 on top of box_2"""
        self.goal_tree.append(['put_on', [str(box_1), str(box_2)]])
        
        goal_seq = [box_1.loc[1], box_2.loc[1]]
        # Check if box_2 is not at the top of its column
        if box_2.loc[0] == 0:
            return
        elif box_1.loc[1] == box_2.loc[1] and box_1.loc[0] < box_2.loc[0]:
            return

        try:
            # clear the top of box_2
            self.clear_top(box_2, goal_seq)

            # clear top of box_1
            self.clear_top(box_1, goal_seq)
        except Exception as e:
            print(e)
            return

        # If not, performing the move
        self.pick_up(box_1)
        self.put_down([box_2.index[0]-1, box_2.index[1]])
        self.goal_tree.append(['move', [str(box_1), str([box_2.index[0]-1, box_2.index[1]])]])

    def event_loop(self):
        """This is where all the action happens"""
        self.surface = pygame.display.set_mode((800, 600))

        self.put_on(boxes['B2'], boxes['B3'])
        interaface.question_aire()
        
        while True:
            self.clock.tick(300)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.surface.fill(color['bg'])
            Box.render_all_boxes()
            self.render()
            
            pygame.display.update()


class Box:
    size = 50
    boxes = []
    boxes_names = []
    def __init__(self, loc: tuple or list, table: Table, name=None, color=None):
        self.loc = np.array(loc)  # location of the box in table in Row x Columnn format, updated manually to allow for animation
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
            else: self.name = name
        self.boxes_names.append(self.name)
        self.table.put(self, loc, insert=True)

    def render(self):
        box = [self.pxloc[0] + self.box_motion_bias_x, self.pxloc[1] + self.box_motion_bias_y, self.size, self.size]
        pygame.draw.rect(self.table.surface, box_color[self.color], box)
        self.write_text(str(self), 24, (50, 50, 50), (self.pxloc[0]+10+self.box_motion_bias_x, self.pxloc[1]+10+self.box_motion_bias_y))
    
    @property
    def index(self):
        """Returns the immediate position of the box in the table, returns none if in hand"""
        return self.table.get_index(self)
    
    def top_is_clear(self):
        """Finds if its top is clear"""
        my_column = self.table.get_col(self.index[1])
        for b in my_column[:self.index[0]]:  # searching through the column until this box reaches to find if there is anything on top of it
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
    

class Interface:
    def __init__(self, table):
        self.table = table
        self.goal_tree = self.table.goal_tree
        self.box_names = Box.boxes_names

    def parse_question(self, question: str):
        """This method parses the queston and creates a dictionary that describes the question. Its type, objective and components"""
        parsed = {}
        question = question.lower().split(' ')

        # Determine the type of question
        if 'how' in question:
            parsed['type'] = 'how'
        elif 'why' in question:
            parsed['type'] = 'why'
        else:
            parsed['type'] = None
            return parsed
        
        # Determine the objective of the question
        if 'put' in question:
            parsed['obj'] = 'put_on'
        elif 'clear' in question and 'top' in question:
            parsed['obj'] = 'clt'
        elif parsed['type'] == 'why' and 'move' in question:
            parsed['obj'] = 'move'
        else:
            parsed['obj'] = None
            return parsed
        
        # Determine the components of the question
        components = []
        for part in question:
            if re.search(r'[bB]\d*', part):
                components.append(part.capitalize())
        if parsed['obj'] == 'move':
            for part in question:
                if re.search(r'\[\d*,\d*\]', part):
                    components.append(str(list(eval(part))))

        parsed['comps'] = components

        return parsed

    def question_aire(self):
        """this is the main method that handles all I/O with the user and uses the other methds to do its job"""
        while True:
            q = input("Question: ")
            if q == 'e' or q == 'exit':
                break
            parsed = self.parse_question(q)
            answer = self.answer_question(parsed)
            print("Answer:", answer, '\n')
    
    def search_tree(self, item, return_index=False):
        """And auxillary method to aid in answering questions by searching for item in the goal tree. when return_index = True,
        item's index in the goal tree is also returned"""
        for i, e in enumerate(self.goal_tree):
            if e == item:
                return (item, i) if return_index else item
        else:
            raise KeyError("Search term not found!")
    
    def answer_question(self, parsed_question: dict):
        """This is the method that actually answers question by taking as input a parsed question"""
        final_answer = "I didn't do that"
        try:
            obj, components, q_type = parsed_question['obj'], parsed_question['comps'], parsed_question['type']
        except KeyError:
            return "Invalid question"

        # This if statement is needed bcz the structure of items for clt and others is slightly different and it may be changed.
        if obj == 'clt':
            search_term = [obj, components[0]]
        else:
            search_term = [obj, components]

        # If the action said in parsed question is not found in the goal tree then there is no point continuing
        try:
            searched_item = self.search_tree(search_term, True)
        except KeyError:
            return final_answer
        
        # The following block comes up with an answer to all possible scenarios
        if q_type == 'how':
            if obj == 'put_on':
                if search_term in self.goal_tree:
                    final_answer = f"By first clearing the top of {components[1]} and then of {components[0]} and then moving {components[0]} to the top of {components[1]}"
            
            elif obj == 'clt' and search_term in self.goal_tree:
                final_answer = "By moving "
                l = self.goal_tree[searched_item[1]+1:]  # part of the goal tree where our solution exists

                for o, c in l:
                    if o is not 'move':
                        break
                    final_answer += f"{str(c[0])} to {str(c[1])} and "
                final_answer = final_answer[:-5]
        
        elif q_type == 'why':
            if obj == 'put_on' and search_term in self.goal_tree:
                final_answer = "Because you told me to"

            elif obj == 'clt' and search_term in self.goal_tree:
                l = self.goal_tree[:searched_item[1]]
                for o, c in reversed(l):
                    if o is 'put_on':
                        final_answer = f"To put {c[0]} on top of {c[1]}"
                        break
                    else:
                        continue
            
            elif obj == 'move':
                index = searched_item[1]
                l = self.goal_tree[:index]

                if index+1 == len(self.goal_tree):
                    last_move = True
                
                elif self.goal_tree[index+1][0] == 'put_on':
                    last_move = True
                
                else:
                    last_move = False

                for o, c in reversed(l):

                    if o == 'put_on':
                        final_answer = f"To put {c[0]} on top of {c[1]}"
                        break

                    elif o == 'clt' and last_move is False:
                        final_answer = f"To clear the top of {c}"
                        break

        return final_answer
        
        
if __name__ == "__main__":
    t = Table((200, 200), (4, 6))
    interaface = Interface(t)
    boxes = [Box((i, j), t) for i, j in [(3, 0), (3, 1), (3, 2), (2, 0), (2, 1), (2, 2), (1, 1), (1, 2), (0, 2)]]
    boxes = {str(x): x for x in boxes}
    t.event_loop()
