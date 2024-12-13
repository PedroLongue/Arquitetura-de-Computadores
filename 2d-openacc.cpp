#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <map>
#include <random>
#include <climits>
#include <openacc.h>

using namespace std;

struct Topology
{
    vector<vector<int>> matrix;
    int n; // Number of materials
};

// Função para obter a topologia desejada
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

// Inicializa a matriz de forma aleatória usando paralelização
void initializeRandomMatrix(vector<vector<int>> &matrix, int maxMaterial)
{
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(0, maxMaterial - 1);

    #pragma acc parallel loop collapse(2) present(matrix)
    for (size_t i = 0; i < matrix.size(); ++i)
    {
        for (size_t j = 0; j < matrix[i].size(); ++j)
        {
            matrix[i][j] = dis(gen);
        }
    }
}

// Calcula o erro Hamming de forma paralela
int calculateHammingError(const vector<vector<int>> &desired, const vector<vector<int>> &achieved)
{
    int error = 0;
    #pragma acc parallel loop collapse(2) reduction(+:error)
    for (size_t i = 0; i < desired.size(); ++i)
    {
        for (size_t j = 0; j < desired[i].size(); ++j)
        {
            if (desired[i][j] != achieved[i][j])
            {
                ++error;
            }
        }
    }
    return error;
}

// Função principal de otimização
void runAntColony(const Topology &desired)
{
    const int maxCycles = 150;
    const int numAnts = 80;
    const double evaporationRate = 0.8;
    const double pheromoneBoost = 5.0; // Ajuste para reforçar boas soluções
    int currentCycle = 0;
    int bestError = INT_MAX;

    // Inicializa a matriz alcançada com valores aleatórios
    Topology achieved = desired;
    initializeRandomMatrix(achieved.matrix, desired.n);

    // Inicializa os feromônios
    vector<vector<double>> pheromones(desired.matrix.size(), vector<double>(desired.matrix[0].size(), 1.0));

    // Prepara o arquivo de saída
    ofstream file("results_2D_OpenAcc.csv");
    file << "Cycle, Error\n";

    #pragma acc data copy(achieved.matrix, pheromones)
    {
        while (currentCycle < maxCycles && bestError > 0)
        {
            // Construção de soluções pelas formigas
            #pragma acc parallel loop collapse(3) present(pheromones, achieved)
            for (int k = 0; k < numAnts; ++k)
            {
                for (size_t i = 0; i < achieved.matrix.size(); ++i)
                {
                    for (size_t j = 0; j < achieved.matrix[i].size(); ++j)
                    {
                        double prob = pheromones[i][j] / (1.0 + pheromones[i][j]);
                        achieved.matrix[i][j] = (rand() % 100 < prob * 100) ? desired.matrix[i][j] : rand() % desired.n;
                    }
                }
            }

            // Avalia o erro da matriz alcançada
            int error = calculateHammingError(desired.matrix, achieved.matrix);
            if (error < bestError)
            {
                bestError = error;
            }

            // Atualiza os feromônios
            #pragma acc parallel loop collapse(2) present(pheromones, achieved)
            for (size_t i = 0; i < pheromones.size(); ++i)
            {
                for (size_t j = 0; j < pheromones[i].size(); ++j)
                {
                    pheromones[i][j] *= evaporationRate;
                    if (achieved.matrix[i][j] == desired.matrix[i][j])
                    {
                        pheromones[i][j] += pheromoneBoost / (1.0 + bestError);
                    }
                }
            }

            // Salva o progresso no arquivo
            file << currentCycle << ", " << bestError << "\n";

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
        cout << "Enter the topology ID ('alvo_I', 'alvo_U', 'alvo_G', 'alvo_dama', 'alvo_3n_2D_1', 'alvo_3n_2D_2'): ";
        string id;
        cin >> id;
        Topology topo = getTopology(id);
        runAntColony(topo);
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    return 0;
}
