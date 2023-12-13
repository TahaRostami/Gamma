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



static std::vector<std::vector<int>> queen_graph_adj_lst(int n) {
    std::vector<std::vector<int>> qgraph;

    for (int i = 0; i < n * n; i++) {
        std::set<int> N;
        //N.insert(i);

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
        for (auto x : N) if(x!=i) N_lst.push_back(x);
        qgraph.push_back(N_lst);
    }
    return qgraph;
}

class DominationDegreeMultisetNode {
public:
    int domination_degree;
    int count;
    int candidate_count;
    DominationDegreeMultisetNode* next;
    DominationDegreeMultisetNode* prev;

    DominationDegreeMultisetNode(int degree, int c, int candidate) : domination_degree(degree), count(c), candidate_count(candidate), next(nullptr), prev(nullptr) {}
};

class DominationDegreeMultiset {
private:
    DominationDegreeMultisetNode* sentinel;
    std::vector<DominationDegreeMultisetNode*> DegreeNodes;
    std::vector<DominationDegreeMultisetNode*> VertexDegreeNode;
    int delta=-1;
public:
    DominationDegreeMultiset() {};
    DominationDegreeMultiset(std::vector<std::vector<int>>& G, int delta) {
        this->delta = delta;
        sentinel = new DominationDegreeMultisetNode(0, 0, 0);
        sentinel->next = sentinel;
        sentinel->prev = sentinel;
        DegreeNodes= std::vector<DominationDegreeMultisetNode*>(delta+1);
        for (int d = 0; d < DegreeNodes.size(); d++){DegreeNodes[d] = new DominationDegreeMultisetNode(d,0, 0);}
        VertexDegreeNode=std::vector<DominationDegreeMultisetNode*>(G.size());

        for (int i = 0; i < G.size(); i++)
        {
            auto init_dom_degree=G[i].size()+1;
            VertexDegreeNode[i] = DegreeNodes[init_dom_degree];
            VertexDegreeNode[i]->count++;
            VertexDegreeNode[i]->candidate_count++;
        }

        for (int d = 0; d < DegreeNodes.size(); d++){
            if (DegreeNodes[d]->count>0){
                DegreeNodes[d]->prev = sentinel->prev;
                DegreeNodes[d]->next = sentinel;
                sentinel->prev->next = DegreeNodes[d];
                sentinel->prev = DegreeNodes[d];
            }
        }     
    }

    ~DominationDegreeMultiset() {
        //clear();
        //delete sentinel;
    }

    void add_candidate(int v_i) {
        VertexDegreeNode[v_i]->candidate_count++;
    }
    void remove_candidate(int v_i) {
        VertexDegreeNode[v_i]->candidate_count--;
    }
    int domination_degree(int v_i) {
        return VertexDegreeNode[v_i]->domination_degree;
    }
    int min_to_dominate(int k) {
        int q = 0;
        auto node = sentinel->prev;
        while (node != sentinel)
        {
            auto c = (node->domination_degree)*(node->candidate_count);
            if (k <= c)
                return q + ceil(k/node->domination_degree);
            else {
                q = q + node->candidate_count;
                k = k - c;
            }
            node = node->prev;
        }
        return delta + 1;
    }

    
    void increment(int v_i,std::vector<bool>& C) {
        auto old_node = VertexDegreeNode[v_i];
        auto old_deg = old_node->domination_degree;
        auto new_deg = old_deg + 1;
        auto new_node = DegreeNodes[new_deg];
        auto old_count = old_node->count;
        auto new_count = new_node->count;
        if (new_count == 0)
        {
            new_node->next = old_node->next;
            new_node->prev = old_node;
            old_node->next->prev = new_node;
            old_node->next = new_node;
        }
        VertexDegreeNode[v_i] = new_node;
        old_node->count--;
        new_node->count++;
        if (C[v_i])
        {
            old_node->candidate_count--;
            new_node->candidate_count++;
        }
        if (old_node->count == 0)//unidom had bug, this line fixes that
        {
            new_node->prev = old_node->prev;
            new_node->prev->next = new_node;
            old_node->next = NULL;
            old_node->prev = NULL;
        }
    }

