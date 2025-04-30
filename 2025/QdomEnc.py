from pysat.card import CardEnc, EncType
import numpy as np
from abc import ABC
from pysat.formula import CNF, IDPool
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib import colors
from pysat.solvers import Solver
from datetime import datetime
import time



class Ordering(Enum):
    NONE = 1
    BY_DOMINATION_DEGREE = 2 # equivalent to occurrence-based ordering in the
                             # "The Impact of Literal Sorting on Cardinality Constraint Encodings" paper
    BLOCK_3x3=3 # Indicates a 3×3 block-wise ordering.
    BLOCKS_BY_MAX_DEGREE_3x3 = 4 # blocks are sorted by max degree
    BLOCKS_SORTED_BY_CELL_DEGREE_3x3=5 # Each block’s cells are sorted by domination degree.
    BLOCKS_SORTED_BY_MAX_THEN_CELL_DEGREE_3x3 = 6 # Sort blocks by max degree, then sort cells within blocks.

class QueenDominationProblem(ABC):
    """
    Abstract base class for defining queen domination problems on an n x n chessboard using SAT encoding.
    """

    def __init__(self, n,gamma):
        self.n = n
        self.gamma=gamma
        self.N = n * n
        self.G = self._get_attack_graph()
        self.vpool = IDPool(start_from=1)
        self.cnf = CNF()
        self.Q = lambda i: self.vpool.id(f"Q@{i}")  # Q(i) is True if square i has a queen (or a relevant piece)
        self.V=[self.Q(i) for i in range(self.N)]
        for i in range(self.N):
            self.Q(i)
        self._encode_domination_constraints()

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

