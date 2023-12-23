// Unidom_plus_2.cpp : Defines the entry point for the application.
//

#include <iostream>
#include <cassert>
#include <cmath>
#include <set>
#include <deque>
#include <algorithm>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <ctime>
#include <queue>
#include <unordered_set>
#include <random>
#include <array>
#include <stack> 
#include <numeric>

static int n = 3;
static int gamma = 1;
static bool SAT = false;

static std::vector<bool> B;
static int size_B;

static int cnt_call = 0;
static int cnt_bound = 0;

static std::mt19937 seed(42);

struct BoolVectorHash {
    std::size_t operator()(const std::vector<bool>& vec) const {
        std::hash<bool> hasher;
        std::size_t hash = 0;
        for (bool b : vec) {
            hash ^= hasher(b) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
        }
        return hash;
    }
};

struct BoolVectorEqual {
    bool operator()(const std::vector<bool>& lhs, const std::vector<bool>& rhs) const {
        return lhs == rhs;
    }
};

static std::unordered_set<std::vector<bool>, BoolVectorHash, BoolVectorEqual> visited_partial_solutions;

struct KeyValuePair {
    int key;
    int value;

    // Constructor
    KeyValuePair(int k, int v) : key(k), value(v) {}

    // Overload the less-than operator for min-heap
    bool operator<(const KeyValuePair& other) const {
        return value > other.value; // Use greater than for min-heap
    }
};

std::vector<std::vector<int>> queen_graph_adj_lst() {
    std::vector<std::vector<int>> qgraph;

    for (int i = 0; i < n * n; i++) {
        std::set<int> N;
        N.insert(i);

        int r = i / n;
        int c = i % n;

        for (int j = 0; j < n * n; j++) {
            if (j < n) {
                N.insert(r * n + j);
                N.insert(j * n + c);
            }
            if ((r - c) == ((j / n) - (j % n)) || (r + c) == ((j / n) + (j % n))) {
                N.insert(j);
            }
        }

        std::vector<int> N_lst;
        for (auto x : N) N_lst.push_back(x);
        qgraph.push_back(N_lst);
    }
    return qgraph;
}


static int min_depth_b_exe = 1000000000;



static std::vector<int> levels;

