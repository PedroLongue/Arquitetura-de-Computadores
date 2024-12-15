import pandas as pd
import matplotlib.pyplot as plt

# Substitua pelo caminho correto para o arquivo CSV de Tempo e Erro
csv_file_path = 'time_error_3D_normal.csv'

# Leia o CSV de Tempo e Erro
data = pd.read_csv(csv_file_path)

# Exibe os nomes das colunas para diagnóstico
print("Colunas encontradas no CSV:", data.columns)

# Corrige espaços extras nos nomes das colunas
data.columns = data.columns.str.strip()

# Certifique-se de que os nomes das colunas estejam corretos
if 'Time(ms)' not in data.columns or 'Error' not in data.columns:
    raise ValueError("O arquivo CSV deve conter as colunas 'Time(ms)' e 'Error'.")

# Extraia tempo e erros
time = data['Time(ms)']
errors = data['Error']

# Ajusta o título do gráfico com base no nome do arquivo
if '3D' in csv_file_path and 'OpenAcc' in csv_file_path:
    title = "Error x Time - OpenAcc - 3D"
    xlim = 30
    ylim = 30
elif '2D' in csv_file_path and 'OpenAcc' in csv_file_path:
    title = "Error x Time - OpenAcc - 2D"
    xlim = 30
    ylim = 30
elif '3D' in csv_file_path and 'OpenMP' in csv_file_path:
    title = "Error x Time - OpenMP - 3D"
    xlim = 30
    ylim = 30
elif '2D' in csv_file_path and 'OpenMP' in csv_file_path:
    title = "Error x Time - OpenMP - 2D"
    xlim = 30
    ylim = 30
elif '2D' in csv_file_path and 'normal' in csv_file_path:
    title = "Error x Time - 2D"
    xlim = 20000
    ylim = 30
elif '3D' in csv_file_path and 'normal' in csv_file_path:
    title = "Error x Time - 3D"
    xlim = 20000
    ylim = 30
else:
    title = "Error x Time"
    xlim = 10000
    ylim = 30

# Plote o gráfico para Tempo e Erro
plt.figure(figsize=(10, 6))
plt.plot(time, errors, label=title, color='orange')
plt.xlabel("Time (ms)")
plt.ylabel("Error")
plt.title(title)
plt.xlim(0, xlim)  # Define os limites do eixo X
plt.ylim(0, ylim)   # Define os limites do eixo Y
plt.grid(True)
plt.legend()
plt.show()
