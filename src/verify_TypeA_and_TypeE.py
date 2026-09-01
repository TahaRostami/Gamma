# replace with desired file's path and name
with open("q733_coords.txt", "r") as f:
    lines=f.read().split('\n')
header, coordinates =lines[0].split(' '), [l.split(' ') for l in lines[1:-1]]
coordinates = set([(int(c[0]),int(c[1])) for c in coordinates])
n, d, k, r, p = int(header[0]), len(coordinates),  int(header[0])//4, (int(header[0]) - 1) // 2, 0
board_range = list(range(-r, r + 1))
uncovered = {(x, y) for x in board_range for y in board_range}



# n is positive odd, n = 4k + 1, and d = 2k + 1.
assert (n>=0 and n%2==1) and n % 4 == 1 and (k>=0) and d==2*k+1
# all queens lie on Q_n.
assert all(-r <= x <= r and -r <= y <= r for x, y in coordinates)

# is domination set?
for x,y in coordinates:
    C = {(x, yy) for yy in board_range} # column x
    R = {(xx, y) for xx in board_range} # row y
    S = {(xx, (x + y) - xx) for xx in board_range if -r <= (x + y) - xx <= r} # sum diagonal: x + y
    D = {(xx, xx + (y - x)) for xx in board_range if -r <= xx + (y - x) <= r} # difference diagonal: y - x
    uncovered -= C | R | S | D
assert not uncovered


# p-orthodox iff every row and column of parity p contains a queen. (p=0 here)
p_rows, p_cols = {w for w in board_range if w % 2 == p}, {w for w in board_range if w % 2 == p}
for x, y in coordinates:
    p_cols.discard(x)
    p_rows.discard(y)
assert (not p_rows) and (not p_cols)

occupied_s = {x + y for x, y in coordinates}
occupied_d = {y - x for x, y in coordinates}

# p-cover: squares whose row and column both have parity 1-p must be covered diagonally.
not_diagonally_covered = {
    (x, y)
    for x in board_range
    for y in board_range
    if x % 2 == (1 - p)
    and y % 2 == (1 - p)
    and x + y not in occupied_s
    and y - x not in occupied_d
}
assert not not_diagonally_covered




# calc required parameters

# e(D)
e = 0
while (2 * (e + 1) in occupied_d and -2 * (e + 1) in occupied_d):e += 1

# f(D)
f = 0
while (2 * (f + 1) in occupied_s and -2 * (f + 1) in occupied_s):f += 1

# u(D)
u = 0
while True:
    i = u + 1

    diff_val = 2 * e + 4 * i
    sum_val  = 2 * f + 4 * i

    if (diff_val in occupied_d and -diff_val in occupied_d and sum_val in occupied_s and -sum_val in occupied_s):
        u += 1
    else:
        break

# Type-A
assert (e + f) % 2 == p
assert e + f + 2 * u >= (n - 5) // 2

# Must contain a square of each long/main diagonal.
assert (0 in occupied_d) and  (0 in occupied_s)


coef_num = d + 3
coef_den = n + 2
coef = coef_num / coef_den
print(f"According to W.D. Weakley's Theorem:")
print(f"Type-A parameters: e={e}, f={f}, u={u}")
print(f"Coefficient = ({d}+3)/({n}+2)")
print(f"Coefficient = {coef_num}/{coef_den} = {coef:.12f}")



# Type-E (Burger et al.)

# Type-E: queens lie only on even orthogonals,
# with at least one queen in every even row and every even column.
assert all(x % 2 == 0 and y % 2 == 0 for x, y in coordinates)

even_rows = {w for w in board_range if w % 2 == 0}
even_cols = {w for w in board_range if w % 2 == 0}

occupied_rows = {y for x, y in coordinates}
occupied_cols = {x for x, y in coordinates}

assert even_rows <= occupied_rows
assert even_cols <= occupied_cols


# Burger et al.

# it uses the reduced representation: original (2x,2y) -> reduced (x,y).
reduced_coordinates = {(x // 2, y // 2) for x, y in coordinates}

# occupied sum and difference diagonals in the reduced representation
occupied_s_E,occupied_d_E  = {x + y for x, y in reduced_coordinates},{y - x for x, y in reduced_coordinates}


# first empty sum diagonal from the center:smallest i > 0 such that s=i or s=-i is empty
i_s = 1
while (i_s in occupied_s_E) and (-i_s in occupied_s_E):i_s += 1

# first empty difference diagonal from the center: smallest i > 0 such that d=i or d=-i is empty
i_d = 1
while (i_d in occupied_d_E) and (-i_d in occupied_d_E):i_d += 1

# is it an (i,i)-set?
assert i_s == i_d

i = i_s
assert i < k


# required s- and d-diagonals are
# 0, ±1, ±2, ..., ±(i-1),
# ±(i+1), ±(i+3), ..., ±(2k-i-1)

required = {0}

for j in range(1, i):
    required.add(j)
    required.add(-j)

for j in range(i + 1, 2 * k - i, 2):
    required.add(j)
    required.add(-j)

assert (required <= occupied_s_E) and (required <= occupied_d_E)

coef_num_E = 3 * k + 5
coef_den_E = 6 * k + 3
coef_E = coef_num_E / coef_den_E

print(f"\nAccording to Burger et al.'s Theorem:")
print(f"Type-E ({i},{i}) set")
print(f"Coefficient = (3*{k}+5)/(6*{k}+3)")
print(f"Coefficient = {coef_num_E}/{coef_den_E} = {coef_E:.12f}")