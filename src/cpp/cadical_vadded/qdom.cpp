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
#include <queue>

static int n = 3;
static int gamma = 1;

static CaDiCaL::Solver solver;
static std::vector<std::set<int>> qgraph;

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

/*got from https://www.geeksforgeeks.org/make-combinations-size-k/
  and a little bit has been modified
*/


void makeCombiUtil(std::vector<std::vector<int>>& ans, std::vector<int>& tmp, std::vector<int> in_lst, int left, int k)
{
    // Pushing this vector to a vector of vector
    if (k == 0) {
        ans.push_back(tmp);
        return;
    }

    // i iterates from left to n. First time
    // left will be 0
    for (int i = left; i <= in_lst.size() - k; ++i)
    {
        tmp.push_back(in_lst[i]);
        makeCombiUtil(ans, tmp, in_lst, i + 1, k - 1);

        // Popping out last inserted element
        // from the vector
        tmp.pop_back();
    }
}

std::vector<std::vector<int>> makeCombi(std::vector<int> in_lst, int k)
{
    std::vector<std::vector<int>> ans;
    std::vector<int> tmp;
    makeCombiUtil(ans, tmp, in_lst, 0, k); // Start from index 0
    return ans;
}

/* 
   This code, encodes the queen domination problem into SAT.
*/
void encode_qdom(std::vector<std::vector<int>>& clset, int gamma) {

    std::vector<int> vars;
    for (int i = 0; i < n * n; i++)vars.push_back((i + 1));

    // basic encoding
    for (int i = 0; i < n * n; i++) {
        std::set<int> N;
        N.insert(vars[i]);

        int r = i / n;
        int c = i % n;

        for (int j = 0; j < n * n; j++) {
            if (j < n) {
                N.insert(vars[r * n + j]);
                N.insert(vars[j * n + c]);
            }
            if ((r - c) == ((j / n) - (j % n)) || (r + c) == ((j / n) + (j % n))) {
                N.insert(vars[j]);
            }
        }

        std::vector<int> clause;
        for (auto ne : N) {
            clause.push_back(ne);
        }
        clset.push_back(clause);
    }

    // encoding the first lemma
    ///*
    for (int r = 0; r < n; r++) {
        std::vector<int> curr_row;
        std::vector<int> curr_col;
        for (int c = 0; c < n; c++) {
            curr_row.push_back(vars[r * n + c]);
            curr_col.push_back(vars[c * n + r]);
        }
        std::vector<int> clause_row;
        for (const auto& comb : makeCombi(curr_row, 2 * gamma - n + 2 + 1)) {for (int item : comb) {clause_row.push_back(-item);}}
        clset.push_back(clause_row);

        std::vector<int> clause_col;
        for (const auto& comb : makeCombi(curr_col, 2 * gamma - n + 2 + 1)) { for (int item : comb) { clause_col.push_back(-item); } }
        clset.push_back(clause_col);
    }
    //*/

    // encoding the main cardinality constraints
    int top_id = n * n;
    seqcounter_encode_atleastN(top_id, clset, vars, gamma);
    seqcounter_encode_atmostN(top_id, clset, vars, gamma);

}


void add_formula_to_SAT_solver(CaDiCaL::Solver& solver, std::vector<std::vector<int>>& clset) {
    for (auto clause : clset) {
        for (auto item : clause) {
            solver.add(item);
        }
        solver.add(0);
    }
}


void create_qdom_instance(CaDiCaL::Solver& solver,int n, int gamma) {
    std::vector<std::vector<int>> clset;
    encode_qdom(clset, gamma);
    add_formula_to_SAT_solver(solver, clset);
}

void queen_graph() {
    std::vector<int> vars;
    for (int i = 0; i < n * n; i++)vars.push_back((i + 1));

    // basic encoding
    for (int i = 0; i < n * n; i++) {
        std::set<int> N;
        N.insert(vars[i]);

        int r = i / n;
        int c = i % n;

        for (int j = 0; j < n * n; j++) {
            if (j < n) {
                N.insert(vars[r * n + j]);
                N.insert(vars[j * n + c]);
            }
            if ((r - c) == ((j / n) - (j % n)) || (r + c) == ((j / n) + (j % n))) {
                N.insert(vars[j]);
            }
        }
        qgraph.push_back(N);
    }
}



