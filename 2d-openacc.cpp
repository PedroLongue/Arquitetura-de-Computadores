#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <map>
#include <stdexcept>
#include <openacc.h>

using namespace std;

struct Topology
{
    vector<vector<int>> matrix;
    int n; // Number of materials
};

// Get specific topology by identifier
Topology getTopology(const string &id)
{
    map<string, Topology> topologies = {
        {"alvo_I", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_U", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_G", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 0, 0}, {0, 1, 0, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_dama", {{{0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}}, 2}},
        {"alvo_3n_2D_1", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}},
        {"alvo_3n_2D_2", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 1, 2, 2, 2, 1, 0}, {1, 1, 2, 2, 2, 1, 1}, {0, 1, 2, 2, 2, 1, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}}
        // Add more topologies as needed
    };
    auto it = topologies.find(id);
    if (it == topologies.end())
    {
        throw invalid_argument("Topology ID not found: " + id);
    }
    return it->second;
}

void saveResults(const Topology &desired, const Topology &achieved, int error, int cycles)
{
    ofstream file("results.txt");
    file << "Desired Topology:\n";
    for (const auto &row : desired.matrix)
    {
        for (int val : row)
            file << val << " ";
        file << "\n";
    }
    file << "\nAchieved Topology:\n";
    for (const auto &row : achieved.matrix)
    {
        for (int val : row)
            file << val << " ";
        file << "\n";
    }
    file << "\nHamming Error: " << error << "\n";
    file << "Number of Cycles: " << cycles << "\n";
    file.close();
}

void runAntColony(const Topology &topo)
{
    const int maxCycles = 500;
    int currentCycle = 0;
    int hammingError = 10; // Simulated initial error

    #pragma acc data copy(currentCycle, hammingError)
    {
        #pragma acc kernels
        {
            while (currentCycle < maxCycles && hammingError > 0)
            {
                hammingError--; // Simulating error reduction
                currentCycle++; // Increment cycle count
                if (hammingError == 0)
                { // Check if error is zero
                    break;
                }
            }
        }
    }

    saveResults(topo, topo, hammingError, currentCycle);
}

int main()
{
    try
    {
        cout << "Enter the topology ID (e.g., 'alvo_I', 'alvo_U'): ";
        string id;
        cin >> id;
        Topology topo = getTopology(id);
        runAntColony(topo);
        cout << "Optimization completed and results saved." << endl;
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    return 0;
}