    void decrement(int v_i, std::vector<bool>& C) {
        auto old_node = VertexDegreeNode[v_i];
        auto old_deg = old_node->domination_degree;
        auto new_deg = old_deg - 1;
        auto new_node = DegreeNodes[new_deg];
        auto old_count = old_node->count;
        auto new_count = new_node->count;
        if (new_count == 0)
        {
            new_node->next = old_node;
            new_node->prev = old_node->prev;
            old_node->prev->next = new_node;
            old_node->prev = new_node;
        }
        VertexDegreeNode[v_i] = new_node;
        old_node->count--;
        new_node->count++;
        if (C[v_i]) {
            old_node->candidate_count--;
            new_node->candidate_count++;
        }
        if (old_node->count == 0)//unidom had bug, this line fixes that
        {
            new_node->next = old_node->next;
            new_node->next->prev = new_node;
            old_node->next = NULL;
            old_node->prev = NULL;
        }
    }


    void display() const {
        DominationDegreeMultisetNode* current = sentinel->next;
        while (current != sentinel) {
            std::cout << "Domination Degree: " << current->domination_degree
                << ", Count: " << current->count
                << ", Candidate Count: " << current->candidate_count << std::endl;
            current = current->next;
        }
        std::cout << std::endl;
    }

    //void removeFront() {
    //        if (sentinel->next != sentinel) {
    //            DominationDegreeMultisetNode* temp = sentinel->next;
    //            sentinel->next = temp->next;
    //            temp->next->prev = sentinel;
    //            delete temp;
    //        }
    //}
    //void clear() {
    //   while (sentinel->next != sentinel) {
    //        removeFront();
    //   }
    //}
};

//......

class VertexNode;
static void find_dominating_set(std::vector<std::vector<int>>& G, std::vector<bool>& P, std::vector<bool>& C,
    std::vector<bool>& B, int desired_size, int& size_B, std::vector<bool>& N_P, int& size_N_P, int& size_P);

class CandidateDegreeNode {
public:
    int candidate_degree;
    int count;
    int undominated_count;
    VertexNode* undominated_list_sentinel;
    CandidateDegreeNode* next;
    CandidateDegreeNode* prev;

    CandidateDegreeNode(int degree);
    void insertAfter(VertexNode* newNode);
    void remove(VertexNode* nodeToRemove);
};

class VertexNode {
public:
    int index;
    VertexNode* next;
    VertexNode* prev;
    CandidateDegreeNode* degree_node;
    bool is_dominated;

    VertexNode(int idx, CandidateDegreeNode* degree);
};

CandidateDegreeNode::CandidateDegreeNode(int degree)
    : candidate_degree(degree), count(0), undominated_count(0), undominated_list_sentinel(nullptr), next(nullptr), prev(nullptr) {
    undominated_list_sentinel = new VertexNode(-1, this);
    undominated_list_sentinel->next = undominated_list_sentinel;
    undominated_list_sentinel->prev = undominated_list_sentinel;
}

void CandidateDegreeNode::insertAfter(VertexNode* newNode) {
    if (!undominated_list_sentinel) {
        undominated_list_sentinel = newNode;
        undominated_list_sentinel->next = undominated_list_sentinel;
        undominated_list_sentinel->prev = undominated_list_sentinel;
    }
    else {
        newNode->next = undominated_list_sentinel->next;
        newNode->prev = undominated_list_sentinel;
        undominated_list_sentinel->next->prev = newNode;
        undominated_list_sentinel->next = newNode;
    }
}

