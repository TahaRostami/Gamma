import matplotlib.pyplot as plt

def display_chessboard(board,dark_color='yellow',light_color='white'):
    """It plots and displays the given chess board graphically

    >>> display_chessboard([['','',''],['','Q',''],['','','']])

    :param board: a list with n items in which each item is a list of size n
    :param dark_color: color of dark squares in the chess board
    :param light_color: color of light squares in the chess board
    :return: currently, it does not return anything, but just plots the board
    """
    colors = [dark_color, light_color]
    fig, ax = plt.subplots()
    width, height = 1.0 / len(board), 1.0 / len(board)
    tbl = plt.table(cellText=board, loc='center', cellLoc='center')
    for i in range(len(board)):
        for j in range(len(board)):
            idx = [j % 2, (j + 1) % 2][i % 2]
            color = colors[idx]
            tbl.add_cell(i, j, width, height, text=board[i][j], loc='center', facecolor=color)
    for x in range(len(board)):
        # Column Labels
        tbl.add_cell(-1, x, width, height / 2, text=x+1, loc='center', edgecolor='none', facecolor='none')
        # Row Labels
        tbl.add_cell(x, -1, width / 2, height, text=x+1, loc='center', edgecolor='none', facecolor='none')
    ax.add_table(tbl)

    ax.axis('off')
    plt.show()
def get_top_id(clauses):
    """ Given a list of clauses, it returns the maximum id

    Some functionalities in PySAT require introducing new variables, and for this reason it sometimes takes top id
    as the input while providing access to variables' top id using nv(i.e., top id). However,
    according to my experiments, it seems that there is a bug, or I do not know who I should deal with this.
    Thus, this function is an alternative for that PySAT's functionality.

    >>> get_top_id([[-1, 2, -3], [1, 4, -2],[-5,-3,-2],[-1,-5,4]])
    5

    :param clauses: a list of lists
    :return:maximum id
    """
    return max([max([abs(item) for item in c]) for c in clauses])
