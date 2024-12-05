import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tkinter as tk

def topology_3d(to_alvo):
    """
    Define a matriz de topologia 3D alvo com base no caso escolhido.
    """
    A, n = None, None
    if to_alvo == "alvo_3n_3D_1":
        n = 3
        A = np.zeros((3, 3, 3))  # Criando um cubo 3x3x3

        # Definindo as cores nas camadas (como solicitado)
        # Primeira camada (z=0) - Azul
        A[:, :, 0] = 2  # Azul

        # Segunda camada (z=1) - Amarelo
        A[:, :, 1] = 1  # Amarelo

        # Terceira camada (z=2) - Verde (Agora usando 3 para o verde)
        A[:, :, 2] = 3  # Verde

    elif to_alvo == "alvo_3n_3D_2":
        n = 3
        A = np.zeros((4, 4, 3))
        A[:, :, 0] = np.array([[2, 2, 1, 1], [2, 0, 0, 1], [2, 0, 0, 1], [2, 2, 1, 1]])
        A[:, :, 1] = np.array([[2, 2, 1, 1], [2, 0, 0, 1], [2, 0, 0, 1], [2, 2, 1, 1]])
        A[:, :, 2] = np.array([[2, 2, 1, 1], [2, 0, 0, 1], [2, 0, 0, 1], [2, 2, 1, 1]])
    else:
        raise ValueError(f"Topo '{to_alvo}' não implementado.")
    
    return A, *A.shape, n

def plot_topology_3d(A, title="Topology", cycle=None, ax=None):
    """
    Plota a topologia 3D.
    """
    nlA, ncA, pA = A.shape
    ax.clear()  # Limpa o eixo antes de desenhar a nova topologia
    
    # Mapeamento de cores para valores
    color_map = {1: 'yellow', 2: 'blue', 3: 'green'}  # Ajuste aqui para a cor verde (3)
    
    for x in range(nlA):
        for y in range(ncA):
            for z in range(pA):
                if A[x, y, z] != 0:  # Só desenha onde a célula tem valor diferente de 0
                    plot_cube(ax, x, y, z, color_map[A[x, y, z]])  # Usa o valor para a cor

    ax.set_title(f"{title} Cycle: {cycle}" if cycle else title)
    ax.set_xlim(0, nlA)  # Ajuste do limite de x
    ax.set_ylim(0, ncA)  # Ajuste do limite de y
    ax.set_zlim(0, pA)  # Ajuste do limite de z
    plt.draw()  # Atualiza o gráfico

def plot_cube(ax, x, y, z, color):
    """
    Plota um cubo no espaço 3D com a cor especificada.
    """
    # As coordenadas dos vértices de um cubo
    vertices = [
        [x - 0.5, y - 0.5, z - 0.5],
        [x + 0.5, y - 0.5, z - 0.5],
        [x + 0.5, y + 0.5, z - 0.5],
        [x - 0.5, y + 0.5, z - 0.5],
        [x - 0.5, y - 0.5, z + 0.5],
        [x + 0.5, y - 0.5, z + 0.5],
        [x + 0.5, y + 0.5, z + 0.5],
        [x - 0.5, y + 0.5, z + 0.5],
    ]
    faces = [
        [vertices[j] for j in [0, 1, 2, 3]],  # Parte inferior
        [vertices[j] for j in [4, 5, 6, 7]],  # Parte superior
        [vertices[j] for j in [0, 1, 5, 4]],  # Frente
        [vertices[j] for j in [2, 3, 7, 6]],  # Trás
        [vertices[j] for j in [1, 2, 6, 5]],  # Lado direito
        [vertices[j] for j in [4, 7, 3, 0]],  # Lado esquerdo
    ]
    ax.add_collection3d(
        Poly3DCollection(faces, alpha=0.7, facecolors=color)  # Coloca a cor para o cubo
    )

def aco_optimize_3d(to_alvo, max_cycles=150, ax=None):
    """
    Implementa a Otimização por Colônia de Formigas para Topologia 3D.
    """
    A, nlA, ncA, pA, n = topology_3d(to_alvo)
    m = 50  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n  # Inicializa os feromônios
    best_topology = None
    best_error = float("inf")

    for cycle in range(max_cycles):
        tabu = np.zeros((m, nlA, ncA, pA), dtype=int)

        # Construção de soluções pelas formigas
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
                        prob = np.nan_to_num(
                            prob, nan=1.0 / n, posinf=1.0 / n, neginf=1.0 / n
                        )

                        # Garantir que as probabilidades somem a 1 após as correções
                        prob_sum = np.sum(prob)
                        if prob_sum != 0:
                            prob /= prob_sum
                        else:
                            prob = (
                                np.ones(n) / n
                            )  # Se ainda somar zero, aplique uma distribuição uniforme

                        # Escolha um material com base na probabilidade
                        tabu[k, x, y, z] = np.random.choice(range(n), p=prob)

        # Avaliação de soluções
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

        # Atualiza a topologia a cada ciclo
        plot_topology_3d(best_topology, "Topologia Encontrada", cycle, ax)
        ax.set_title(f"Ciclo: {cycle}, Erro: {best_error:.2f}")
        plt.pause(0.01)  # Pausa para renderizar a figura

        # Se o erro for zero, interrompe o loop
        if best_error == 0:
            print(f"Convergiu no ciclo {cycle}")
            break

# Função principal com interface gráfica
def main():
    def start_aco():
        to_alvo = selected_target.get()
        aco_optimize_3d(to_alvo, ax=ax)

    root = tk.Tk()
    root.title("Otimização ACO 3D")

    selected_target = tk.StringVar(root)
    selected_target.set("alvo_3n_3D_1")  # Valor inicial
    option_menu = tk.OptionMenu(root, selected_target, "alvo_3n_3D_1", "alvo_3n_3D_2")
    option_menu.pack()

    start_button = tk.Button(root, text="Iniciar ACO", command=start_aco)
    start_button.pack()

    # Inicializar a visualização 3D com matplotlib
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Exibir a interface Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()
