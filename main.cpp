#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <limits>
#include <chrono>  // For timing measurements
#include <iomanip> // For output formatting
#include <fstream> // For file operations
#include <string>  // For string operations
#include <filesystem> // For directory operations
using namespace std;
namespace fs = std::filesystem;

// Define a structure for state in the priority queue
struct State {
    int node;
    double g;   // cost from start to this node
    double f;   // g + h
};

// Comparator for the priority queue (min-heap based on f value)
struct CompareState {
    bool operator()(const State& a, const State& b) const {
        return a.f > b.f;  // smaller f has higher priority
    }
};

// Structure to hold graph data
struct GraphData {
    int numNodes;
    vector<vector<pair<int, double>>> adjacencyList;
    vector<pair<double, double>> coordinates;
    int startNode;
    int goalNode;
    string name;
};

// Function to read a graph from a file
GraphData readGraphFromFile(const string& filename) {
    GraphData graph;
    ifstream file(filename);
    
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        return graph;
    }
    
    // Read graph name
    getline(file, graph.name);
    
    // Read number of nodes
    file >> graph.numNodes;
    
    // Initialize adjacency list
    graph.adjacencyList.resize(graph.numNodes);
    
    // Read coordinates
    graph.coordinates.resize(graph.numNodes);
    for (int i = 0; i < graph.numNodes; i++) {
        file >> graph.coordinates[i].first >> graph.coordinates[i].second;
    }
    
    // Read start and goal nodes
    file >> graph.startNode >> graph.goalNode;
    
    // Read number of edges
    int numEdges;
    file >> numEdges;
    
    // Read edges
    for (int i = 0; i < numEdges; i++) {
        int u, v;
        double w;
        file >> u >> v >> w;
        graph.adjacencyList[u].emplace_back(v, w);
        graph.adjacencyList[v].emplace_back(u, w); // Assuming undirected graph
    }
    
    file.close();
    return graph;
}

int main() {
    string graphsFolder = "graphs";
    
    // Read all graph files from the folder
    vector<GraphData> graphs;
    for (const auto& entry : fs::directory_iterator(graphsFolder)) {
        if (entry.path().extension() == ".txt") {
            GraphData graph = readGraphFromFile(entry.path().string());
            if (graph.numNodes > 0) {
                graphs.push_back(graph);
            }
        }
    }
    
    if (graphs.empty()) {
        cout << "No valid graph files found in the folder." << endl;
        return 0;
    }
    
    // Process each graph
    for (const auto& graph : graphs) {
        cout << "Processing graph: " << graph.name << endl;
        cout << "Number of nodes: " << graph.numNodes << endl;
        cout << "Start node: " << graph.startNode << ", Goal node: " << graph.goalNode << endl;
        cout << endl;
        
        int N = graph.numNodes;
        int start = graph.startNode;
        int goal = graph.goalNode;
        const auto& coords = graph.coordinates;
        
        // Heuristic: Euclidean distance
        auto heuristic = [&](int node) {
            double dx = coords[node].first - coords[goal].first;
            double dy = coords[node].second - coords[goal].second;
            return sqrt(dx*dx + dy*dy);
        };

        // A* search algorithm (function template to accept heuristic as a parameter)
        auto runAStar = [&](auto&& heuristic) {
            const int NUM_RUNS = 100; // Run multiple times for more accurate timing
            long long totalNanoseconds = 0;
            int totalNodesExpanded = 0;
            int totalSteps = 0;
            double pathCost = 0;
            
            for (int run = 0; run < NUM_RUNS; run++) {
                // Start timing
                auto startTime = chrono::steady_clock::now(); // More consistent than high_resolution_clock
                
                // Min-heap priority queue for open set
                priority_queue<State, vector<State>, CompareState> open;
                // Distance (g-cost) array, initialize to infinity
                vector<double> dist(N, numeric_limits<double>::infinity());
                dist[start] = 0.0;
                // Start with the start node in the open set
                open.push({start, 0.0, heuristic(start)});

                vector<bool> closed(N, false);
                int nodesExpanded = 0;
                int steps = 0;

                while (!open.empty()) {
                    State cur = open.top();
                    open.pop();
                    steps++;

                    if (cur.g > dist[cur.node]) {
                        // This is a stale entry (we already found a better route to cur.node)
                        continue;
                    }

                    // Mark current node as expanded
                    nodesExpanded++;
                    if (cur.node == goal) {
                        // Goal reached; we can stop A* search
                        break;
                    }
                    closed[cur.node] = true;

                    // Explore neighbors
                    for (auto& [nbr, w] : graph.adjacencyList[cur.node]) {
                        double newG = cur.g + w;
                        if (newG < dist[nbr] && !closed[nbr]) {
                            // Found a better path to neighbor
                            dist[nbr] = newG;
                            double newF = newG + heuristic(nbr);
                            open.push({nbr, newG, newF});
                        }
                    }
                }

                // End timing
                auto endTime = chrono::steady_clock::now();
                auto duration = chrono::duration_cast<chrono::nanoseconds>(endTime - startTime);
                
                totalNanoseconds += duration.count();
                totalNodesExpanded += nodesExpanded;
                totalSteps += steps;
                
                // Save path cost (only need to do this once)
                if (run == 0) {
                    pathCost = (dist[goal] != numeric_limits<double>::infinity() ? dist[goal] : -1);
                }
            }
            
            // Calculate averages
            double avgTimeNs = static_cast<double>(totalNanoseconds) / NUM_RUNS;
            double avgNodesExpanded = static_cast<double>(totalNodesExpanded) / NUM_RUNS;
            double avgSteps = static_cast<double>(totalSteps) / NUM_RUNS;
            
            cout << "Average nodes expanded: " << fixed << setprecision(2) << avgNodesExpanded 
                 << ", Average steps: " << avgSteps << endl;
            cout << "Average execution time: " << fixed << setprecision(9) 
                 << avgTimeNs / 1000000.0 << " ms (" << avgTimeNs << " ns)" << endl;
            cout << "Min execution time: " << fixed << setprecision(9)
                 << static_cast<double>(totalNanoseconds) / (NUM_RUNS * 1000000.0) << " ms" << endl;
            cout << "Path cost to goal: " << pathCost << endl;
            cout << endl;
        };

        cout << "Using Euclidean distance heuristic:" << endl;
        runAStar(heuristic);
        
        cout << "----------------------------------------" << endl;
    }

    return 0;
}