class QdomEncoder(QueenDominationProblem):
    def __init__(self, n, gamma,card_type=EncType.mtotalizer,rc_enabled=False,ordering_type=Ordering.NONE):
        super().__init__(n, gamma)
        self.ordering_type=ordering_type
        self.rc_enabled=rc_enabled
        self.card_type=card_type
        self.V_sorted=None
        if self.rc_enabled:
            self.R = lambda r: self.vpool.id(f"R@{r}")  # True if row r has no queens
            self.C = lambda c: self.vpool.id(f"C@{c}")  # True if column c has no queens

        self._encode()


    def _encode(self):
        if self.ordering_type == Ordering.BY_DOMINATION_DEGREE:
            sorted_indices = sorted(range(self.N), key=lambda i: len(self.G[i]), reverse=True)
        elif self.ordering_type == Ordering.BLOCK_3x3:
            block_size=3
            sorted_indices = []
            for br in range(0, n, block_size):  # block row
                for bc in range(0, n, block_size):  # block col
                    for r in range(br, min(br + block_size, n)):
                        for c in range(bc, min(bc + block_size, n)):
                            sorted_indices.append(r * n + c)
        elif self.ordering_type == Ordering.BLOCKS_BY_MAX_DEGREE_3x3:
            block_size=3
            blocks = []
            for br in range(0, n, block_size):  # block row
                for bc in range(0, n, block_size):  # block col
                    block = []
                    for r in range(br, min(br + block_size, n)):
                        for c in range(bc, min(bc + block_size, n)):
                            block.append(r * n + c)
                    blocks.append(block)
            # replace by other functions e.g, min, avg if desirable
            block_max = [
                (i, max(len(self.G[idx]) for idx in block))
                for i, block in enumerate(blocks)
            ]

            sorted_blocks = sorted(block_max, key=lambda x: -x[1])

            sorted_indices = []
            for i, _ in sorted_blocks:
                sorted_indices.extend(blocks[i])
        elif self.ordering_type==Ordering.BLOCKS_SORTED_BY_CELL_DEGREE_3x3:
            block_size=3
            blocks = []
            for br in range(0, n, block_size):  # block row
                for bc in range(0, n, block_size):  # block col
                    block = []
                    for r in range(br, min(br + block_size, n)):
                        for c in range(bc, min(bc + block_size, n)):
                            idx = r * n + c
                            block.append(idx)
                    # Sort each block by individual domination degree (descending)
                    block.sort(key=lambda i: -len(self.G[i]))
                    blocks.append(block)

            sorted_indices = [i for block in blocks for i in block]
        elif self.ordering_type==Ordering.BLOCKS_SORTED_BY_MAX_THEN_CELL_DEGREE_3x3:
            block_size=3
            blocks = []
            for br in range(0, n, block_size):  # block row
                for bc in range(0, n, block_size):  # block col
                    block = []
                    for r in range(br, min(br + block_size, n)):
                        for c in range(bc, min(bc + block_size, n)):
                            idx = r * n + c
                            block.append(idx)
                    # Sort each block by individual domination degree (descending)
                    block.sort(key=lambda i: -len(self.G[i]))
                    blocks.append(block)

            # Sort blocks by their max (not avg) domination degree (descending)
            blocks.sort(key=lambda block: -max(len(self.G[i]) for i in block))

            # Flatten the sorted blocks into a single list of indices
            sorted_indices = [i for block in blocks for i in block]

        else: # NONE
            sorted_indices = list(range(len(self.V)))

        self.V_sorted = [self.Q(i) for i in sorted_indices]
        self.cnf.extend(CardEnc.atleast(lits=[-v for v in self.V_sorted], vpool=self.vpool,
                                        bound=self.n * self.n - self.gamma, encoding=self.card_type))

        if self.rc_enabled:
            # ---------- Row Constraints ----------
            # R(r) ↔ All squares in row r are empty (¬Q)
            for r in range(n):
                row_vars = self.V[r * n: r * n + n]
                for q in row_vars:
                    self.cnf.append([-self.R(r), -q])  # If row is empty, no square in it has a queen
                self.cnf.append([self.R(r)] + row_vars)  # If all squares are empty, R(r) is True

            # ---------- Column Constraints ----------
            # C(c) ↔ All squares in column c are empty (¬Q)
            for c in range(n):
                col_vars = self.V[c::n]
                for q in col_vars:
                    self.cnf.append([-self.C(c), -q])
                self.cnf.append([self.C(c)] + col_vars)

            # replace if ordering of rc by dom degree is desirable
            # mid = n // 2
            # order = [mid]
            # for i in range(1, n):
            #     if i % 2:
            #         order.append(mid + (i + 1) // 2)
            #     else:
            #         order.append(mid - (i // 2))
            # ordering_result = [r for r in order]

            ordering_result = [r for r in range(n)]
            # At least n - γ rows and columns must be completely empty
            self.cnf.extend(CardEnc.atleast(lits=[self.R(r) for r in ordering_result], vpool=self.vpool, bound=n - gamma,
                                            encoding=self.card_type))
            self.cnf.extend(CardEnc.atleast(lits=[self.C(c) for c in ordering_result], vpool=self.vpool, bound=n - gamma,
                                            encoding=self.card_type))

        return self


