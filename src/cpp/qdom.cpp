#include "cadical.hpp"

#ifdef NDEBUG
#undef NDEBUG
#endif

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

static int n = 3;
static int gamma = 1;

static CaDiCaL::Solver solver;


/* 
   This implementation follows Donald Knuth's irredundant variant
   of the C. Sinz's encoding, as suggested by Alex Healy. I have
   got it from pysat and I have modified it.
   
   I should check copyright, permission, etc.
*/
struct pair_hash {
    template <class T1, class T2>
    std::size_t operator () (const std::pair<T1, T2>& p) const {
        auto h1 = std::hash<T1>{}(p.first);
        auto h2 = std::hash<T2>{}(p.second);

        // Simple hash combining algorithm
        return h1 ^ h2;
    }
};

int mk_yvar(int& top_id, std::unordered_map<std::pair<int, int>, int, pair_hash>& vset, std::pair<int, int> np)
{
    auto ppos = vset.find(np);
    int nid = -1;

    if (ppos == vset.end()) {
        nid = ++top_id;
        vset.insert(make_pair(np, nid));
    }
    else
        nid = ppos->second;

    return nid;
}

void seqcounter_encode_atmostN(int& top_id, std::vector<std::vector<int>>& clset, std::vector<int>& vars, int tval) {
    std::unordered_map<std::pair<int, int>, int, pair_hash> p2i_map;
    for (size_t j = 0; j < vars.size() - tval; ++j) {
        int s0j = mk_yvar(top_id, p2i_map, std::make_pair(0, j));
        std::vector<int> c_new; c_new.push_back(-vars[j]); c_new.push_back(s0j); clset.push_back(c_new);

        for (int k = 0; k < tval - 1; ++k) {
            int skj = mk_yvar(top_id, p2i_map, std::make_pair(k, j));
            if (j < vars.size() - tval - 1) {
                int skj1 = mk_yvar(top_id, p2i_map, std::make_pair(k, j + 1));
                std::vector<int> c_new2; c_new2.push_back(-skj); c_new2.push_back(skj1); clset.push_back(c_new2);
            }

            int sk1j = mk_yvar(top_id, p2i_map, std::make_pair(k + 1, j));
            std::vector<int> c_new3; c_new3.push_back(-vars[j + k + 1]); c_new3.push_back(-skj); c_new3.push_back(sk1j); clset.push_back(c_new3);
        }

        int stj = mk_yvar(top_id, p2i_map, std::make_pair(tval - 1, j));
        if (j < vars.size() - tval - 1) {
            int stj1 = mk_yvar(top_id, p2i_map, std::make_pair(tval - 1, j + 1));
            std::vector<int> c_new4; c_new4.push_back(-stj); c_new4.push_back(stj1); clset.push_back(c_new4);
        }

        std::vector<int> c_new5; c_new5.push_back(-vars[j + tval]); c_new5.push_back(-stj); clset.push_back(c_new5);
    }
}

void seqcounter_encode_atleastN(int& top_id, std::vector<std::vector<int>>& clset, std::vector<int>& vars, int tval) {
    std::vector<int> ps;
    int nrhs = -tval;

    for (size_t i = 0; i < vars.size(); i++) {
        nrhs += 1;
        ps.push_back(-vars[i]);
    }
    seqcounter_encode_atmostN(top_id, clset, ps, nrhs);
}


/* 
   This code, encodes the queen domination problem into SAT.
*/
void encode_qdom(std::vector<std::vector<int>>& clset, int gamma) {

    for (int i = 0; i < n * n; i++) {
        std::set<int> N;
        N.insert(i+1);

        int r = i / n;
        int c = i % n;

        for (int j = 0; j < n * n; j++) {
            if (j < n) {
                N.insert(r * n + j+1);
                N.insert(j * n + c+1);
            }
            if ((r - c) == ((j / n) - (j % n)) || (r + c) == ((j / n) + (j % n))) {
                N.insert(j+1);
            }
        }

        std::vector<int> clause;
        for (auto ne : N) {
            clause.push_back(ne);
        }
        clset.push_back(clause);
    }

    int top_id = n * n;

    std::vector<int> vars;
    for (int i = 0; i < n * n; i++)
        vars.push_back((i + 1));

    seqcounter_encode_atleastN(top_id, clset, vars, gamma);
    seqcounter_encode_atmostN(top_id, clset, vars, gamma);

}


int main (int argc, char** argv) {

    if (argc >= 3) {n = std::atoi(argv[1]);gamma = std::atoi(argv[2]);}

    auto start = std::chrono::system_clock::now();
    std::time_t currentTime = std::chrono::system_clock::to_time_t(start);
    char timeStr[100];std::strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", std::localtime(&currentTime));
    std::cout << "Started: " << timeStr << std::endl;

    //solver.set("log",0);
    //solver.set("chrono",0);
    //solver.set("inprocessing",1);

    std::vector<std::vector<int>> clset;
    encode_qdom(clset,gamma);
    for (auto clause: clset) {
        for (auto item : clause) {
            solver.add(item);
            //std::cout << item<<" ";
        }
        //std::cout << std::endl;
        solver.add(0);
    }

    int res = solver.solve();
    if (res == 10) {
        std::cout << std::endl;
        for (int i = 0; i < n * n; i++) if (solver.val(i + 1) > 0) std::cout << solver.val(i + 1) << " ";
    }
    if(res==10) std::cout << std::endl<<"Result: " << "SAT" << std::endl;
    else if(res == 20)std::cout << std::endl << "Result: " << "UNSAT" << std::endl;
    else std::cout << std::endl << "Result: " << "??Unknown??" << std::endl;
    solver.statistics();
    return 0;
}