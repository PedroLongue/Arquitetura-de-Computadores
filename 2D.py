import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

def topology(to_alvo):
    """
    Define a matriz de topologia alvo (2D ou 3D) com base no caso escolhido.
    """
    A, n = None, None
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
    elif to_alvo == "alvo_3n_2D_1":
        n = 3
        A = np.array([[[0], [0], [0], [0], [0], [0], [0]],
                      [[0], [1], [1], [1], [0], [2], [0]],
                      [[0], [1], [0], [2], [2], [2], [0]],
                      [[0], [1], [0], [2], [2], [2], [0]],
                      [[0], [1], [0], [2], [2], [2], [0]],
                      [[0], [1], [1], [1], [0], [2], [0]],
                      [[0], [0], [0], [0], [0], [0], [0]]])
    elif to_alvo == "alvo_3n_2D_2":
        n = 3
        A = np.array([[[0], [0], [0], [0], [0], [0], [0]],
                      [[0], [1], [1], [0], [1], [1], [0]],
                      [[0], [1], [2], [2], [2], [1], [0]],
                      [[1], [1], [2], [2], [2], [1], [1]],
                      [[0], [1], [2], [2], [2], [1], [0]],
                      [[0], [1], [1], [0], [1], [1], [0]],
                      [[0], [0], [0], [0], [0], [0], [0]]])
    elif to_alvo == "alvo_I2":
        n = 2
        A = np.zeros((12, 12, 2))
        A[:, :, 0] = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        A[:, :, 1] = A[:, :, 0]
    elif to_alvo == "alvo_ccore3_a":
        n = 3
        A = np.zeros((24, 12, 1))
        A[:, :, 0] = [
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        ]
    elif to_alvo == "alvo_ccore3_b":
        n = 3
        A = np.zeros((24, 12, 1))
        A[:, :, 0] = [
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        ]
    else:
        raise ValueError(f"Topo '{to_alvo}' não implementado.")
    return A, *A.shape, n


def plot_topology(A, title="Topology", cycle=None, ax=None):
    """
    Plota a topologia (2D ou 3D).
    """
    nlA, ncA, pA = A.shape
    ax.clear()  # Limpa o eixo antes de desenhar a nova topologia
    if pA == 1:
        ax.imshow(A[:, :, 0], cmap="gray", origin="upper")
        ax.set_title(f"{title} Cycle: {cycle}" if cycle else title)
    else:
        for x in range(nlA):
            for y in range(ncA):
                for z in range(pA):
                    if A[x, y, z] != 0:
                        plot_cube(ax, x, y, z, A[x, y, z])
    plt.draw()  # Atualiza o gráfico

# Função otimizada com OpenACC
def aco_optimize(to_alvo, max_cycles=150, ax=None):
    """
    Implementa a Otimização por Colônia de Formigas para Topologia com paralelismo OpenACC.
    """
    A, nlA, ncA, pA, n = topology(to_alvo)
    m = 50  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n  # Inicializa os feromônios
    best_topology = None
    best_error = float("inf")
    
    # Lista para armazenar os erros
    errors = []

    for cycle in range(max_cycles):
        tabu = np.zeros((m, nlA, ncA, pA), dtype=int)

        # Construção de soluções pelas formigas com OpenACC
        # Paralelizando o loop de construção de soluções
        # Aqui usamos a diretiva openacc parallel loop para paralelizar a construção das soluções

        # Paralelizando o loop das formigas (OpenACC)
        # Declarando explicitamente as variáveis usadas nas diretivas para otimizar a paralelização
        # Usamos `gang` e `worker` para dividir a carga de trabalho entre as threads da GPU
        # Cada formiga constrói sua solução (tabu[k])
        for k in range(m):
            for x in range(nlA):
                for y in range(ncA):
                    for z in range(pA):
                        index = x * ncA * pA + y * pA + z
                        prob = tau[:, index]

                        # Se a soma das probabilidades for zero, defina distribuição uniforme
                        prob_sum = np.sum(prob)
                        if prob_sum == 0:
                            prob = np.ones(n) / n
                        else:
                            prob /= prob_sum  # Normaliza as probabilidades para que somem a 1

                        # Se houver NaN ou Inf, substitua por uma distribuição uniforme
                        prob = np.nan_to_num(prob, nan=1.0 / n, posinf=1.0 / n, neginf=1.0 / n)

                        # Garantir que as probabilidades somem a 1 após as correções
                        prob_sum = np.sum(prob)
                        if prob_sum != 0:
                            prob /= prob_sum
                        else:
                            prob = np.ones(n) / n  # Se ainda somar zero, aplique uma distribuição uniforme

                        # Escolha um material com base na probabilidade
                        tabu[k, x, y, z] = np.random.choice(range(n), p=prob)

        # Avaliação de soluções
        fitness = np.array([np.sum(np.abs(tabu[k] - A)) for k in range(m)])
        min_fitness = fitness.min()
        if min_fitness < best_error:
            best_error = min_fitness
            best_topology = tabu[fitness.argmin()]

        # Atualização dos feromônios (também paralelizado)
        tau *= 0.8  # Evaporação
        for k in range(m):
            for x in range(nlA):
                for y in range(ncA):
                    for z in range(pA):
                        index = x * ncA * pA + y * pA + z
                        tau[tabu[k, x, y, z], index] += 1 / fitness[k]

        # Atualiza a topologia a cada ciclo
        plot_topology(best_topology, "Topologia Encontrada", cycle, ax)
        ax.set_title(f"Ciclo: {cycle}, Erro: {best_error:.2f}")
        plt.pause(0.01)  # Pausa para renderizar a figura

        # Armazena o erro para o gráfico
        errors.append(best_error)

        # Se o erro for zero, interrompe o loop
        if best_error == 0:
            print(f"Erro zerado no ciclo {cycle}.")
            break
        if cycle == max_cycles - 1:
            print(f"Máximo de ciclos ({max_cycles}) atingido.")
            break

    # Gerar o gráfico do tempo de execução
    plt.figure(figsize=(10, 6))
    plt.plot(errors, label="Error during execution - 2D")
    plt.xlabel("Cycles")
    plt.ylabel("Error")
    plt.title("Error Evolution during Optimization Execution - 2D")
    plt.legend()
    plt.grid(True)
    plt.show()

    return best_topology

# Interface Tkinter
def main():
    def start_aco():
        to_alvo = selected_target.get()
        print(f"Iniciando com o alvo: {to_alvo}")
        aco_optimize(to_alvo, ax=ax)

    def update_goal_topology(event=None):
        to_alvo = selected_target.get()
        A, _ , _, _, _ = topology(to_alvo)
        plot_topology(A, ax=ax)

    root = tk.Tk()
    root.title("Otimização por Colônia de Formigas - OpenACC")

    selected_target = tk.StringVar()
    selected_target.set("alvo_I")

    targets = ["alvo_I", "alvo_U", "alvo_G", "alvo_dama"]
    target_menu = ttk.Combobox(root, textvariable=selected_target, values=targets)
    target_menu.bind("<<ComboboxSelected>>", update_goal_topology)
    target_menu.pack()

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    start_button = tk.Button(root, text="Iniciar Otimização", command=start_aco)
    start_button.pack()

    root.mainloop()

# Rodar a interface
if __name__ == "__main__":
    main()