from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
from enum import Enum
from dataclasses import dataclass
from itertools import product
import numpy as np
import matplotlib.pyplot as plt
from hilbertcurve.hilbertcurve import HilbertCurve
import argparse
from datetime import datetime
import os


class Ordering(Enum):
    NONE = 1
    DOMINATION_DEGREE = 2
    HILBERTCURVE = 3


@dataclass
class TotNode:
    vars: list
    nof_input: int
    left: object = None
    right: object = None
    names: list = None
    bottom_depth: int = 0
    paper_depth: int = None
    node_id: int = 0


def generate_board(n):
    return np.arange(1, n * n + 1).reshape((n, n))


def apply_symmetry(board, sym):
    if sym == "identity":
        return board
    if sym == "rotate90":
        return np.rot90(board, k=1)
    if sym == "rotate180":
        return np.rot90(board, k=2)
    if sym == "rotate270":
        return np.rot90(board, k=3)
    if sym == "flip_horizontal":
        return np.fliplr(board)
    if sym == "flip_vertical":
        return np.flipud(board)
    if sym == "flip_main_diag":
        return np.transpose(board)
    if sym == "flip_anti_diag":
        return np.flipud(np.fliplr(np.transpose(board)))
    raise ValueError(f"Unknown symmetry: {sym}")


def get_ordering(n, sym="identity"):
    return apply_symmetry(generate_board(n), sym).flatten().tolist()


def add_totalizer_merge(cnf, out, av, bv, rhs):
    for j in range(1, min(rhs, len(bv)) + 1):
        cnf.append([-bv[j - 1], out[j - 1]])

    for i in range(1, min(rhs, len(av)) + 1):
        cnf.append([-av[i - 1], out[i - 1]])

    for i in range(1, min(rhs, len(av)) + 1):
        max_j = min(rhs - i, len(bv))
        for j in range(1, max_j + 1):
            cnf.append([-av[i - 1], -bv[j - 1], out[i + j - 1]])


def assign_paper_depths(root, aux_meta):
    paper_depth_nodes = {}

    def dfs(node, paper_depth):
        if node is None:
            return

        node.paper_depth = paper_depth

        if node.left is not None and node.right is not None and paper_depth >= 1:
            paper_depth_nodes.setdefault(paper_depth, []).append(node)

            for var in node.vars:
                if var in aux_meta:
                    aux_meta[var]["paper_depth"] = paper_depth

        dfs(node.left, paper_depth + 1)
        dfs(node.right, paper_depth + 1)

    dfs(root.left, 1)
    dfs(root.right, 1)

    return paper_depth_nodes


def build_tracked_totalizer(cnf, vpool, lits, names, bound, prefix):
    assert len(lits) == len(names)

    rhs = min(bound + 1, len(lits))
    aux_meta = {}
    bottom_depth_nodes = {}

    queue = []
    for idx, (lit, name) in enumerate(zip(lits, names)):
        queue.append(
            TotNode(
                vars=[lit],
                nof_input=1,
                names=[name],
                bottom_depth=0,
                node_id=idx,
            )
        )

    bottom_depth = 1

    while len(queue) > 1:
        new_queue = []
        i = 0
        node_id = 0

        while i < len(queue):
            left = queue[i]
            i += 1

            if i >= len(queue):
                new_queue.append(left)
                continue

            right = queue[i]
            i += 1

            nof_input = left.nof_input + right.nof_input
            kmin = min(rhs, nof_input)
            names_here = left.names + right.names

            out = []
            node = TotNode(
                vars=out,
                nof_input=nof_input,
                left=left,
                right=right,
                names=names_here,
                bottom_depth=bottom_depth,
                node_id=node_id,
            )

            for t in range(1, kmin + 1):
                var = vpool.id(f"{prefix}@bd{bottom_depth}@n{node_id}@ge{t}")
                out.append(var)

                aux_meta[var] = {
                    "bottom_depth": bottom_depth,
                    "paper_depth": None,
                    "node_id": node_id,
                    "count": t,
                    "nof_input": nof_input,
                    "names": list(names_here),
                    "meaning": (
                        f"at least {t} true literals among "
                        f"this node's {nof_input} literals"
                    ),
                }

            add_totalizer_merge(cnf, out, left.vars, right.vars, kmin)

            bottom_depth_nodes.setdefault(bottom_depth, []).append(node)
            new_queue.append(node)
            node_id += 1

        queue = new_queue
        bottom_depth += 1

    root = queue[0]

    if bound + 1 <= len(root.vars):
        cnf.append([-root.vars[bound]])

    paper_depth_nodes = assign_paper_depths(root, aux_meta)

    return root, aux_meta, bottom_depth_nodes, paper_depth_nodes


