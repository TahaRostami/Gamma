from ortools.sat.python import cp_model
import time

def solve_queen_domination(n, num_threads=1):
    start_time = time.time()  # Start time measurement

    model = cp_model.CpModel()

    # Variables
    x = [model.NewBoolVar(f'v_{i}') for i in range(n*n)]

    # Constraints: Each square must be dominated
    for r in range(n):
        for c in range(n):
            model.Add(sum(x[i] for i in get_queen_positions(n, r, c)) >= 1)

    # Objective function: Minimize the number of queens
    model.Minimize(sum(x))

    # Solver
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = num_threads
    status = solver.Solve(model)

    queens_positions = []
    if status == cp_model.OPTIMAL:
        queens_positions = [i for i in range(n*n) if solver.Value(x[i]) == 1]

    end_time = time.time()
    elapsed_time = end_time - start_time

    return queens_positions, elapsed_time


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

n = 10
queens, time_taken = solve_queen_domination(n, num_threads=1)
print("Queen Positions:", queens)
print("Time taken:", time_taken, "seconds")
