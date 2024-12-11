import pandas as pd
import matplotlib.pyplot as plt

# Substitua pelo caminho correto para o arquivo CSV
csv_file_path = 'results_omp.csv'

# Leia o CSV
data = pd.read_csv(csv_file_path)

# Exibe os nomes das colunas para diagnóstico
print("Colunas encontradas no CSV:", data.columns)

# Corrige espaços extras nos nomes das colunas
data.columns = data.columns.str.strip()

# Certifique-se de que os nomes das colunas estejam corretos
if 'Cycle' not in data.columns or 'Error' not in data.columns:
    raise ValueError("O arquivo CSV deve conter as colunas 'Cycle' e 'Error'.")

# Extraia ciclos e erros
cycles = data['Cycle']
errors = data['Error']

# Ajusta o título do gráfico com base no nome do arquivo
if 'omp' in csv_file_path.lower():
    label = "Error during execution - 2D with OpenMP"
else:
    label = "Error during execution - 2D with OpenAcc"

# Plote o gráfico com limites definidos
plt.figure(figsize=(10, 6))
plt.plot(cycles, errors, label=label)
plt.xlabel("Cycles")
plt.ylabel("Error")
plt.title(label)
plt.xlim(0, 150)  # Define os limites do eixo X
plt.ylim(0, 30)   # Define os limites do eixo Y
plt.legend()
plt.grid(True)
plt.show()
