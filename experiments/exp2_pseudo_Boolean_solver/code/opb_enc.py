import argparse

def get_queen_graph(n):
    G = []
    V = [i for i in range(n * n)]  # start variables from 1
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

    with open(f"n_{n}_gamma_{gamma}.opb", "w") as f:
        f.write(f"* #variable= {n*n}\n")

        if gamma is None:
           f.write("min: " + " ".join(f"1 x{i+1}" for i in range(n * n)) + " ;\n\n")
        else:
           f.write(" ".join(f"1 x{i + 1}" for i in range(n * n)) + f" = {gamma} ;\n\n")

        for ns_idx in range(len(G)):
            f.write(" ".join(f"1 x{j+1}" for j in G[ns_idx]) + " >= 1 ;")
            if ns_idx!=len(G)-1:
                f.write("\n\n")
