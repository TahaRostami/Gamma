import matplotlib.pyplot as plt
import tkinter as tk

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

def convert_to_3cnf(cnf_formula):
    """ convert the given CNF formula into 3CNF

    >>> convert_to_3cnf(cnf_formula=[[-1, 2, 3], [-2, 4, -5], [1, 2, 5, -2, 4]])
    [[-1, 2, 3], [-2, 4, -5], [1, 2, 6], [-6, 5, 7], [-7, -2, 4]]

    :param cnf_formula: CNF formula
    :return: 3-CNF formula
    """
    def new_variable():
        nonlocal var_counter
        var_counter += 1
        return var_counter

    def split_clause(clause):
        if len(clause) <= 3:
            return [clause]
        else:
            v=new_variable()
            return [[clause[0], clause[1], v]] + split_clause([-v]+clause[2:])

    var_counter = get_top_id(cnf_formula)
    cnf_3 = []
    for clause in cnf_formula:
        cnf_3 += split_clause(clause)

    return cnf_3

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

class QueenDomVizTool:
    """ A simple interactive visual tool for Queen Domination Problem. Left click for adding a queen, and Right click for
    removing the queen.
    """
    def __init__(self,n=8,cell_size=50,colors=["white", "lightgray"],piece_symbol='♛',numbering="row_major",attacked_squares_color="red"):
        """
        :param n: number of rows in the chessboard
        :param cell_size: size of each square
        :param colors: light and dark colors
        :param piece_symbol: text to represent the piece
        :param numbering: 'row_major', 'col_major', or None
        :param attacked_squares_color: a color or None
        """

        self.queens = set()
        self.attacked_squares = set()
        self.board_size = n

        self._cell_size = cell_size
        self._colors=colors
        self._piece_symbol=piece_symbol
        self._numbering=numbering
        self._attacked_squares_color=attacked_squares_color

        self._root = tk.Tk()
        self._root.title("Queen Domination Problem")

        self._canvas = tk.Canvas(self._root, width=self.board_size * self._cell_size, height=self.board_size * self._cell_size)
        self._canvas.pack()

        self._canvas.bind("<Button-1>", self._place_queen)
        self._canvas.bind("<Button-3>", self._remove_queen)

        self._statistics_label = tk.Label(self._root, text="Statistics")
        self._statistics_label.pack()
        self._board_size_label = tk.Label(self._root, text="\nBoard Size (n):")
        self._board_size_label.pack()
        self._board_size_entry = tk.Entry(self._root)
        self._board_size_entry.insert(0, str(self.board_size))
        self._board_size_entry.pack()

        self._change_size_button = tk.Button(self._root, text="Change Size", command=self._change_board_size)
        self._change_size_button.pack()

        self._reset_button = tk.Button(self._root, text="Reset Board", command=self._reset_board)
        self._reset_button.pack()

    def _place_queen(self,event):
        x, y = event.x // self._cell_size, event.y // self._cell_size
        if (x, y) not in self.queens:
            self.queens.add((x, y))
            self._update_attacked_squares()

    def _remove_queen(self,event):
        x, y = event.x // self._cell_size, event.y // self._cell_size
        if (x, y) in self.queens:
            self.queens.remove((x, y))
            self._update_attacked_squares()

    def _update_attacked_squares(self):
        self.attacked_squares.clear()
        for queen in self.queens:
            x, y = queen
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if i == x or j == y or abs(i - x) == abs(j - y):
                        self.attacked_squares.add((i, j))
        self._draw_board()

    def _reset_board(self):
        self.queens.clear()
        self.attacked_squares.clear()
        self._draw_board()

    def _change_board_size(self):
        new_size = int(self._board_size_entry.get())
        if new_size != self.board_size:
            self.board_size = new_size
            self._canvas.config(width=self.board_size * self._cell_size, height=self.board_size * self._cell_size)
            self._reset_board()

    def _draw_board(self):
        self._canvas.delete("all")
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = self._colors[(i + j) % 2]
                self._canvas.create_rectangle(i * self._cell_size, j * self._cell_size, (i + 1) * self._cell_size, (j + 1) * self._cell_size,
                                              fill=color)
                if (i, j) in self.queens:
                    self._canvas.create_text(i * self._cell_size + self._cell_size // 2, j * self._cell_size + self._cell_size // 2, text=self._piece_symbol,
                                             font=("Helvetica", self._cell_size // 2), fill="black")
                else:

                    if self._numbering is not None:
                        if self._numbering== "row_major":
                            idx = self.board_size * j + i + 1
                        elif self._numbering== "col_major":
                            idx = self.board_size * i + j + 1
                        else: raise Exception()
                        self._canvas.create_text(i * self._cell_size + self._cell_size // 2, j * self._cell_size + self._cell_size // 2, text=idx,
                                                 font=("Helvetica", self._cell_size // 4), fill="black")
                    if self._attacked_squares_color is not None and (i, j) in self.attacked_squares:
                       self._canvas.create_rectangle(i * self._cell_size, j * self._cell_size, (i + 1) * self._cell_size, (j + 1) * self._cell_size, fill=self._attacked_squares_color, stipple="gray12")

        self._statistics_label.config(text=f"\n#queens:{len(self.queens)}\n#squares:{self.board_size * self.board_size}\n#empty squares: {self.board_size * self.board_size - len(self.attacked_squares)}\n#attacked squares: {len(self.attacked_squares)}")

    def show(self):
        """ execute the program and open-up the visualization tool
        """
        self._update_attacked_squares()
        self._root.mainloop()


if __name__=="__main__":
    QueenDomVizTool(n=12).show()