class QDSolver : CaDiCaL::ExternalPropagator {
    CaDiCaL::Solver* solver;
    std::vector<std::vector<int>> new_clauses;
    std::deque<std::vector<int>> current_trail;

public:
    QDSolver(CaDiCaL::Solver* s) : solver(s) {
        solver->connect_external_propagator(this);
        for (int i = 0; i < n * n; i++)
        {
            solver->add_observed_var(i + 1);
            //solver->phase(i + 1);
        }

        // The root-level of the trail is always there
        current_trail.push_back(std::vector<int>());
    }

    ~QDSolver() {
        solver->disconnect_external_propagator();
    }

    void notify_assignment(int lit, bool is_fixed) {
        //if (is_fixed) {
        //    current_trail.front().push_back(lit);
        //}
        //else {
        //    current_trail.back().push_back(lit);
        //}

    }

    void notify_new_decision_level() {
        /*current_trail.push_back(std::vector<int>());*/
    }

    void notify_backtrack(size_t new_level) {
        //while (current_trail.size() > new_level + 1) {
        //    current_trail.pop_back();
        //}
    }

    bool cb_check_found_model(const std::vector<int>& model) {
        (void)model;
        return true;
    }

    bool cb_has_external_clause() {

        ///*
        std::priority_queue<int> pq_DD;
        std::vector<int> AC(n*n,0);
        int size_P = 0;
        int cnt_undom = n*n;
        for (int i = 0; i < n * n; i++)
        {
            if (solver->value(i + 1) > 0)
            {
                size_P++;
                for (auto v : qgraph[i])
                {
                    AC[v - 1]++;
                    if (AC[v - 1] == 1)
                    {
                        cnt_undom--;
                    }
                }
            }
            else if (solver->value(i + 1) == 0)
            {
                int DD = 0;
                for (auto v : qgraph[i])
                {
                    bool is_undominated = true;
                    for (auto u : qgraph[v-1]) {
                        if (solver->value(u) > 0)
                        {
                            is_undominated = false;
                            break;
                        }
                    }
                    if(is_undominated)
                    {
                        DD++;
                    }
                }
                pq_DD.push(DD);
                
            }
            //std::cout << solver->value(i + 1) << " ";
        }

        int sum = 0;
        int k = 0;
        while (!pq_DD.empty() && sum<cnt_undom)
        {
            //std::cout << pq_DD.top() << " ";
            k++;
            sum += pq_DD.top();
            pq_DD.pop();
        }
        //std::cout << "\n";


        if (k + size_P > gamma)
        {
            std::vector<int> clause;
            for (int i = 0; i < n * n; i++)
            {
                if (solver->value(i + 1) > 0)
                {
                    clause.push_back(-(i + 1));
                }
                else if (solver->value(i + 1) < 0)
                {
                    clause.push_back((i + 1));
                }
            }
            new_clauses.push_back(clause);
        }
        //*/
        //std::cout<< "n: " << n << " gamma: " << gamma <<" min needed:" << k + size_P << "cnt_undom: "<< cnt_undom << "\n";
        return (!new_clauses.empty());
    }

    int cb_add_external_clause_lit() {
        //return 0;
        ///*
         if (new_clauses.empty()) return 0;
         else {
            assert(!new_clauses.empty());
            size_t clause_idx = new_clauses.size() - 1;
            if (new_clauses[clause_idx].empty()) {
                new_clauses.pop_back();
                return 0;
            }

            int lit = new_clauses[clause_idx].back();
            new_clauses[clause_idx].pop_back();
            return lit;
         }
        //*/
    }

    int cb_decide() {

        //if(sel!=0) solver->phase(sel);
        return 0;
    }

    int cb_propagate() { return 0; }
    int cb_add_reason_clause_lit(int plit) {
        (void)plit;
        return 0;
    };
};

int main (int argc, char** argv) {

    n = 4;
    gamma = 2;

    if (argc >= 3) {n = std::atoi(argv[1]);gamma = std::atoi(argv[2]);}

    queen_graph();

    auto start = std::chrono::system_clock::now();
    std::time_t currentTime = std::chrono::system_clock::to_time_t(start);
    char timeStr[100];std::strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", std::localtime(&currentTime));
    std::cout << "Started: " << timeStr << std::endl;

    //std::cout<< solver.set("log",0) <<"\n";
    std::cout<< solver.set("chrono", 0)<<"\n";
    //std::cout<< solver.set("inprocessing", 0)<<"\n";
    //std::cout << solver.set("stabilize", 0) << "\n";
    //std::cout << solver.set("walk", 0) << "\n";
    //solver.usage();
    //solver.options();

    create_qdom_instance(solver, n, gamma);
    QDSolver qds(&solver);

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