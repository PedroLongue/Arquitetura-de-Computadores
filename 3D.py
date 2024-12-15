import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tkinter as tk

# Definição de variáveis globais
hplot = None
htext = None

def topology(to_alvo):
    """
    A    : topology matrix
    nlA  : number of lines of A
    ncA  : number of columns of A
    pA   : depth of A
    n    : type (number) of materials
    """

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
                [2, 2, 1, 1],  # Camada 1
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ],
            [
                [2, 2, 1, 1],  # Camada 2
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ],
            [
                [2, 2, 1, 1],  # Camada 3
                [2, 0, 0, 1],
                [2, 0, 0, 1],
                [2, 2, 1, 1]
            ]
        ])
    elif to_alvo == 'alvo_I2_complex':
        n = 2
        A = np.array([
            [
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],  # Camada 1
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0],
                [0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
                [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
                [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
                [0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],  # Camada 2
                [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
                [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0],
                [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0],
                [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                [1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0],
                [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0],
                [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
            ]
        ])

    else:
        raise ValueError("The topology specified does not exist!")

    # Shape of the array
    nlA, ncA, pA = A.shape if A.ndim == 3 else (*A.shape, 1)
    return A, nlA, ncA, pA, n

def get3Dpoints(vec, coordinates, orientation=[0, 0, 0]):
    coordinates = [1/2 * coordinates[0], 1/2 * coordinates [1], 1/2 * coordinates[2]]

    # Criação da matriz de rotação
    rot_mat = np.array([
        [
            np.cos(orientation[1]) * np.cos(orientation[2]),
            -np.cos(orientation[1]) * np.sin(orientation[2]),
            np.sin(orientation[1])
        ],
        [
            np.sin(orientation[0]) * np.sin(orientation[1]) * np.cos(orientation[2]) + np.cos(orientation[0]) * np.sin(orientation[2]),
            -np.sin(orientation[0]) * np.sin(orientation[1]) * np.sin(orientation[2]) + np.cos(orientation[0]) * np.cos(orientation[2]),
            -np.sin(orientation[0]) * np.cos(orientation[1])
        ],
        [
            -np.cos(orientation[0]) * np.sin(orientation[1]) * np.cos(orientation[2]) + np.sin(orientation[0]) * np.sin(orientation[2]),
            np.cos(orientation[0]) * np.sin(orientation[1]) * np.sin(orientation[2]) + np.sin(orientation[0]) * np.cos(orientation[2]),
            np.cos(orientation[0]) * np.cos(orientation[1])
        ]
    ])

    # Aplicação da transformação
    transformed_coordinates = np.dot(rot_mat, coordinates)
    erg_coordinates = vec + transformed_coordinates

    return erg_coordinates

def plotcube(coordinates, size, orientation, color8, transparency, LineOnOff, ax):
    """
    Função para plotar um cubo 3D.
    """
    # Calcula os 8 vértices
    c1 = get3Dpoints(coordinates, [-size[0], -size[1], -size[2]], orientation)
    c2 = get3Dpoints(coordinates, [size[0], -size[1], -size[2]], orientation)
    c3 = get3Dpoints(coordinates, [-size[0], -size[1], size[2]], orientation)
    c4 = get3Dpoints(coordinates, [size[0], -size[1], size[2]], orientation)
    c5 = get3Dpoints(coordinates, [-size[0], size[1], -size[2]], orientation)
    c6 = get3Dpoints(coordinates, [size[0], size[1], -size[2]], orientation)
    c7 = get3Dpoints(coordinates, [-size[0], size[1], size[2]], orientation)
    c8 = get3Dpoints(coordinates, [size[0], size[1], size[2]], orientation)

    # Definir as faces do cubo (cada face é um quadrilátero)
    faces = [
        [c1, c2, c4, c3],  # Face inferior
        [c5, c6, c8, c7],  # Face superior
        [c1, c2, c6, c5],  # Face frontal
        [c3, c4, c8, c7],  # Face traseira
        [c1, c3, c7, c5],  # Face esquerda
        [c2, c4, c8, c6],  # Face direita
    ]

    # Cria uma Poly3DCollection para desenhar o cubo
    cube = Poly3DCollection(faces, facecolors=color8, linewidths=1, edgecolors='k', alpha=transparency)
    
    # Adiciona a coleção de faces ao gráfico 3D
    ax.add_collection3d(cube)

def plottopology(A, n, fig, ax, *args):
    """
    Função para plotar a topologia baseada em uma matriz A, e outras informações.
    """
    global hplot, htext

    nlA, ncA, pA = A.shape if A.ndim == 3 else (*A.shape, 1)

    if fig == 1:
        # Criar o gráfico com a topologia objetivo
        ax.set_box_aspect([1, 1, 1])  # Assegura que a caixa tenha proporções iguais
        ax.set_title('Goal Topology')
        ax.clear()

        if pA == 1:
            # Se pA == 1, mostramos o gráfico 2D
            ax.imshow(A, cmap='gray', interpolation='nearest')
            ax.axis('off')  # Desativa os eixos para não mostrar números ou grades
            plt.show()
        else:
            # Plotando a estrutura 3D
            d1 = ncA + 1
            d2 = pA + 1
            d3 = nlA + 1

            
            ax.plot3D([0, d1, d1, 0, 0, d1, d1, 0], 
                      [0, 0, 0, 0, d2, d2, d2, d2], 
                      [0, 0, d3, d3, 0, 0, d3, d3], 'k.', markersize=0.1)

            # Plotando os cubos dentro da topologia
            for p in range(min(pA, A.shape[2])-1, -1, -1):
                for i in range(min(nlA, A.shape[0])-1, -1, -1):
                    for j in range(min(ncA, A.shape[1])):
                        if n > 1:
                            color_value = A[i, j, p] / (n - 1)
                            rgba = (color_value, color_value, color_value, 0.5)
                            plotcube([j, p, i], [1, 1, 1], [0, 0, 0], [rgba] * 8, 0.5, 1, ax)
            
            plt.draw()

def aco_optimize_3d(to_alvo, max_cycles=150, ax=None, ax2=None):
    """
    Implementa a Otimização por Colônia de Formigas para Topologia 3D.
    """
    A, nlA, ncA, pA, n = topology(to_alvo)
    m = 80  # Número de formigas
    tau = np.ones((n, nlA * ncA * pA)) / n  # Inicializa os feromônios
    best_topology = None
    best_error = float("inf")

    # Desenha a topologia alvo na figura
    plottopology(A, 3, 1, ax2)
    ax2.set_title('Topologia Alvo')

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
        plottopology(best_topology, 3, 1, ax)
        ax.set_title(f"Ciclo: {cycle}, Erro: {best_error:.2f}")

        plt.pause(0.01)  # Pausa para renderizar a figura

        errors.append(best_error)
        # Se o erro for zero, interrompe o loop
        if best_error == 0:
            print(f"Convergiu no ciclo {cycle}")
            break
    
    # Gera o gráfico de Erro x Ciclo
    plt.figure(figsize=(10, 6))
    plt.plot(errors, label="Error during execution - 3D")
    plt.xlabel("Cycles")
    plt.ylabel("Error")
    plt.title("Error Evolution during Optimization Execution - 3D")
    plt.legend()
    plt.grid(True)
    plt.show()

# Função principal com interface gráfica
def main():
    def start_aco():
        to_alvo = selected_target.get()
        aco_optimize_3d(to_alvo, ax=ax, ax2=ax2)

    root = tk.Tk()
    root.title("Otimização ACO 3D")

    selected_target = tk.StringVar(root)
    selected_target.set("alvo_3n_3D_1")  # Valor inicial
    option_menu = tk.OptionMenu(root, selected_target, "alvo_3n_3D_1", "alvo_3n_3D_2")
    option_menu.pack()

    start_button = tk.Button(root, text="Iniciar ACO", command=start_aco)
    start_button.pack()

    # Cria a figura
    fig = plt.figure(figsize=(10, 8))

    # Adiciona o gráfico alvo (à esquerda)
    ax2 = fig.add_subplot(121, projection='3d')

    # Adiciona o gráfico ACO (à direita)
    ax = fig.add_subplot(122, projection='3d')

    # Exibe a interface Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()
