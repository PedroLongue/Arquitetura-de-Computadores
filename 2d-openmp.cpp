#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <map>
#include <stdexcept>
#include <omp.h> // Biblioteca para programação paralela com OpenMP

using namespace std;

// Estrutura para representar a topologia
struct Topology
{
    vector<vector<int>> matrix; // Matriz representando a topologia
    int n; // Número de materiais na topologia
};

// Função para obter uma topologia a partir de um ID
Topology getTopology(const string &id)
{
    // Mapeamento de IDs de topologia para suas respectivas configurações
    map<string, Topology> topologies = {
        {"alvo_I", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_U", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_G", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 0, 0}, {0, 1, 0, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_dama", {{{0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}}, 2}},
        {"alvo_3n_2D_1", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}},
        {"alvo_3n_2D_2", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 1, 2, 2, 2, 1, 0}, {1, 1, 2, 2, 2, 1, 1}, {0, 1, 2, 2, 2, 1, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}}
    };

    // Busca a topologia correspondente ao ID
    auto it = topologies.find(id);
    if (it == topologies.end())
    {
        throw invalid_argument("Topology ID not found: " + id); // Erro caso o ID não seja encontrado
    }
    return it->second;
}

// Calcula o erro de Hamming entre duas matrizes de topologia
int calculateHammingError(const vector<vector<int>> &topo1, const vector<vector<int>> &topo2)
{
    int error = 0;
    for (size_t i = 0; i < topo1.size(); i++)
    {
        for (size_t j = 0; j < topo1[i].size(); j++)
        {
            if (topo1[i][j] != topo2[i][j])
            {
                error++; // Incrementa o erro se os elementos forem diferentes
            }
        }
    }
    return error;
}

// Salva os resultados em um arquivo
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

// Executa a simulação da colônia de formigas
void runAntColony(const Topology &desired)
{
    const int maxCycles = 500; // Número máximo de ciclos
    int currentCycle = 0; // Contador de ciclos
    Topology achieved = desired; // Inicializa a topologia alcançada como a desejada

    srand(time(nullptr)); // Inicializa a semente para números aleatórios

#pragma omp parallel shared(currentCycle, achieved, desired)
    {
        bool done = false; // Indica se a otimização foi concluída
#pragma omp for
        for (int i = 0; i < maxCycles && !done; ++i)
        {
            int hammingError = calculateHammingError(desired.matrix, achieved.matrix);

#pragma omp critical
            {
                if (hammingError > 0)
                {
                    // Modifica aleatoriamente a topologia alcançada
                    int x = rand() % achieved.matrix.size();
                    int y = rand() % achieved.matrix[0].size();
                    achieved.matrix[x][y] ^= 1; // Alterna entre 0 e 1
                }
                else
                {
                    done = true; // Encerra se não houver erro
                }
            }
#pragma omp atomic
            currentCycle++; // Incrementa o contador de ciclos
        }
    }

    int finalHammingError = calculateHammingError(desired.matrix, achieved.matrix);
    saveResults(desired, achieved, finalHammingError, currentCycle); // Salva os resultados
}

int main()
{
    try
    {
        cout << "Enter the topology ID (e.g., 'alvo_I', 'alvo_U'): ";
        string id;
        cin >> id;
        Topology desired = getTopology(id); // Obtém a topologia desejada
        runAntColony(desired); // Executa a simulação
        cout << "Optimization completed and results saved." << endl;
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl;
        return 1; // Retorna erro
    }
    return 0; // Indica sucesso
}