void BS(std::vector<std::vector<int>>& qgraph, std::vector<bool>& P, int size_P, std::vector<bool> C, std::vector<int>& AC, std::vector<int>& NumQinRow, int max_row_1, int max_row_2, std::vector<int>& NumQinCol, int max_col_1, int max_col_2) {
    /*
   qgraph: queen graph
   P: current partial solution s.t., true means there is a queen in that square, and false means there is no queen there
   AC: stores number of queens attack a sqaure w.r.t. P
    */
    //std::vector<int> DD(n*n,0);
    //if (SAT) { return; } //should be removed
    cnt_call++;
    if (size_P > gamma || SAT || size_P >= size_B) { return; }

    ///*
    if ((max_row_1 > 2 * gamma - n + 2) || (max_col_1 > 2 * gamma - n + 2) || (max_row_1 + max_row_2 > 2 * gamma - n + 3) || (max_col_1 + max_col_2 > 2 * gamma - n + 3))
    {
        cnt_bound++; //return;
    }
    //*/

    std::vector<int> undominated_squares; for (int x = 0; x < AC.size(); x++) if (AC[x] == 0) undominated_squares.push_back(x);
    if (undominated_squares.size() == 0) {
        //if P is dominating set
        if (size_P < size_B) { //gamma
            size_B = size_P;
            B.clear();
            for (auto x : P) { B.push_back(x); }
            SAT = true;
        }
        return;
    }

    float k = size_P + (undominated_squares.size() * 1.0 / ((4 * n - 3) + 1)); //B1
    if (k > gamma || k >= size_B) { 
        cnt_bound++;
        //levels.push_back(size_P);
        //return;
    }

    ///* B2
    std::vector<int> DD(n * n, 0);
    for (auto u : undominated_squares) {
        for (auto s : qgraph[u]) {
            DD[s]++;
        }
    }
    std::vector<int> CDD;
    for (int z = 0; z < DD.size(); z++) { if (C[z])CDD.push_back(DD[z]); }
    std::priority_queue<int> maxHeap(CDD.begin(), CDD.end());
    int sum = 0; int q = 0;
    while (!maxHeap.empty() && sum < undominated_squares.size()) {
        int popped = maxHeap.top(); maxHeap.pop();
        sum += popped; q++;
    }
    k = size_P + q; //B2
    //*/
    if (k > gamma || k >= size_B) { 
        cnt_bound++; 
        levels.push_back(size_P);
        return;
    }

    ///* B3
    std::vector<int> DD_undom(undominated_squares.size(), 0);
    for (int u = 0; u < undominated_squares.size(); u++) {
        DD_undom[u] = DD[undominated_squares[u]];
    }

    std::vector<int> MDD(undominated_squares.size(), 0);//(4 * n - 3) + 1
    for (int a = 0; a < undominated_squares.size(); a++) {
        for (int b = 0; b < qgraph[undominated_squares[a]].size(); b++) {
            if (C[qgraph[undominated_squares[a]][b]]) {
                if (DD[qgraph[undominated_squares[a]][b]] > MDD[a]) {
                    MDD[a] = DD[qgraph[undominated_squares[a]][b]];
                }
            }
        }
    }


    std::vector<std::pair<int, std::pair<int, int>>> combined;
    for (size_t i = 0; i < MDD.size(); ++i) {
        //combined.push_back({ DD_undom[i], {undominated_squares[i], MDD[i]}});
        combined.push_back({ MDD[i], {undominated_squares[i], MDD[i]} });
    }
    std::sort(combined.begin(), combined.end());
    std::vector<int> sorted_undominated_squares;
    std::vector<int> sorted_MDD;

    for (const auto& pair : combined)
    {
        sorted_undominated_squares.push_back(pair.second.first); sorted_MDD.push_back(pair.second.second);
    }

    int ii = 0; int count = 0;
    while (ii < undominated_squares.size()) {
        count++;
        ii = ii + sorted_MDD[ii];
    }
    k = size_P + count; //B3
    //*/

    if (k > gamma || k >= size_B) {
        if (min_depth_b_exe > size_P)
            min_depth_b_exe = size_P; 
        cnt_bound++; 
        //levels.push_back(size_P);
        //return;
    }


    auto v = undominated_squares[0];



    ///* Prev impl of neigh ordering
    std::vector<int> valid_cadidate_squares; for (auto u : qgraph[v]) { if (C[u]) { valid_cadidate_squares.push_back(u); } }

    std::vector<bool> T(C);
    for (auto u : valid_cadidate_squares) {
        int r = u / n;
        int c = u % n;
        NumQinRow[r]++;
        int max_row_1_tmp = max_row_1;
        int max_row_2_tmp = max_row_2;
        if (NumQinRow[r] >= max_row_1)
        {
            max_row_2_tmp = max_row_1_tmp;
            max_row_1_tmp = NumQinRow[r];
        }
        else if (NumQinRow[r] >= max_row_2) {
            max_row_2_tmp = NumQinRow[r];
        }

        NumQinCol[c]++;
        int max_col_1_tmp = max_col_1;
        int max_col_2_tmp = max_col_2;
        if (NumQinCol[c] >= max_col_1)
        {
            max_col_2_tmp = max_col_1_tmp;
            max_col_1_tmp = NumQinCol[c];
        }
        else if (NumQinCol[c] >= max_col_2) {
            max_col_2_tmp = NumQinCol[c];
        }

        P[u] = true;
        T[u] = false;
        //C[u] = false;
        for (auto x : qgraph[u]) { AC[x]++; }
        //BS(qgraph, P, size_P + 1, C, AC, NumQinRow, max_row_1_tmp, max_row_2_tmp, NumQinCol, max_col_1_tmp, max_col_2_tmp);
        BS(qgraph, P, size_P + 1, T, AC, NumQinRow, max_row_1_tmp, max_row_2_tmp, NumQinCol, max_col_1_tmp, max_col_2_tmp);
        P[u] = false;
        for (auto x : qgraph[u]) { AC[x]--; }
        NumQinRow[r]--; NumQinCol[c]--;
    }
}



int main(int argc, char** argv) {

    std::time_t currentTime = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    char timeStr[100]; std::strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", std::localtime(&currentTime));

    n =11; gamma = 6;
    if (argc >= 3) { n = std::atoi(argv[1]); gamma = std::atoi(argv[2]); }


    std::cout << "n: " << n << " gamma: "<<gamma << "\n";
    std::cout << "Started: " << timeStr << "\n\n";
    auto start = std::chrono::high_resolution_clock::now();




    auto qgraph = queen_graph_adj_lst();
    size_B = qgraph.size();
    std::vector<bool> P(n * n, false);
    std::vector<bool> C(n * n, true);
    std::vector<int> AC(n * n, 0);
    std::vector<int> DD(n*n,0);//for (int j = 0; j < n * n; j++) { DD[j]=qgraph[j].size(); }
    std::vector<int> NumQinRow(n, 0);
    std::vector<int> NumQinCol(n, 0);
    int max_row_1=0; int max_row_2 = 0; int max_col_1 = 0; int max_col_2 = 0;

    BS(qgraph, P, 0, C, AC, NumQinRow, max_row_1, max_row_2, NumQinCol, max_col_1, max_col_2);

    std::cout << min_depth_b_exe <<"\n";
    if (SAT)
    {
        for (int r = 0; r < n; r++)
        {
            for (int c = 0; c < n; c++)
            {
                std::cout << " " << (B[r * n + c] ? "Q" : "-");
            }
            std::cout << "\n";
        }
    }
    else { std::cout << "UNSAT"; }

    std::cout << "\n" << "#calls: " << cnt_call << " #bound: " << cnt_bound << " benf%= " << cnt_bound * 1.0 / cnt_call <<"\n";

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    double seconds = duration.count();
    std::cout << "\ntime: " << seconds << " seconds\n";

    float average = std::accumulate(levels.begin(), levels.end(), 0.0)*1.0 / levels.size();
    int smallest_element = *std::min_element(levels.begin(), levels.end());
    int largestt_element = *std::max_element(levels.begin(), levels.end());
    std::cout << "\nmin: " << smallest_element<<" max: "<<largestt_element << " avg: " << average << "\n";
    return 0;
}
