import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

def topology(to_alvo):
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
    ax.clear()
    ax.imshow(A[:, :, 0], cmap="gray", origin="upper")
    ax.set_title(f"{title} (Cycle: {cycle})" if cycle else title)
    ax.axis("off")
    plt.draw()

def initialize_random_topology(shape, n):
    return np.random.randint(0, n, size=shape)

def aco_optimize(to_alvo, max_cycles=150, ax_goal=None, ax_process=None):
    A, nlA, ncA, pA, n = topology(to_alvo)
    m = 80  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n

    best_topology = initialize_random_topology(A.shape, n)
    best_error = float("inf")

    plot_topology(ax_goal, A, title="Goal Topology")

    errors = []
    times = []  # Lista para armazenar tempos de execução acumulados
    start_time = time.time()

    for cycle in range(max_cycles):
        tabu = np.zeros((m, nlA, ncA, pA), dtype=int)
        
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
                        prob = np.clip(prob, 0, 1)
                        prob /= prob.sum()
                        tabu[k, x, y, z] = np.random.choice(range(n), p=prob)

        fitness = np.array([np.sum(np.abs(tabu[k] - A)) for k in range(m)])
        min_fitness = fitness.min()
        if min_fitness < best_error:
            best_error = min_fitness
            best_topology = tabu[fitness.argmin()]

        tau *= 0.8
        for k in range(m):
            for x in range(nlA):
                for y in range(ncA):
                    for z in range(pA):
                        index = x * ncA * pA + y * pA + z
                        if fitness[k] > 0:  # Verificação para evitar divisão por zero
                            tau[tabu[k, x, y, z], index] += 1 / fitness[k]

        plot_topology(ax_process, best_topology, title="Processing Topology", cycle=cycle)
        plt.pause(0.1)

        errors.append(best_error)
        times.append(time.time() - start_time)

        if best_error == 0:
            print(f"Convergiu no ciclo {cycle}")
            break

    # Plota Ciclo x Erro
    plt.figure(figsize=(10, 5))
    plt.plot(errors, label="Error during execution - Cycle x Error")
    plt.xlabel("Cycles")
    plt.ylabel("Error")
    plt.title("Error Evolution - Cycle x Error")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Plota Tempo x Erro
    plt.figure(figsize=(10, 5))
    plt.plot(times, errors, label="Error during execution - Time x Error", color="orange")
    plt.xlabel("Time (s)")
    plt.ylabel("Error")
    plt.title("Error Evolution - Time x Error")
    plt.grid(True)
    plt.legend()
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
