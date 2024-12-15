import numpy as np
import time
import csv

def topology(to_alvo):
    if to_alvo == 'alvo_3n_3D_1':
        n = 3
        A = np.array([
            [
                [0, 0, 0], 
                [1, 1, 1], 
                [2, 2, 2]
            ],
                    
            [
                [0, 0, 0], 
                [1, 1, 1], 
                [2, 2, 2]
            ],
                    
            [
                [0, 0, 0], 
                [1, 1, 1], 
                [2, 2, 2]
            ]
        ])
    elif to_alvo == 'alvo_3n_3D_2':
        n = 3
        A = np.array([
            [
                [2, 2, 1, 1],
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ],
            [
                [2, 2, 1, 1],
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ],
            [
                [2, 2, 1, 1],
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ]
        ])
    else:
        raise ValueError("The topology specified does not exist!")

    nlA, ncA, pA = A.shape if A.ndim == 3 else (*A.shape, 1)
    return A, nlA, ncA, pA, n

def aco_optimize_3d(to_alvo, max_cycles=150, output_cycle_csv="results_3D_normal.csv", output_time_csv="time_error_3D_normal.csv"):
    """
    Implementa a Otimização por Colônia de Formigas para Topologia 3D.
    """
    A, nlA, ncA, pA, n = topology(to_alvo)
    m = 80  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n
    best_topology = None
    best_error = float("inf")
    errors = []
    times = []

    start_time = time.time()

    # Cria arquivos CSV
    with open(output_cycle_csv, mode='w', newline='') as cycle_csv, open(output_time_csv, mode='w', newline='') as time_csv:
        cycle_writer = csv.writer(cycle_csv)
        time_writer = csv.writer(time_csv)

        # Escreve cabeçalhos
        cycle_writer.writerow(["Cycle", "Error"])
        time_writer.writerow(["Time(ms)", "Error"])

        for cycle in range(max_cycles):
            tabu = np.zeros((m, nlA, ncA, pA), dtype=int)

            # Construção de soluções pelas formigas
            for k in range(m):
                for x in range(nlA):
                    for y in range(ncA):
                        for z in range(pA):
                            index = x * ncA * pA + y * pA + z
                            prob = tau[:, index]
                            prob_sum = np.sum(prob)
                            if prob_sum > 0:
                                prob /= prob_sum
                            else:
                                prob = np.ones(n) / n

                            prob = np.nan_to_num(prob, nan=1.0/n)
                            prob /= np.sum(prob)  # Garante que soma 1

                            tabu[k, x, y, z] = np.random.choice(range(n), p=prob)

            # Avaliação das soluções
            fitness = np.array([np.sum(np.abs(tabu[k] - A)) for k in range(m)])
            min_fitness = fitness.min()
            if min_fitness < best_error:
                best_error = min_fitness
                best_topology = tabu[fitness.argmin()]

            # Atualização dos feromônios
            tau *= 0.8
            for k in range(m):
                for x in range(nlA):
                    for y in range(ncA):
                        for z in range(pA):
                            index = x * ncA * pA + y * pA + z
                            if fitness[k] > 0:  # Evita divisão por zero
                                tau[tabu[k, x, y, z], index] += 1 / fitness[k]

            # Registra dados no CSV
            elapsed_time = (time.time() - start_time) * 1000  # Tempo em ms
            errors.append(best_error)
            times.append(elapsed_time)

            cycle_writer.writerow([cycle, best_error])
            time_writer.writerow([elapsed_time, best_error])

            # Verifica se convergiu
            if best_error == 0:
                print(f"Convergiu no ciclo {cycle}")
                break

if __name__ == "__main__":
    # Execute a otimização para uma topologia específica
    aco_optimize_3d("alvo_3n_3D_1")
