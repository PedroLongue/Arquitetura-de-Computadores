#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <random>
#include <climits>
#include <fstream>
#include <omp.h>
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
    else if (id == "alvo_I2_complex")
    {
        return {
            {{{0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0},
              {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0},
              {0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0},
              {0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0},
              {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0},
              {1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1},
              {1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1},
              {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0},
              {0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0},
              {0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0},
              {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0},
              {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0}},
             {{0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0},
              {0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0},
              {1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0},
              {1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0},
              {1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0},
              {1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0},
              {1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0},
              {1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0},
              {1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0},
              {0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0},
              {0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0},
              {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0}}},
            2,
            12,
            12,
            2};
    }
    else
    {
        throw invalid_argument("Topology ID not found: " + id);
    }
}

// Initialize matrix with random values using OpenMP
void initializeRandomMatrix3D(vector<vector<vector<int>>> &matrix, int maxMaterial)
{
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(0, maxMaterial - 1);

#pragma omp parallel for collapse(3)
    for (size_t i = 0; i < matrix.size(); ++i)
    {
        for (size_t j = 0; j < matrix[i].size(); ++j)
        {
            for (size_t k = 0; k < matrix[i][j].size(); ++k)
            {
                matrix[i][j][k] = dis(gen);
            }
        }
    }
}

// Calculate Hamming error between 3D matrices
int calculateHammingError3D(const vector<vector<vector<int>>> &desired, const vector<vector<vector<int>>> &achieved)
{
    int error = 0;

#pragma omp parallel for collapse(3) reduction(+ : error)
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
    vector<vector<vector<double>>> pheromones(
        desired.nl,
        vector<vector<double>>(desired.nc, vector<double>(desired.p, 1.0)));

    // Prepare output files
    ofstream file("results_3D_OpenMP.csv");
    file << "Cycle,Error\n";

    ofstream fileTimeError("time_error_3D_OpenMP.csv");
    fileTimeError << "Time(ms),Error\n";

    double totalExecutionTime = 0.0;

    while (currentCycle < maxCycles && bestError > 0)
    {
        auto start = chrono::high_resolution_clock::now();

        vector<vector<vector<int>>> tabu(numAnts,
                                         vector<vector<int>>(desired.nl, vector<int>(desired.nc * desired.p)));

// Solution construction by ants
#pragma omp parallel for collapse(4)
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
#pragma omp parallel for collapse(3)
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

        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> execTime = end - start;
        totalExecutionTime += execTime.count();

        // Log to both CSVs
        file << currentCycle << "," << bestError << "\n";
        fileTimeError << totalExecutionTime << "," << bestError << "\n";

        // Progress output
        cout << "Cycle: " << currentCycle << ", Error: " << bestError << ", Execution Time: " << execTime.count() << " ms\n";
        ++currentCycle;
    }

    file.close();
    fileTimeError.close();
    cout << "Optimization completed in " << currentCycle << " cycles with error " << bestError << ".\n";
}

int main()
{
    try
    {
        cout << "Enter the topology ID ('alvo_3n_3D_1', 'alvo_3n_3D_2', 'alvo_I2_complex'): ";
        string id;
        cin >> id;
        Topology3D topo = getTopology3D(id);
        runAntColony3D(topo);
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }

    return 0;
}