void CandidateDegreeNode::remove(VertexNode* nodeToRemove) {
    if (undominated_list_sentinel == nodeToRemove) {
        undominated_list_sentinel = nodeToRemove->next;
        if (nodeToRemove->next == nodeToRemove) {
            undominated_list_sentinel = nullptr;
        }
    }
    nodeToRemove->prev->next = nodeToRemove->next;
    nodeToRemove->next->prev = nodeToRemove->prev;
    nodeToRemove->next = nullptr;
    nodeToRemove->prev = nullptr;
}

VertexNode::VertexNode(int idx, CandidateDegreeNode* degree)
    : index(idx), next(nullptr), prev(nullptr), degree_node(degree), is_dominated(false) {}

class CandidateDegreePriorityQueue {
private:
    int delta;
    std::vector<VertexNode*> VertexNodes;
    std::vector<CandidateDegreeNode*> DegreeNodes;
    CandidateDegreeNode* sentinel;

public:
    int cnt_dominated = 0;

    CandidateDegreePriorityQueue() {}

    CandidateDegreePriorityQueue(std::vector<std::vector<int>>& G, int delta) {
        this->delta = delta;
        DegreeNodes = std::vector<CandidateDegreeNode*>(delta + 1);
        VertexNodes = std::vector<VertexNode*>(G.size());
        sentinel = new CandidateDegreeNode(-1);
        sentinel->next = sentinel;
        sentinel->prev = sentinel;
        for (int d = 0; d < delta + 1; d++) { DegreeNodes[d] = new CandidateDegreeNode(d); }
        for (int v = 0; v < G.size(); v++) 
        { 
            auto node = DegreeNodes[G[v].size() + 1];
            VertexNodes[v] = new VertexNode(v, node);
            node->insertAfter(VertexNodes[v]);
            node->count++;
            node->undominated_count++;
        }

        for (int d = 0; d < delta + 1; d++) {
            if (DegreeNodes[d]->count > 0) {
                DegreeNodes[d]->prev = sentinel->prev;
                DegreeNodes[d]->next = sentinel;
                sentinel->prev->next = DegreeNodes[d];
                sentinel->prev = DegreeNodes[d];
            }
        }

    }

    void dominate(int v_i) {
        cnt_dominated++;
        auto vertex_node = VertexNodes[v_i];
        vertex_node->is_dominated = true;
        vertex_node->degree_node->undominated_count--;
        splice_out(vertex_node);
    }

    bool is_dominated(int v_i) {
        return VertexNodes[v_i]->is_dominated;
    }

    void undominate(int v_i) {
        cnt_dominated--;
        auto vertex_node = VertexNodes[v_i];
        vertex_node->is_dominated = true;
        vertex_node->degree_node->undominated_count++;
        splice_in(vertex_node);
    }

    int candidate_degree(int vi) {
        return VertexNodes[vi]->degree_node->candidate_degree;
    }

    void increment(int v_i,std::vector<bool>& C) {
        auto vertex_node = VertexNodes[v_i];
        auto old_degree_node = vertex_node->degree_node;
        auto old_deg = old_degree_node->candidate_degree;//undom had bug, this line fixes it
        auto new_deg = old_deg + 1;
        //if (new_deg >= DegreeNodes.size())
        //{
        //    new_deg = DegreeNodes.size() - 1;
        //}
        auto new_degree_node = DegreeNodes[new_deg];
        auto old_count = old_degree_node->count;
        auto new_count = new_degree_node->count;
        if (new_count == 0)//undom has bug, should be changed
        {
            new_degree_node->next = old_degree_node->next;
            new_degree_node->prev = old_degree_node;
            old_degree_node->next->prev = new_degree_node;
            old_degree_node->next = new_degree_node;
        }
        old_degree_node->count--;
        if (vertex_node->is_dominated == false)
        {
            splice_out(vertex_node);
            old_degree_node->undominated_count--;
        }
        vertex_node->degree_node = new_degree_node;
        if (vertex_node->is_dominated == false)
        {
            splice_in(vertex_node);
            new_degree_node->undominated_count++;
        }
        new_degree_node->count++;
        if (old_degree_node->count == 0)//undom has bug, should be changed
        {
            new_degree_node->prev = old_degree_node->prev;
            new_degree_node->prev->next = new_degree_node;
            old_degree_node->next = NULL;
            old_degree_node->prev = NULL;
        }
    }

