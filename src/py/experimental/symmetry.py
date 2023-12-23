import matplotlib.pyplot as plt

def display_chessboards(chessboards, dark_color='yellow', light_color='white'):
    """It plots and displays the given chess boards graphically

    :param chessboards: a list of chess boards, where each board is a list with n items,
                        and each item is a list of size n
    :param dark_color: color of dark squares in the chess board
    :param light_color: color of light squares in the chess board
    :return: currently, it does not return anything, but just plots the boards
    """
    colors = [dark_color, light_color]
    fig, axs = plt.subplots(2, 4, figsize=(12, 6))  # 2 rows, 4 columns for 8 subplots

    for board_index, board in enumerate(chessboards):
        row_index, col_index = divmod(board_index, 4)
        width, height = 1.0 / len(board), 1.0 / len(board)
        tbl = axs[row_index, col_index].table(cellText=board, loc='center', cellLoc='center')

        for i in range(len(board)):
            for j in range(len(board)):
                idx = [j % 2, (j + 1) % 2][i % 2]
                color = colors[idx]
                tbl.add_cell(i, j, width, height, text=board[i][j], loc='center', facecolor=color)

        for x in range(len(board)):
            # Column Labels
            tbl.add_cell(-1, x, width, height / 2, text=x + 1, loc='center', edgecolor='none', facecolor='none')
            # Row Labels
            tbl.add_cell(x, -1, width / 2, height, text=x + 1, loc='center', edgecolor='none', facecolor='none')

        axs[row_index, col_index].axis('off')

    plt.show()
def plot_syms(P,n):

   I=[['Q' if (i*n+j) in P else '' for j in range(n)] for i in range(n)]
   C1 = [['Q' if ((n-1-j) * n + i) in P else '' for j in range(n)] for i in range(n)]
   C2 = [['Q' if ((n-1-i) * n + (n-1-j)) in P else '' for j in range(n)] for i in range(n)]
   C3 = [['Q' if ((j) * n + (n-1-i)) in P else '' for j in range(n)] for i in range(n)]
   D1 = [['Q' if ((n-1-j) * n + (n-1-i)) in P else '' for j in range(n)] for i in range(n)]
   D2 = [['Q' if ((j) * n + (i)) in P else '' for j in range(n)] for i in range(n)]
   R1 = [['Q' if ((n-1-i) * n + (j)) in P else '' for j in range(n)] for i in range(n)]
   R2 = [['Q' if ((i) * n + (n-1-j)) in P else '' for j in range(n)] for i in range(n)]
   display_chessboards([I,C1,C2,C3,D1,D2,R1,R2])



if __name__=="__main__":
    plot_syms([0, 5,45], 10)