#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <map>
#include <stdexcept>
#include <openacc.h> // Biblioteca para programação paralela com OpenACC

using namespace std;

// Estrutura para representar uma topologia
struct Topology
{
    vector<vector<int>> matrix; // Matriz representando a topologia
    int n; // Número de materiais na topologia
};

// Função para obter uma topologia com base no identificador fornecido
Topology getTopology(const string &id)
{
    // Mapeamento de identificadores de topologias para suas configurações
    map<string, Topology> topologies = {
        {"alvo_I", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_U", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_G", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 0, 0}, {0, 1, 0, 1, 1, 1, 0}, {0, 1, 0, 0, 0, 1, 0}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 2}},
        {"alvo_dama", {{{0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 0, 1, 0}}, 2}},
        {"alvo_3n_2D_1", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 0, 2, 2, 2, 0}, {0, 1, 1, 1, 0, 2, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}},
        {"alvo_3n_2D_2", {{{0, 0, 0, 0, 0, 0, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 1, 2, 2, 2, 1, 0}, {1, 1, 2, 2, 2, 1, 1}, {0, 1, 2, 2, 2, 1, 0}, {0, 1, 1, 0, 1, 1, 0}, {0, 0, 0, 0, 0, 0, 0}}, 3}}
        // Mais topologias podem ser adicionadas conforme necessário
    };

    // Busca o identificador no mapa
    auto it = topologies.find(id);
    if (it == topologies.end())
    {
        throw invalid_argument("Topology ID not found: " + id); // Erro se o ID não for encontrado
    }
    return it->second; // Retorna a topologia correspondente
}

// Função para salvar os resultados em um arquivo
void saveResults(const Topology &desired, const Topology &achieved, int error, int cycles)
{
    ofstream file("results.txt");
    file << "Desired Topology:\n";
    for (const auto &row : desired.matrix)
    {
        for (int val : row)
            file << val << " "; // Escreve os valores da matriz desejada
        file << "\n";
    }
    file << "\nAchieved Topology:\n";
    for (const auto &row : achieved.matrix)
    {
        for (int val : row)
            file << val << " "; // Escreve os valores da matriz alcançada
        file << "\n";
    }
    file << "\nHamming Error: " << error << "\n"; // Salva o erro de Hamming
    file << "Number of Cycles: " << cycles << "\n"; // Salva o número de ciclos
    file.close();
}

// Simula o algoritmo da colônia de formigas
void runAntColony(const Topology &topo)
{
    const int maxCycles = 500; // Número máximo de ciclos
    int currentCycle = 0; // Ciclo atual
    int hammingError = 10; // Erro inicial simulado

    // Copia as variáveis para a memória do dispositivo usando OpenACC
    #pragma acc data copy(currentCycle, hammingError)
    {
        #pragma acc kernels // Define a região de execução paralela
        {
            while (currentCycle < maxCycles && hammingError > 0)
            {
                hammingError--; // Simula a redução do erro
                currentCycle++; // Incrementa o número de ciclos
                if (hammingError == 0)
                { // Verifica se o erro é zero
                    break; // Encerra o loop
                }
            }
        }
    }

    // Salva os resultados após a simulação
    saveResults(topo, topo, hammingError, currentCycle);
}

// Função principal
int main()
{
    try
    {
        cout << "Enter the topology ID (e.g., 'alvo_I', 'alvo_U'): "; // Solicita o ID da topologia
        string id;
        cin >> id; // Lê o ID
        Topology topo = getTopology(id); // Obtém a topologia correspondente
        runAntColony(topo); // Executa a simulação
        cout << "Optimization completed and results saved." << endl; // Confirmação de sucesso
    }
    catch (const exception &e)
    {
        cerr << "Error: " << e.what() << endl; // Exibe mensagens de erro
        return 1; // Retorna código de erro
    }
    return 0; // Retorna sucesso
}
