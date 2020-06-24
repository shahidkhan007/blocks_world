# blocks_world
A system that can answer questions about its behavior using a goal tree

It is able to do that by creating a goal tree.
A goal tree is basically a container that contains the actions that an agent has to take to achieve its goal.
the goal tree goes from the goal the the top of the hierarchy down to the last action it has to take. well the order can be reverse too
but chain shouldn't be broken/shuffled I guess.

In this particular case there is a table (Rows x Columns) filled with boxes. 
The agent(A hand in this case) is told to put one block on top of another block. The agent first clears the top of Box 1, then that of Box 2 and then moves
Box 1 to the top of Box 2, creating a goal tree along the way. 

The agent/system is able to answer 2 types of questions:
1. Why it did what it did, and
2. How it did what it did

since this program was built to demonstrate the use of goal trees, itsNLP abilities are not very high level, you will have to use a
specific pattern of asking your questions for the agent to understand it.

Questions you can ask:

why did you move 'box_name' to '[some_row_number,some_col_number_without_a_space_in_btw_the_comma]'

how did you put 'box_name_1' on top of 'box_name_2'

why did you clear the top of 'box_name'

how did you clear the top of 'box_name'


