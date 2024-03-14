import argparse
"""

Encodes minimum queen domination set problem of size n, and gamma(optional)
to saves it into a .opb format, so can be feed to pseudo-Boolean solvers


the format is described in:

Input/Output Format and Solver Requirements
for the Competitions of Pseudo-Boolean Solvers,

by Olivier ROUSSEL, and Vasco MANQUINHO
"""

def get_queen_graph(n):
    G = []
    V = [i for i in range(n * n)]  # Start variables from 1
    for i in range(len(V)):
        N = [V[i]]
        r, c = i // n, i % n
        # squares in the same row
        N += V[r * n:r * n + n]
        # squares in the same column
        N += V[c::n]
        # squares in the same diagonal (from top left to bottom right)
        N += [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        # squares in the same diagonal (from top right to bottom left)
        N += [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        N = list(set(N))
        G.append(N)
    return G


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Hi!")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--gamma", type=int, default=None)
    args = parser.parse_args()

    n = args.n
    gamma=args.gamma
    G = get_queen_graph(n)

    with open("E:\\shared\\opb\\q.opb", "w") as f:
        # Variable declarations
        f.write(f"* #variable= {n*n}\n")

        # Objective function
        if gamma is None:
           f.write("min: " + " ".join(f"1 x{i+1}" for i in range(n * n)) + " ;\n\n")
        else:
           f.write(" ".join(f"1 x{i + 1}" for i in range(n * n)) + f" = {gamma} ;\n\n")

        # Constraints
        for ns_idx in range(len(G)):
            f.write(" ".join(f"1 x{j+1}" for j in G[ns_idx]) + " >= 1 ;")
            if ns_idx!=len(G)-1:
                f.write("\n\n")
