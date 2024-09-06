import gurobipy as gp
from gurobipy import GRB

def solve_queen_domination(n,num_threads=1):
    model = gp.Model("MinQueenDomination")

    model.setParam(GRB.Param.Threads, num_threads)

    x = model.addVars(n * n, vtype=GRB.BINARY, name="x")

    model.setObjective(gp.quicksum(x[v] for v in range(n * n)), GRB.MINIMIZE)

    for r in range(n):
        for c in range(n):
            model.addConstr(gp.quicksum(x[i] for i in get_queen_positions(n, r, c)) >= 1)

    model.optimize()

    queens = [v for v in range(n * n) if x[v].x > 0.5]

    return queens

def get_queen_positions(n, row, col):
    positions = []

    positions.append(row * n + col)

    for i in range(n):
        positions.append(row * n + i)
        positions.append(i * n + col)

    for i in range(n):
        if 0 <= row + i < n and 0 <= col + i < n:
            positions.append((row + i) * n + col + i)
        if 0 <= row - i < n and 0 <= col + i < n:
            positions.append((row - i) * n + col + i)
        if 0 <= row + i < n and 0 <= col - i < n:
            positions.append((row + i) * n + col - i)
        if 0 <= row - i < n and 0 <= col - i < n:
            positions.append((row - i) * n + col - i)

    return positions

n = 15
queens = solve_queen_domination(n,num_threads=1)

print("Queen Positions:", queens)
