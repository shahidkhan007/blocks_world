import re
from .box import Box


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
                    final_answer = f"By first clearing the top of {components[1]} and then of {components[0]}" \
                        f" and then moving {components[0]} to the top of {components[1]}"

            elif obj == 'clt' and search_term in self.goal_tree:
                final_answer = "By moving "
                l = self.goal_tree[searched_item[1] + 1:]  # part of the goal tree where our solution exists

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

                if index + 1 == len(self.goal_tree):
                    last_move = True

                elif self.goal_tree[index + 1][0] == 'put_on':
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