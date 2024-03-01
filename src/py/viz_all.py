import math
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

def display_chessboard_heatmap(ax, chessboard, n):
    # Reshape the chessboard to a 2D array
    chessboard_matrix = np.array(chessboard).reshape(n, n)
    im = ax.imshow(chessboard_matrix, cmap='hot', interpolation='nearest')
    ax.set_title(f'Chessboard {n}x{n}')
    ax.axis('off')
    return im

def parse_chessboard(file_content):
    lines = file_content.strip().split('\n')
    parsed_boards = []

    for line in lines:
        if ':' in line or '-' in line or '=' in line:
            continue
        parsed_boards.append(line.split()[1:])

    return parsed_boards

n = int(sys.argv[1])
gamma = int(sys.argv[2])
base_path = ""#"E:\\shared\\ga_parallel\\"
files = [f"all_{n}_{gamma}.txt"]

res = {}
for i, file_path in enumerate(files):
    splited = file_path.split('_')
    n, gamma = int(splited[1]), int(splited[2].replace('.txt', ''))
    res[n] = {}

for i, file_path in enumerate(files):
    splited = file_path.split('_')
    n, gamma = int(splited[1]), int(splited[2].replace('.txt', ''))
    with open(base_path + file_path, "r") as f:
        boards = parse_chessboard(f.read())
        for j, board in enumerate(boards, start=1):
            P = sorted(map(int, board))
            k = ' '.join(map(str, P))
            if k not in res[n]:
                res[n][k] = 0
            res[n][k] += 1

display_boards = []
for k, v in res.items():
    display_boards.append([0] * (k * k))
    for k2 in res[k]:
        for idx in k2.split(' '):
            display_boards[-1][int(idx)] += 1
    for z in range(len(display_boards[-1])):
        display_boards[-1][z] /= len(res[k])

num_chessboards = len(display_boards)
num_rows = int(np.ceil(np.sqrt(num_chessboards)))
num_cols = int(np.ceil(num_chessboards / num_rows))
fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5))

ns = [int(np.sqrt(len(item))) for item in display_boards]

# Handle the case when there is only one chessboard
if num_chessboards == 1:
    axes = np.array([axes])  # Reshape axes into a 2D array

for i, ax in zip(np.argsort(ns), axes.flatten()):
    im = display_chessboard_heatmap(ax, display_boards[i], ns[i])

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
fig.colorbar(im, cax=cbar_ax)
plt.tight_layout()
plt.show()
