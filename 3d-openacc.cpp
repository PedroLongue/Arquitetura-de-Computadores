#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <random>
#include <climits>
#include <fstream>
#include <openacc.h>
#include <chrono>

using namespace std;

struct Topology3D
{
    vector<vector<vector<int>>> matrix;
    int nl, nc, p; // Dimensions: lines, columns, depth
    int n;         // Number of materials
};

// Function to define topologies
Topology3D getTopology3D(const string &id)
{
    if (id == "alvo_3n_3D_1")
    {
        return {
            {{{0, 0, 0}, {1, 1, 1}, {2, 2, 2}},
             {{0, 0, 0}, {1, 1, 1}, {2, 2, 2}},
             {{0, 0, 0}, {1, 1, 1}, {2, 2, 2}}},
            3,
            3,
            3,
            3};
    }
    else if (id == "alvo_3n_3D_2")
    {
        return {
            {{{2, 2, 1, 1}, {2, 0, 0, 1}, {2, 0, 0, 1}, {2, 2, 1, 1}},
             {{2, 2, 1, 1}, {2, 0, 0, 1}, {2, 0, 0, 1}, {2, 2, 1, 1}},
             {{2, 2, 1, 1}, {2, 0, 0, 1}, {2, 0, 0, 1}, {2, 2, 1, 1}}},
            3,
            4,
            4,
            3};
    }
    else
    {
        throw invalid_argument("Topology ID not found: " + id);
    }
}

// Initialize matrix with random values using OpenACC
void initializeRandomMatrix3D(vector<vector<vector<int>>> &matrix, int maxMaterial)
{
    // Use OpenACC for parallelization
#pragma acc parallel loop collapse(3)
    for (size_t i = 0; i < matrix.size(); ++i)
    {
        for (size_t j = 0; j < matrix[i].size(); ++j)
        {
            for (size_t k = 0; k < matrix[i][j].size(); ++k)
            {
                // Unique seed for each thread using system clock and thread ID
                unsigned int seed = static_cast<unsigned int>(time(nullptr) + i * 10000 + j * 100 + k);
                std::mt19937 gen(seed);
                std::uniform_int_distribution<> dis(0, maxMaterial - 1);

                matrix[i][j][k] = dis(gen);
            }
        }
    }
}

// Function to print a 3D matrix
void printMatrix3D(const vector<vector<vector<int>>> &matrix)
{
    for (size_t i = 0; i < matrix.size(); ++i)
    {
        cout << "Layer " << i << ":\n";
        for (size_t j = 0; j < matrix[i].size(); ++j)
        {
            for (size_t k = 0; k < matrix[i][j].size(); ++k)
            {
                cout << matrix[i][j][k] << " ";
            }
            cout << "\n";
        }
        cout << "\n";
    }
}

// Calculate Hamming error between 3D matrices
int calculateHammingError3D(const vector<vector<vector<int>>> &desired, const vector<vector<vector<int>>> &achieved)
{
    int error = 0;

#pragma acc parallel loop collapse(3) reduction(+ : error)
    for (size_t i = 0; i < desired.size(); ++i)
    {
        for (size_t j = 0; j < desired[i].size(); ++j)
        {
            for (size_t k = 0; k < desired[i][j].size(); ++k)
            {
                if (desired[i][j][k] != achieved[i][j][k])
                {
                    ++error;
                }
            }
        }
    }

    return error;
}

// Ant Colony Optimization for 3D Topologies
void runAntColony3D(const Topology3D &desired)
{
    const int maxCycles = 150;
    const int numAnts = 80;
    const double evaporationRate = 0.8;
    const double pheromoneBoost = 5.0;
    int bestError = INT_MAX;
    int currentCycle = 0;

    // Initialize matrices and pheromones
    Topology3D achieved = desired;
    initializeRandomMatrix3D(achieved.matrix, desired.n);

    // Print the randomly initialized matrix
    cout << "Randomly Initialized Matrix:\n";
    printMatrix3D(achieved.matrix);

    vector<vector<vector<double>>> pheromones(
        desired.nl,
        vector<vector<double>>(desired.nc, vector<double>(desired.p, 1.0)));

    // Prepare output file
    ofstream file("results_3D_OpenAcc.csv");
    file << "Cycle,Error\n";

#pragma acc data copy(achieved.matrix, pheromones)
    {
        while (currentCycle < maxCycles && bestError > 0)
        {
            vector<vector<vector<int>>> tabu(numAnts,
                                             vector<vector<int>>(desired.nl, vector<int>(desired.nc * desired.p)));

// Solution construction by ants
#pragma acc parallel loop collapse(4) present(pheromones, achieved)
            for (int k = 0; k < numAnts; ++k)
            {
                for (size_t i = 0; i < desired.nl; ++i)
                {
                    for (size_t j = 0; j < desired.nc; ++j)
                    {
                        for (size_t z = 0; z < desired.p; ++z)
                        {
                            double prob = pheromones[i][j][z] / (1.0 + pheromones[i][j][z]);
                            achieved.matrix[i][j][z] = (rand() % 100 < prob * 100) ? desired.matrix[i][j][z] : rand() % desired.n;
                        }
                    }
                }
            }

            // Evaluate error
            int error = calculateHammingError3D(desired.matrix, achieved.matrix);
            if (error < bestError)
            {
                bestError = error;
            }

// Update pheromones
#pragma acc parallel loop collapse(3) present(pheromones, achieved)
            for (size_t i = 0; i < pheromones.size(); ++i)
            {
                for (size_t j = 0; j < pheromones[i].size(); ++j)
                {
                    for (size_t z = 0; z < pheromones[i][j].size(); ++z)
                    {
                        pheromones[i][j][z] *= evaporationRate;
                        if (achieved.matrix[i][j][z] == desired.matrix[i][j][z])
                        {
                            pheromones[i][j][z] += pheromoneBoost / (1.0 + bestError);
                        }
                    }
                }
            }

            // Log progress to CSV
            file << currentCycle << "," << bestError << "\n";

            // Progress output
            cout << "Cycle: " << currentCycle << ", Error: " << bestError << endl;
            ++currentCycle;
        }
    }

    file.close();
    cout << "Optimization completed in " << currentCycle << " cycles with error " << bestError << ".\n";
}

int main()
{
    try
    {
        cout << "Enter the topology ID ('alvo_3n_3D_1', 'alvo_3n_3D_2'): ";
        string id;
        cin >> id;
        Topology3D topo = getTopology3D(id);

        // Print the initial topology matrix
        cout << "Initial Topology Matrix:\n";
        printMatrix3D(topo.matrix);

        runAntColony3D(topo);
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }

    return 0;
}