def select_totalizer_cube_vars_paper(
    paper_depth_nodes,
    bound,
    total_inputs,
    num_vars=12,
    start_depth=2,
):
    if total_inputs == 0:
        return []

    R = bound / total_inputs
    chosen = []
    depth = start_depth

    while len(chosen) < num_vars and depth in paper_depth_nodes:
        nodes = sorted(
            paper_depth_nodes[depth],
            key=lambda node: len(node.vars),
            reverse=True,
        )

        for node in nodes:
            ncnt = len(node.vars)
            if ncnt == 0:
                continue

            base = int(R * ncnt)

            if node.node_id % 2 == 0:
                counter = base + 1
            else:
                counter = base

            counter = max(1, min(counter, ncnt))
            chosen.append(node.vars[counter - 1])

            if len(chosen) >= num_vars:
                break

        depth += 1

    return chosen


def all_static_cubes(cube_vars):
    for signs in product([False, True], repeat=len(cube_vars)):
        yield [var if sign else -var for var, sign in zip(cube_vars, signs)]


def write_cubes(path, cube_vars):
    with open(path, "w") as f:
        for cube in all_static_cubes(cube_vars):
            f.write("a " +" ".join(map(str, cube)) + " 0\n")


class QdomEncoder:
    def __init__(
        self,
        n,
        gamma,
        line_card_type=EncType.mtotalizer,
        ordering_type=Ordering.NONE,
        symmetry_break=False,
    ):
        self.n = n
        self.gamma = gamma
        self.N = n * n
        self.ordering_type = ordering_type
        self.line_card_type = line_card_type
        self.symmetry_break = symmetry_break

        self.vpool = IDPool(start_from=1)
        self.cnf = CNF()

        self.Q = lambda i: self.vpool.id(f"Q@{i}")
        self.L = lambda name: self.vpool.id(f"L@{name}")

        self.V = [self.Q(i) for i in range(self.N)]
        self.V_sorted = None

        self.lines, self.square_to_lines = self._build_lines()

        self.line_names_sorted = None
        self.line_bound = None

        self.square_bound = gamma
        self.square_tot_root = None
        self.square_tot_aux_meta = {}
        self.square_tot_bottom_depth_nodes = {}
        self.square_tot_paper_depth_nodes = {}

        self._encode_line_domination_constraints()
        self._encode_line_cardinality_constraint_mtotalizer()
        self._encode_square_cardinality_constraint_tracked_totalizer()

        if self.symmetry_break:
            self._encode_static_symmetry_breaking()


    def _build_lines(self):
        n = self.n
        lines = {}

        for r in range(n):
            lines[f"row_{r}"] = [r * n + c for c in range(n)]

        for c in range(n):
            lines[f"col_{c}"] = [r * n + c for r in range(n)]

        for d in range(-(n - 1), n):
            lines[f"diag_{d}"] = [
                r * n + c
                for r in range(n)
                for c in range(n)
                if r - c == d
            ]

        for s in range(2 * n - 1):
            lines[f"anti_{s}"] = [
                r * n + c
                for r in range(n)
                for c in range(n)
                if r + c == s
            ]

        square_to_lines = [[] for _ in range(n * n)]
        for i in range(n * n):
            r, c = divmod(i, n)
            square_to_lines[i] = [
                f"row_{r}",
                f"col_{c}",
                f"diag_{r - c}",
                f"anti_{r + c}",
            ]

        return lines, square_to_lines

    def _encode_line_domination_constraints(self):

        for i in range(self.N):
            self.cnf.append([self.L(name) for name in self.square_to_lines[i]])

        for line_name, cells in self.lines.items():
            self.cnf.append([-self.L(line_name)] + [self.Q(i) for i in cells])


    def _encode_line_cardinality_constraint_mtotalizer(self):
        sorted_line_names = sorted(
            self.lines.keys(),
            key=lambda line_name: len(self.lines[line_name]),
            reverse=True,
        )

        self.line_names_sorted = sorted_line_names
        line_vars = [self.L(line_name) for line_name in sorted_line_names]
        self.line_bound = min(4 * self.gamma, len(line_vars))

        self.cnf.extend(
            CardEnc.atmost(
                lits=line_vars,
                bound=self.line_bound,
                vpool=self.vpool,
                encoding=self.line_card_type,
            )
        )

    def _get_sorted_square_indices(self):
        if self.ordering_type == Ordering.DOMINATION_DEGREE:
            score = []
            for i in range(self.N):
                covered = set()
                for line_name in self.square_to_lines[i]:
                    covered.update(self.lines[line_name])
                score.append(len(covered))

            return sorted(range(self.N), key=lambda i: score[i], reverse=True)

        if self.ordering_type == Ordering.HILBERTCURVE:
            hilbert = HilbertCurve(p=(self.n - 1).bit_length(), n=2)
            return sorted(
                range(self.N),
                key=lambda i: -hilbert.distance_from_point([i // self.n, i % self.n]),
            )

        return list(range(self.N))

    def _encode_square_cardinality_constraint_tracked_totalizer(self):
        sorted_indices = self._get_sorted_square_indices()
        self.V_sorted = [self.Q(i) for i in sorted_indices]

        square_names = [f"Q@{i}" for i in sorted_indices]

        (
            self.square_tot_root,
            self.square_tot_aux_meta,
            self.square_tot_bottom_depth_nodes,
            self.square_tot_paper_depth_nodes,
        ) = build_tracked_totalizer(
            cnf=self.cnf,
            vpool=self.vpool,
            lits=self.V_sorted,
            names=square_names,
            bound=self.square_bound,
            prefix="TSQUARE",
        )


    def get_symmetry_permutation(self, n, sym):
        """
        Returns perm where perm[i] is the square index obtained by applying sym to i.
        Uses 0-based square indices.
        """
        board = np.arange(n * n).reshape((n, n))
        return apply_symmetry(board, sym).flatten().tolist()

    def _encode_static_symmetry_breaking(
        self,
        symmetries=None,
        prefix_k=None,
    ):
        N = self.N
        X = self._get_sorted_square_indices()

        if symmetries is None:
            symmetries = [
                "rotate90",
                "rotate180",
                "rotate270",
                "flip_horizontal",
                "flip_vertical",
                "flip_main_diag",
                "flip_anti_diag",
            ]

        if prefix_k is None:
            prefix_k = N

        k = min(prefix_k, N)

        for sym in symmetries:
            perm = self.get_symmetry_permutation(self.n, sym)
            Y = [perm[i] for i in X]

            a = [
                self.vpool.id(f"SB@{sym}@{self.ordering_type.name}@prefix{k}@{i}")
                for i in range(k + 1)
            ]

            self.cnf.append([a[0]])
            self.cnf.append([a[k]])

            for i in range(1, k + 1):
                x_lit = self.Q(X[i - 1])
                y_lit = self.Q(Y[i - 1])

                self.cnf.append([a[i], y_lit, -a[i - 1]])
                self.cnf.append([a[i], -x_lit, -a[i - 1]])
                self.cnf.append([y_lit, -x_lit, -a[i - 1]])

    def print_selected_cube_vars(self, cube_vars):
        print("\n--- Selected cube variables from SQUARE totalizer ---")
        for v in cube_vars:
            meta = self.square_tot_aux_meta[v]
            print(
                f"{v}: paper_depth={meta['paper_depth']}, "
                f"bottom_depth={meta['bottom_depth']}, "
                f"node={meta['node_id'] + 1}, "
                f"count={meta['count']}, "
                f"size={meta['nof_input']} :: "
                f"{meta['meaning']}"
            )


def plot(queen_positions, n, gamma):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticks(np.arange(n + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1.5)

    board_colors = np.zeros((n, n, 3))
    light_square = (240 / 255, 217 / 255, 181 / 255)
    dark_square = (181 / 255, 136 / 255, 99 / 255)

    for r in range(n):
        for c in range(n):
            board_colors[r, c] = light_square if (r + c) % 2 == 0 else dark_square

    ax.imshow(board_colors)

    for row, col in [divmod(pos, n) for pos in queen_positions]:
        ax.text(
            col,
            row,
            "♛",
            fontsize=max(6, 200 // n),
            ha="center",
            va="center",
            color="black",
        )

    plt.title(f"n={n}, gamma={gamma}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="QDOM: lines use mtotalizer, squares use tracked totalizer for cubing."
    )

    parser.add_argument("--n", type=int, default=12)
    parser.add_argument("--gamma", type=int, default=6)

    parser.add_argument(
        "--line_enc",
        type=str,
        default="mtotalizer",
        choices=["seqcounter", "sortnetwrk", "cardnetwrk", "mtotalizer", "kmtotalizer"],
        help="Encoding used for line cardinality constraint.",
    )

    parser.add_argument(
        "--ordering",
        type=str,
        default="HILBERTCURVE",
        choices=["NONE", "HILBERTCURVE", "DOMINATION_DEGREE"],
    )

    parser.add_argument("--sym_break", action="store_true")

    parser.add_argument("--write_cnf", action="store_true")
    parser.add_argument("--write_dir", type=str, default="./out")

    parser.add_argument("--make_cubes", action="store_true")
    parser.add_argument("--cube_vars", type=int, default=12)
    parser.add_argument("--cube_start_depth", type=int, default=2)
    parser.add_argument("--cube_file", type=str, default="square_totalizer.cubes")
    parser.add_argument("--print_cube_vars", action="store_true")

    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--plot_solution", action="store_true")

    args = parser.parse_args()

    total_start = datetime.now()

    ordering_type = getattr(Ordering, args.ordering.upper())
    line_enc_type = getattr(EncType, args.line_enc)

    encoding_start = datetime.now()

    enc = QdomEncoder(
        n=args.n,
        gamma=args.gamma,
        line_card_type=line_enc_type,
        ordering_type=ordering_type,
        symmetry_break=args.sym_break,
    )

    encoding_end = datetime.now()
    encoding_time = (encoding_end - encoding_start).total_seconds()

    if args.write_cnf:
        os.makedirs(args.write_dir, exist_ok=True)

        sb_tag = "sym" if args.sym_break else "nosym"
        cnf_path = os.path.join(
            args.write_dir,
            f"{args.n}_{args.gamma}_{args.ordering}_{args.line_enc}_{sb_tag}_square_cubing.cnf",
        )

        enc.cnf.to_file(cnf_path)
        print(f"CNF written to: {cnf_path}")

    cube_vars = []

    if args.make_cubes:
        cube_vars = select_totalizer_cube_vars_paper(
            paper_depth_nodes=enc.square_tot_paper_depth_nodes,
            bound=enc.square_bound,
            total_inputs=len(enc.V_sorted),
            num_vars=args.cube_vars,
            start_depth=args.cube_start_depth,
        )

        write_cubes(args.cube_file, cube_vars)

        print(f"Cubes written to: {args.cube_file}")
        print(f"Number of cube variables: {len(cube_vars)}")
        print(f"Number of cubes: {2 ** len(cube_vars)}")
        print(f"Symmetry breaking: {'enabled' if args.sym_break else 'disabled'}")
        print(f"Square cardinality bound k: {enc.square_bound}")
        print(f"Number of square literals s: {len(enc.V_sorted)}")
        print(f"R_k = k / s: {enc.square_bound / len(enc.V_sorted):.6f}")

        if args.print_cube_vars:
            enc.print_selected_cube_vars(cube_vars)

    solving_time = None

    if args.solve:
        solve_start = datetime.now()

        if args.make_cubes and cube_vars:
            cubes = list(all_static_cubes(cube_vars))
            print(f"Solving {len(cubes)} cubes sequentially...")

            sat_found = False
            queens = []

            with Solver(name="Cadical195", bootstrap_with=enc.cnf, use_timer=True) as solver:
                for idx, cube in enumerate(cubes):
                    if solver.solve(assumptions=cube):
                        model = set(solver.get_model())
                        queens = [i for i in range(enc.N) if enc.Q(i) in model]
                        sat_found = True
                        print(f"SAT in cube {idx}: {cube}")
                        break
                    else:
                        print(f"UNSAT cube: {idx}, time: {solver.time_accum():.4f} seconds")

                if not sat_found:
                    print("UNSAT over all cubes")

                print(f"Solve time internal: {solver.time_accum():.4f} seconds")

            if sat_found and args.plot_solution:
                plot(queens, args.n, args.gamma)

        else:
            with Solver(name="Cadical195", bootstrap_with=enc.cnf, use_timer=True) as solver:
                if solver.solve():
                    model = set(solver.get_model())
                    queens = [i for i in range(enc.N) if enc.Q(i) in model]
                    print("SAT")

                    if args.plot_solution:
                        plot(queens, args.n, args.gamma)
                else:
                    print("UNSAT")

                print(f"Solve time internal: {solver.time_accum():.4f} seconds")

        solve_end = datetime.now()
        solving_time = (solve_end - solve_start).total_seconds()

    total_end = datetime.now()
    total_time = (total_end - total_start).total_seconds()

    print("\n--- Timing Summary ---")
    print(f"Encoding time: {encoding_time:.2f} seconds")
    if solving_time is not None:
        print(f"Solving time: {solving_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")