    void decrement(int v_i, std::vector<bool>& C) {
        auto vertex_node = VertexNodes[v_i];
        auto old_degree_node = vertex_node->degree_node;
        auto old_deg = old_degree_node->candidate_degree;//undom had bug, this line fixes it
        auto new_deg = old_deg - 1;//undom had bug, this line fixes that
        auto new_degree_node = DegreeNodes[new_deg];
        auto old_count = old_degree_node->count;
        auto new_count = new_degree_node->count;
        if (new_count == 0)//undom had bug, this line fixes that
        {
            new_degree_node->next = old_degree_node;
            new_degree_node->prev = old_degree_node->prev;
            old_degree_node->prev->next = new_degree_node;
            old_degree_node->prev = new_degree_node;
        }
        old_degree_node->count--;
        if (vertex_node->is_dominated == false)
        {
            splice_out(vertex_node);
            old_degree_node->undominated_count--;
        }
        vertex_node->degree_node = new_degree_node;
        if (vertex_node->is_dominated == false)
        {
            splice_in(vertex_node);
            new_degree_node->undominated_count++;
        }
        new_degree_node->count = new_degree_node->count + 1;
        if (old_degree_node->count == 0) //undom had bug, this line fixes that
        {
            new_degree_node->next = old_degree_node->next;
            new_degree_node->next->prev = new_degree_node;
            old_degree_node->next = NULL;
            old_degree_node->prev = NULL;
        }
    }

    int get_min_undominated() {
        auto degree_node = sentinel->next;
        while(degree_node != sentinel) {
            if (degree_node->undominated_count > 0)
            {
                return degree_node->undominated_list_sentinel->next->index;
            }
            degree_node = degree_node->next;
        }
        return -1;
    }

    int get_max_undominated() {
        auto degree_node = sentinel->prev;
        while (degree_node != sentinel) {
            if (degree_node->undominated_count > 0)
            {
                return degree_node->undominated_list_sentinel->next->index;
            }
            degree_node = degree_node->prev;
        }
        return -1;
    }

    void splice_in(VertexNode* vertex_node) {
        auto degree_node = vertex_node->degree_node;
        vertex_node->next = degree_node->undominated_list_sentinel;
        vertex_node->prev = degree_node->undominated_list_sentinel->prev;
        vertex_node->next->prev = vertex_node;
        vertex_node->prev->next = vertex_node;
    }

    void splice_out(VertexNode* vertex_node) {
        vertex_node->next->prev = vertex_node->prev;
        vertex_node->prev->next = vertex_node->next;
        vertex_node->next = NULL;
        vertex_node->prev = NULL;
    }
};


static DominationDegreeMultiset DDMS;
static CandidateDegreePriorityQueue CDPQ;

static bool add_vertex(std::vector<std::vector<int>>& G, std::vector<bool>& P,
    std::vector<bool>& C, std::vector<bool>& B,int desired_size, std::stack<int>& F,int v_j
    ,int& size_B, std::vector<bool>& N_P, int& size_N_P, int& size_P)
{
    if (C[v_j]==false){ return false;}
    F.push(v_j);
    C[v_j] = false;

    DDMS.remove_candidate(v_j);
    bool force_stop = false;

    auto NeighbourList = std::vector<int>(G[v_j]);
    NeighbourList.push_back(v_j);

    for (auto v_k : NeighbourList)
    {
        if (N_P[v_k]==false)
        {
            CDPQ.dominate(v_k);
        }
        CDPQ.decrement(v_k,C);
        if (CDPQ.candidate_degree(v_k) == 0)
        {
            force_stop = true;
        }
        if (N_P[v_j] == false)
        {
            DDMS.decrement(v_k,C);
        }
    }

 
    //This part is hard coded(and is not efficient) for debuging purposes
    auto tmp = std::vector<bool>(N_P);

    P[v_j] = true; size_P++; N_P[v_j]=true;

    for (auto x : G[v_j]) {if (N_P[x] == false){ N_P[x] = true;}}
    size_N_P = 0; for (auto x : N_P) if (x) size_N_P++;
    

    find_dominating_set(G, P, C, B, desired_size,size_B,N_P,size_N_P,size_P);
    
    N_P = tmp;
    P[v_j] = false; size_P--;
    size_N_P = 0; for (auto x : N_P) if (x) size_N_P++;

    return force_stop;

}


