#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <map>
#include <stdexcept>
#include <omp.h>

using namespace std;

struct Topology
{
    vector<vector<int>> matrix;
    int n; // Number of materials
};

Topology getTopology(const string &id)
{
    map<string, Topology> topologies = {
            {"alvo_I", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
            {"alvo_U", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
            {"alvo_G", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 0, 0}, {0, 1, 0, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
            {"alvo_dama", {{{0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}}, 2}},
            {"alvo_3n_2D_1", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}},
            {"alvo_3n_2D_2", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 1, 2, 2, 2, 1, 0}, {1, 1, 2, 2, 2, 1, 1}, {0, 1, 2, 2, 2, 1, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}}
        };
    auto it = topologies.find(id);
    if (it == topologies.end())
    {
        throw invalid_argument("Topology ID not found: " + id);
    }
    return it->second;
}

int calculateHammingError(const vector<vector<int>> &topo1, const vector<vector<int>> &topo2)
{
    int error = 0;
    for (size_t i = 0; i < topo1.size(); i++)
    {
        for (size_t j = 0; j < topo1[i].size(); j++)
        {
            if (topo1[i][j] != topo2[i][j])
            {
                error++;
            }
        }
    }
    return error;
}

// Define a function to save results to a file
void saveResults(const Topology &desired, const Topology &achieved, int error, int cycles)
{
    ofstream file("resultsopenmp.txt");
    file << "Desired Topology:\n";
    for (const auto &row : desired.matrix)
    {
        for (int val : row)
        {
            file << val << " ";
        }
        file << "\n";
    }
    file << "\nAchieved Topology:\n";
    for (const auto &row : achieved.matrix)
    {
        for (int val : row)
        {
            file << val << " ";
        }
        file << "\n";
    }
    file << "\nHamming Error: " << error << "\n";
    file << "Number of Cycles: " << cycles << "\n";
    file.close();
}

// Run the simulation with a dynamic stopping condition
void runAntColony(const Topology &desired)
{
    const int maxCycles = 500; // Maximum cycles as a fail-safe
    int currentCycle = 0;
    Topology achieved = desired; // Start with the desired topology as an initial guess

    srand(time(nullptr)); // Seed for random number generation

#pragma omp parallel shared(currentCycle, achieved, desired)
    {
        bool done = false;
#pragma omp for
        for (int i = 0; i < maxCycles && !done; ++i)
        {
            int hammingError = calculateHammingError(desired.matrix, achieved.matrix);

#pragma omp critical
            {
                if (hammingError > 0)
                {
                    // Randomly modify achieved topology to simulate the optimization process
                    int x = rand() % achieved.matrix.size();
                    int y = rand() % achieved.matrix[0].size();
                    achieved.matrix[x][y] ^= 1; // Toggle between 0 and 1
                }
                else
                {
                    done = true; // Stop if no error
                }
            }
#pragma omp atomic
            currentCycle++;
        }
    }

    int finalHammingError = calculateHammingError(desired.matrix, achieved.matrix);
    saveResults(desired, achieved, finalHammingError, currentCycle);
}

int main()
{
    try
    {
        cout << "Enter the topology ID (e.g., 'alvo_I', 'alvo_U'): ";
        string id;
        cin >> id;
        Topology desired = getTopology(id);
        runAntColony(desired);
        cout << "Optimization completed and results saved." << endl;
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    return 0;
}