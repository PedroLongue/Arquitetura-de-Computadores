import numpy as np import cupy as cp import matplotlib.pyplot as plt

    def initialize_pheromones(size, n) : ""
                                         "Inicializa a matriz de feromônios."
                                         "" return cp.ones((size, n)) / n

                                                           def construct_solutions(tabu, tau, nlA, ncA, pA, n) : ""
                                                                                                                 "Construção das soluções pelas formigas."
                                                                                                                 "" num_ants = tabu.shape[0]

                                                                                   for ant in range(num_ants) : for x in range(nlA) : for y in range(ncA) : for z in range(pA) :index = x * ncA * pA + y * pA + z prob = tau[index]

#Normaliza probabilidades
                                                                                                                                                                                                                             prob_sum = cp.sum(prob) if prob_sum> 0 :prob /= prob_sum else :prob = cp.ones(n) / n

#Escolha do material
                                                                                                                                                                                                                                                                                                           choice = cp.random.choice(n, p = cp.asnumpy(prob)) tabu[ant, x, y, z] = choice

                                                                                                                                                                                                                                                                                                                                                                   def update_pheromones(tau, tabu, fitness, nlA, ncA, pA, n) : ""
                                                                                                                                                                                                                                                                                                                                                                                                                                "Atualização dos feromônios."
                                                                                                                                                                                                                                                                                                                                                                                                                                "" tau *= 0.8 #Evaporação num_ants = tabu.shape[0]

                                                                                                                                                                                                                                                                                                                                                                                         for ant in range(num_ants) : for x in range(nlA) : for y in range(ncA) : for z in range(pA) :index = x * ncA * pA + y * pA + z material = tabu[ant, x, y, z] tau[index, material] += 1.0 / fitness[ant]

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          def evaluate_solutions(tabu, goal, nlA, ncA, pA) : ""
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             "Avaliação das soluções."
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             "" num_ants = tabu.shape[0] fitness = cp.zeros(num_ants)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          for ant in range(num_ants) :fitness[ant] = cp.sum(cp.abs(tabu[ant] - goal))

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                return fitness

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            def main() :nlA, ncA, pA = 7, 7, 1 #Dimensões do espaço de design n = 2 #Número de materiais possíveis num_ants = 50 max_cycles = 150

#Inicialização
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     size = nlA * ncA * pA tau = initialize_pheromones(size, n) tabu = cp.zeros((num_ants, nlA, ncA, pA), dtype = int) goal = cp.random.randint(0, n, size =(nlA, ncA, pA))

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          best_fitness = float("inf") best_solution = None

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                fitness_history =[]

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                for cycle in range(max_cycles) :
#Construção de soluções
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                construct_solutions(tabu, tau, nlA, ncA, pA, n)

#Avaliação
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        fitness = evaluate_solutions(tabu, goal, nlA, ncA, pA) min_fitness = cp.min(fitness) best_ant = cp.argmin(fitness)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        if min_fitness < best_fitness:
            best_fitness = min_fitness
            best_solution = tabu[best_ant]

        fitness_history.append(best_fitness)

#Atualização dos feromônios
        update_pheromones(tau, tabu, fitness, nlA, ncA, pA, n)

        print(f"Cycle {cycle}: Best Fitness = {best_fitness}")

        if best_fitness == 0:
            print(f"Converged at cycle {cycle}")
            break

#Visualização dos resultados
    plt.plot(fitness_history, label="Fitness over cycles")
    plt.xlabel("Cycles")
    plt.ylabel("Fitness")
    plt.title("ACO Optimization - Fitness Evolution")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
