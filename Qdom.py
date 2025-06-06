from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from hilbertcurve.hilbertcurve import HilbertCurve
import argparse
from datetime import datetime
from pysat.solvers import Solver

class Ordering(Enum):
    NONE = 1
    DOMINATION_DEGREE = 2
    HILBERTCURVE=3


class QdomEncoder:
    def __init__(self, n, gamma,card_type=EncType.mtotalizer,ordering_type=Ordering.NONE):
        self.n = n
        self.gamma=gamma
        self.N = n * n
        self.ordering_type=ordering_type
        self.card_type=card_type
        self.G = self._get_attack_graph()
        self.vpool = IDPool(start_from=1)
        self.cnf = CNF()
        self.Q = lambda i: self.vpool.id(f"Q@{i}")  # Q(i) is True if square i has a queen
        self.V=[self.Q(i) for i in range(self.N)]
        for i in range(self.N):
            self.Q(i)
        self.V_sorted=None
        self._encode_domination_constraints()
        self._encode_cardinality_constraints()

    def _get_attack_graph(self):
        """
            Constructs a graph representing queen moves on an n x n chessboard.

            :param n: Size of the chessboard (number of rows/columns).
            :return: A list G where G[i] is a list of 0-based indices representing all
                     squares the queen can attack from square i (including itself).
            """
        n=self.n
        N = n * n
        V = [i for i in range(N)]
        G = []  # Adjacency list representing queen attack relations

        for i in range(N):
            r, c = divmod(i, n)
            Ns = [V[i]]  # Include the current square

            # Add all squares in the same row
            Ns += V[r * n: r * n + n]

            # Add all squares in the same column
            Ns += V[c::n]

            # Add all squares on the top-left to bottom-right diagonal
            Ns += [V[j] for j in range(N) if (j // n) - (j % n) == r - c]

            # Add all squares on the top-right to bottom-left diagonal
            Ns += [V[j] for j in range(N) if (j // n) + (j % n) == r + c]

            G.append(list(set(Ns)))  # Remove duplicates and add to the graph


        return G

    def _encode_domination_constraints(self):
        """
        Encodes the constraint that every square must be dominated.
        """
        for i in range(self.N):
            self.cnf.append([self.Q(idx) for idx in self.G[i]])

        return self.cnf

    def _encode_cardinality_constraints(self):

        if self.ordering_type == Ordering.DOMINATION_DEGREE:
            sorted_indices = sorted(range(self.N), key=lambda i: len(self.G[i]), reverse=True)
        elif self.ordering_type == Ordering.HILBERTCURVE:
            hilbert = HilbertCurve(p=self.n.bit_length(), n=2)
            sorted_indices= sorted(
                range(self.n * self.n),
                key=lambda i: (
                    hilbert.distance_from_point([i // self.n, i % self.n]), -len(self.G[i])
                )
            )
        else: # NONE
            sorted_indices = list(range(len(self.V)))

        self.V_sorted = [self.Q(i) for i in sorted_indices]
        self.cnf.extend(CardEnc.atleast(lits=[-v for v in self.V_sorted], vpool=self.vpool,
                                        bound=self.n * self.n - self.gamma, encoding=self.card_type))

        return self



def plot(queen_positions,n,gamma):
    # Visualization
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticks(np.arange(n + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1.5)

    board_colors = np.zeros((n, n, 3))  # 3D array for RGB colors

    # Define board colors in normalized RGB format
    LIGHT_SQUARE = (240 / 255, 217 / 255, 181 / 255)  # Light Brown
    DARK_SQUARE = (181 / 255, 136 / 255, 99 / 255)  # Dark Brown
    for r in range(n):
        for c in range(n):
            board_colors[r, c] = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE

    ax.imshow(board_colors)

    # Place queens
    for row, col in [(divmod(pos, n)) for pos in queen_positions]:
        ax.text(col, row, "♛", fontsize=max(6, 200 // n), ha='center', va='center', color="black")

    plt.title(f"n={n},gamma={gamma}")
    plt.show()
def plot_literal_ordering(n, order_indices,ordering_type):
    board = np.zeros((n, n), dtype=int)

    for idx, i in enumerate(order_indices):
        r, c = divmod(i, n)
        board[r, c] = idx + 1  # Store the order of index (1-based index)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(board, cmap="viridis", origin="upper")

    # Draw grid lines
    for x in range(n + 1):
        ax.axhline(x - 0.5, color="gray", lw=0.5)
        ax.axvline(x - 0.5, color="gray", lw=0.5)

    # Annotate indices
    for r in range(n):
        for c in range(n):
            ax.text(c, r, str(board[r, c]), ha='center', va='center', fontsize=10, color='white')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"ORDERING TYPE: {ordering_type.name} for {n}x{n} Grid")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QDOM problem encoding and optional solving with CaDiCaL.")

    parser.add_argument("--n", type=int, default=12, help="Board size (n x n)")
    parser.add_argument("--gamma", type=int, default=6, help="Number of queens per group")

    parser.add_argument("--enc", type=str, default="mtotalizer", choices=["seqcounter","sortnetwrk","cardnetwrk","mtotalizer","kmtotalizer"],
                        help="Cardinality encoding type")
    parser.add_argument("--ordering", type=str, default="HILBERTCURVE", choices=["NONE", "HILBERTCURVE", "DOMINATION_DEGREE"],
                        help="Literal ordering strategy")

    parser.add_argument("--visualize", action="store_true", help="Plot variable ordering")
    parser.add_argument("--plot_solution", action="store_true", help="Plot the solution if SAT")
    parser.add_argument("--write_dir", type=str, default=None,
                        help="Directory path to write the CNF file (writing enabled only if specified)")
    parser.add_argument("--solve", action="store_true", help="Solve the encoded CNF using CaDiCaL and report timing")

    args = parser.parse_args()

    total_start = datetime.now()

    n, gamma = args.n, args.gamma
    N = n * n

    # Map string to Enum
    ordering_type = getattr(Ordering, args.ordering.upper())
    enc_type = getattr(EncType, args.enc)


    # === Encoding ===
    encoding_start = datetime.now()
    enc = QdomEncoder(n, gamma, enc_type, ordering_type=ordering_type)
    encoding_end = datetime.now()
    encoding_time = (encoding_end - encoding_start).total_seconds()

    # === Optional: Visualize Variable Ordering ===
    if args.visualize:
        plot_literal_ordering(n, [x - 1 for x in enc.V_sorted], ordering_type=ordering_type)

    # === Optional: Write CNF to File ===
    if args.write_dir:
        cnf_filename = f"{n}_{gamma}_{args.ordering.upper()}_{args.enc}.cnf"
        enc.cnf.to_file(cnf_filename)
        print(f"CNF written to: {cnf_filename}")

    # === Optional: Solve using CaDiCaL ===
    solving_time = None
    if args.solve:
        with Solver(name='Cadical195', bootstrap_with=enc.cnf, use_timer=True) as solver:
            solve_start = datetime.now()
            if solver.solve():
                model = solver.get_model()
                queens = [m - 1 for m in model if 0 < m <= N]
                SAT = True
            else:
                print("UNSAT")
                SAT = False
            solve_end = datetime.now()
            solving_time = (solve_end - solve_start).total_seconds()
            print(f"Solve time (internal): {solver.time_accum():.4f} seconds")

        if SAT and args.plot_solution:
            plot(queens, n, gamma)

    total_end = datetime.now()
    total_time = (total_end - total_start).total_seconds()

    # === Final Time Report ===
    print("\n--- Timing Summary ---")
    print(f"Encoding time: {encoding_time:.2f} seconds")
    if solving_time is not None:
        print(f"Solving time: {solving_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")