class VizSolver(object):
    """
    This class has not been thoroughly tested. While it appears to work correctly based on my initial review,
     bugs may still be present. Use with caution.
    """
    def __init__(self, n, vpool):
        self.trail = []
        self.trlim = []
        self.qhead = None
        self.decision_level = 0
        self.level = {}
        self.backtrack_log = []

        self.n = n
        self.vpool = vpool
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.state = np.full((n, n), 0)  # 0=unassigned, 1=true, -1=false
        self.im = None
        plt.ion()
        plt.show()

    def update_plot(self):
        cmap = colors.ListedColormap(['red', 'white', 'green'])  # -1=red, 0=white, 1=green
        bounds = [-1.5, -0.5, 0.5, 1.5]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        if self.im:
            self.im.set_data(self.state)
        else:
            self.im = self.ax.imshow(self.state, cmap=cmap, norm=norm)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_title(f"Real-time SAT Solver View")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(0.05)

    def on_assignment(self, lit: int, fixed: bool = False) -> None:
        self.level[abs(lit)] = self.decision_level
        if self.qhead is None:
            self.qhead = len(self.trail)
        self.trail.append(lit)

        name = self.vpool.obj(abs(lit))
        if fixed:
            print("fixed")
        if name.startswith("Q@"):
            index = int(name.split("@")[1])
            r, c = divmod(index, self.n)
            self.state[r, c] = 1 if lit > 0 else -1
            self.update_plot()

    def on_new_level(self) -> None:
        self.decision_level += 1
        self.trlim.append(len(self.trail))

    def on_backtrack(self, to: int):
        while self.decision_level > to:
            self.decision_level -= 1
            lim = self.trlim.pop()
            undone = self.trail[lim:]
            self.trail = self.trail[:lim]
            self.qhead = None
            for lit in undone:
                name = self.vpool.obj(abs(lit))
                if name.startswith("Q@"):
                    index = int(name.split("@")[1])
                    r, c = divmod(index, self.n)
                    self.state[r, c] = 0
            self.update_plot()

    def decide(self) -> int:
        """Used for manual branching (optional in this tutorial)."""
        return 0  # Let the solver decide

    def propagate(self):
        """Used for custom propagation logic (we’re skipping it for now)."""
        return []  # No manual propagation

    def provide_reason(self, lit: int):
        """Explain why a literal was propagated (skip for now)."""
        pass

    def check_model(self, model) -> bool:
        """Optional: Validate the final model."""
        return True

    def add_clause(self):
        """Add clauses dynamically if needed (skip for now)."""
        return []
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

if __name__=="__main__":

    # start_time = datetime.now()

    # Configuration
    n,gamma=12,6
    N=n*n

    # Create encoding
    enc1=QdomEncoder(n, gamma, EncType.mtotalizer, ordering_type=Ordering.BLOCKS_SORTED_BY_CELL_DEGREE_3x3)
    SAT = False

    # Optional: visualize variable ordering
    # plot_literal_ordering(n, [x - 1 for x in enc1.V_sorted], ordering_type=enc1.ordering_type)

    # Optional: export CNF to file
    # enc1.cnf.to_file(f"{n}_{gamma}_{enc1.ordering_type.name}_{...}.cnf")

    # === Consistency Note ===
    # In my experiments, I typically wrote the formula to disk and ran CaDiCaL from the command line.
    # The snippet below is for direct solver invocation:
    #
    # with Solver(name='Cadical195', bootstrap_with=enc1.cnf, use_timer=True) as solver:
    #     # Note: CaDiCaL does not support solver.set_phases(V)
    #     if solver.solve():
    #         print("SAT")
    #         model = solver.get_model()
    #         queens = [m - 1 for m in model if 0 < m <= N]  # Adjust to 0-based indexing
    #         SAT = True
    #     else:
    #         print("UNSAT")
    #
    #     print(f"Solve time (internal): {solver.time_accum():.4f} seconds")
    #
    # end_time = datetime.now()
    # elapsed_time = (end_time - start_time).total_seconds()

    # Use the following code to observe the real-time behavior of the solver with respect to chessboard-related
    # variables, if desired.

    # viewer = VizSolver(n=n, vpool=enc1.vpool)
    # SAT = False
    # with Solver(name='Cadical195', bootstrap_with=enc1.cnf, use_timer=True) as solver:
    #     solver.connect_propagator(viewer)
    #     for v in enc1.V:
    #         solver.observe(v)
    #     if solver.solve():
    #         model = solver.get_model()
    #         queens = [m - 1 for m in model if 0 < m <= n * n]
    #         SAT = True
    #     else:
    #         print("UNSAT")
    # if SAT:
    #     print("SAT")
    #     plot(queens, n, gamma)