static void restore_candidate(std::vector<std::vector<int>>& G, std::vector<bool>& P,
    std::vector<bool>& C, std::vector<bool>& B, int desired_size, int v_j, std::vector<bool>& N_P) {
    
    C[v_j] = true;
    DDMS.add_candidate(v_j);

    auto NeighbourList = std::vector<int>(G[v_j]);
    NeighbourList.push_back(v_j);

    for (auto v_k : NeighbourList)
    {
        if (N_P[v_k] == false)//it might have bug or might not , CDPQ.is_dominated(v_k) == false? CDPQ.is_dominated(v_k) == true
        {
            CDPQ.undominate(v_k);
        }
        CDPQ.increment(v_k,C);
        if (N_P[v_j] == false)//it might have bug or might not , CDPQ.is_dominated(v_k) == false? CDPQ.is_dominated(v_k) == true
        {
            DDMS.increment(v_k, C);
        }
    }

}

static void find_dominating_set(std::vector<std::vector<int>>& G, std::vector<bool>& P, std::vector<bool>& C,
    std::vector<bool>& B, int desired_size, int& size_B, std::vector<bool>& N_P, int& size_N_P, int& size_P) {

    if (size_N_P ==G.size())
    {
        if (size_P < size_B)
        {
            for (int x = 0; x < P.size(); x++) B[x] = P[x];
            size_B = size_P;
        }
        return;
    }
    int k=DDMS.min_to_dominate(G.size()- size_N_P) + size_P;
    if (k >= size_B or k > desired_size){return;}
    auto v = CDPQ.get_max_undominated(); //v ← ChooseNextVertex(G, P, C)
    
    if (v < 0) return;

    auto NeighbourList = std::vector<int>(G[v]);
    NeighbourList.push_back(v);

    //TODO:Sort NeighbourList by domination degree
    std::stack<int> F;
    for (auto v_j : NeighbourList)
    {
        if (C[v_j])
        {
            auto force_stop = add_vertex(G, P, C, B, desired_size, F, v_j,size_B,N_P,size_N_P,size_P);
            //F.push(v_j); // unidom had bug, this line and the above one fix it
            if (force_stop) break;
        }
    }
    while (!F.empty())
    {
        auto j = F.top();
    	F.pop();
        restore_candidate(G, P, C, B, desired_size, j,N_P);
    }

}

int main() {
    int n = 3; int delta = 4 * n - 3;
    auto G = queen_graph_adj_lst(n);
    auto C = std::vector<bool>(G.size(),true);
    auto P = std::vector<bool>(G.size(), false);
    auto B = std::vector<bool>(G.size(), true);
    DDMS = DominationDegreeMultiset(G, delta);
    CDPQ = CandidateDegreePriorityQueue(G, delta);


    int size_B = B.size();
    auto N_P= std::vector<bool>(G.size(), false);
    int size_N_P = 0;
    int size_P = 0;

    find_dominating_set(G, P, C, B, G.size(),size_B,N_P,size_N_P,size_P);

    for (int r = 0; r < n; r++)
	{
		for (int c = 0; c < n; c++)
		{
			std::cout << " " << (B[r * n + c] ? "Q" : "-");
		}
		std::cout << "\n";
	}
    return 0;
}

