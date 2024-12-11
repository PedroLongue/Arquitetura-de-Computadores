import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def topology(to_alvo):
    """
    Define a matriz de topologia alvo (2D ou 3D) com base no caso escolhido.
    """
    if to_alvo == "alvo_I":
        n = 2
        A = np.array([[[0], [0], [0], [0], [0], [0], [0]],
                      [[0], [1], [1], [1], [1], [1], [0]],
                      [[0], [0], [0], [1], [0], [0], [0]],
                      [[0], [0], [0], [1], [0], [0], [0]],
                      [[0], [0], [0], [1], [0], [0], [0]],
                      [[0], [1], [1], [1], [1], [1], [0]],
                      [[0], [0], [0], [0], [0], [0], [0]]])
    elif to_alvo == "alvo_U":
        n = 2
        A = np.array([[[0], [0], [0], [0], [0], [0], [0]],
                      [[0], [1], [0], [0], [0], [1], [0]],
                      [[0], [1], [0], [0], [0], [1], [0]],
                      [[0], [1], [0], [0], [0], [1], [0]],
                      [[0], [1], [0], [0], [0], [1], [0]],
                      [[0], [1], [1], [1], [1], [1], [0]],
                      [[0], [0], [0], [0], [0], [0], [0]]])
    elif to_alvo == "alvo_G":
        n = 2
        A = np.array([[[0], [0], [0], [0], [0], [0], [0]],
                      [[0], [1], [1], [1], [1], [1], [0]],
                      [[0], [1], [0], [0], [0], [0], [0]],
                      [[0], [1], [0], [1], [1], [1], [0]],
                      [[0], [1], [0], [0], [0], [1], [0]],
                      [[0], [1], [1], [1], [1], [1], [0]],
                      [[0], [0], [0], [0], [0], [0], [0]]])
    elif to_alvo == "alvo_dama":
        n = 2
        A = np.array([[[0], [1], [0], [1], [0], [1], [0]],
                      [[1], [0], [1], [0], [1], [0], [1]],
                      [[0], [1], [0], [1], [0], [1], [0]],
                      [[1], [0], [1], [0], [1], [0], [1]],
                      [[0], [1], [0], [1], [0], [1], [0]],
                      [[1], [0], [1], [0], [1], [0], [1]],
                      [[0], [1], [0], [1], [0], [1], [0]]])
    else:
        raise ValueError(f"Topo '{to_alvo}' não implementado.")
    return A, *A.shape, n

def plot_topology(ax, A, title="Topology", cycle=None):
    """
    Plota a topologia 2D.
    """
    ax.clear()
    ax.imshow(A[:, :, 0], cmap="gray", origin="upper")
    ax.set_title(f"{title} (Cycle: {cycle})" if cycle else title)
    ax.axis("off")  # Remove os eixos para um visual mais limpo
    plt.draw()

def initialize_random_topology(shape, n):
    """
    Inicializa uma matriz de topologia aleatória.
    shape: Forma da matriz (dimensões)
    n: Número de materiais disponíveis
    """
    return np.random.randint(0, n, size=shape)


def aco_optimize(to_alvo, max_cycles=150, ax_goal=None, ax_process=None):
    """
    Implementa a Otimização por Colônia de Formigas para Topologia.
    """
    A, nlA, ncA, pA, n = topology(to_alvo)
    m = 80  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n  # Inicializa os feromônios

    # Inicializa a topologia de forma aleatória
    best_topology = initialize_random_topology(A.shape, n)
    best_error = float("inf")

    # Exibe a topologia alvo no gráfico
    plot_topology(ax_goal, A, title="Goal Topology")

    errors = []

    for cycle in range(max_cycles):
        tabu = np.zeros((m, nlA, ncA, pA), dtype=int)
        
        # Construção de soluções pelas formigas
        for k in range(m):
            for x in range(nlA):
                for y in range(ncA):
                    for z in range(pA):
                        index = x * ncA * pA + y * pA + z
                        prob = tau[:, index]

                        # Normalização das probabilidades
                        prob_sum = np.sum(prob)
                        if prob_sum > 0:
                            prob /= prob_sum
                        else:
                            prob = np.ones(n) / n  # Distribuição uniforme se prob_sum for 0

                        # Garantir que as probabilidades somem exatamente 1
                        prob = np.clip(prob, 0, 1)
                        prob /= prob.sum()

                        # Escolher o material com base na probabilidade
                        tabu[k, x, y, z] = np.random.choice(range(n), p=prob)

        # Avaliação das soluções
        fitness = np.array([np.sum(np.abs(tabu[k] - A)) for k in range(m)])
        min_fitness = fitness.min()
        if min_fitness < best_error:
            best_error = min_fitness
            best_topology = tabu[fitness.argmin()]

        # Atualização dos feromônios
        tau *= 0.8  # Evaporação
        for k in range(m):
            for x in range(nlA):
                for y in range(ncA):
                    for z in range(pA):
                        index = x * ncA * pA + y * pA + z
                        tau[tabu[k, x, y, z], index] += 1 / fitness[k]

        # Atualiza o gráfico da topologia em processo
        plot_topology(ax_process, best_topology, title="Processing Topology", cycle=cycle)
        plt.pause(0.1)

        errors.append(best_error)

        # Verifica convergência
        if best_error == 0:
            print(f"Convergiu no ciclo {cycle}")
            break

    plt.figure(figsize=(10, 6))
    plt.plot(errors, label="Error during execution - 2D")
    plt.xlabel("Cycles")
    plt.ylabel("Error")
    plt.title("Error Evolution during Optimization Execution - 2D")
    plt.xlim(0, 150)  # Define os limites do eixo X
    plt.ylim(0, 30)   # Define os limites do eixo Y
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    def start_aco():
        to_alvo = selected_target.get()
        aco_optimize(to_alvo, ax_goal=ax_goal, ax_process=ax_process)

    root = tk.Tk()
    root.title("ACO Optimization - 2D")

    selected_target = tk.StringVar()
    selected_target.set("alvo_I")

    targets = ["alvo_I", "alvo_U", "alvo_G", "alvo_dama"]
    target_menu = ttk.Combobox(root, textvariable=selected_target, values=targets)
    target_menu.pack()

    start_button = tk.Button(root, text="Start Optimization", command=start_aco)
    start_button.pack()

    fig, (ax_goal, ax_process) = plt.subplots(1, 2, figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()

if __name__ == "__main__":
    main()
