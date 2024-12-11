#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <map>
#include <stdexcept>
#include <openacc.h> // Biblioteca para paralelismo

using namespace std;

// Estrutura para representar uma topologia
struct Topology {
    vector<vector<int>> matrix;
    int n;
};

// Função para obter uma topologia com base no identificador fornecido
Topology getTopology(const string &id) {
    // Mapeamento de identificadores de topologias para suas configurações
    map<string, Topology> topologies = {
        {"alvo_I", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_U", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_G", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 0, 0}, {0, 1, 0, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_dama", {{{0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}}, 2}},
        {"alvo_3n_2D_1", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}},
        {"alvo_3n_2D_2", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 1, 2, 2, 2, 1, 0}, {1, 1, 2, 2, 2, 1, 1}, {0, 1, 2, 2, 2, 1, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}}
    };

    // Busca o identificador no mapa
    auto it = topologies.find(id);
    if (it == topologies.end()) {
        throw invalid_argument("Topology ID not found: " + id); // Erro se o ID não for encontrado
    }
    return it->second; // Retorna a topologia correspondente
}

// Função para calcular o erro de Hamming entre duas matrizes
int calcHammingError(const vector<vector<int>> &desired, const vector<vector<int>> &achieved) {
    int error = 0;
    for (size_t i = 0; i < desired.size(); ++i) {
        for (size_t j = 0; j < desired[0].size(); ++j) {
            if (desired[i][j] != achieved[i][j]) {
                ++error;
            }
        }
    }
    return error;
}

// Função para executar o algoritmo de colônia de formigas
void runAntColony(Topology &topo, const Topology &desired) {
    int numAnts = 10; // Número de formigas
    int maxCycles = 100; // Número máximo de ciclos
    double evaporationRate = 0.5; // Taxa de evaporação do feromônio
    double pheromoneIntensity = 1.0; // Intensidade inicial do feromônio

    int rows = topo.matrix.size();
    int cols = topo.matrix[0].size();

    // Inicializa a matriz de feromônio
    vector<vector<double>> pheromone(rows, vector<double>(cols, 1.0));

    vector<vector<int>> bestSolution = topo.matrix;
    int bestError = calcHammingError(desired.matrix, topo.matrix);

    srand(time(0)); // Inicializa o gerador de números aleatórios

    #pragma acc data copy(pheromone, topo.matrix)
    for (int cycle = 0; cycle < maxCycles; ++cycle) {
        vector<vector<int>> currentSolution = topo.matrix;
        #pragma acc parallel loop collapse(2)
        for (int ant = 0; ant < numAnts; ++ant) {
            for (int i = 0; i < rows; ++i) {
                for (int j = 0; j < cols; ++j) {
                    // Decisão baseada em probabilidade
                    double random = (double)rand() / RAND_MAX;
                    if (random < pheromone[i][j]) {
                        currentSolution[i][j] = desired.matrix[i][j];
                    }
                }
            }
        }

        // Calcula o erro de Hamming para a solução atual
        int currentError = calcHammingError(desired.matrix, currentSolution);

        // Atualiza a melhor solução
        if (currentError < bestError) {
            bestError = currentError;
            bestSolution = currentSolution;
        }

        // Atualização do feromônio
        #pragma acc parallel loop collapse(2)
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                pheromone[i][j] *= (1.0 - evaporationRate); // Evaporação
                if (currentSolution[i][j] == desired.matrix[i][j]) {
                    pheromone[i][j] += pheromoneIntensity; // Reforço do feromônio
                }
            }
        }

        // Verifica se encontrou a solução desejada
        if (bestError == 0) {
            break;
        }

        cout << "Cycle: " << cycle + 1 << ", Best Error: " << bestError << endl;
    }

    // Atualiza a matriz alcançada com a melhor solução encontrada
    topo.matrix = bestSolution;
}

int main() {
    try {
        cout << "Enter the topology ID (e.g., 'alvo_I', 'alvo_U'): ";
        string id;
        cin >> id;
        Topology desired = getTopology(id);

        Topology initial = desired; // Pode ser ajustado para começar com uma matriz zerada
        for (auto &row : initial.matrix) {
            for (auto &val : row) {
                val = 0; // Inicializa com valores zerados
            }
        }

        runAntColony(initial, desired);

        cout << "Final Solution:" << endl;
        for (const auto &row : initial.matrix) {
            for (int val : row) {
                cout << val << " ";
            }
            cout << endl;
        }
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }

    return 0;
}
