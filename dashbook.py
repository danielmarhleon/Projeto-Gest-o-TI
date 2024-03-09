import pandas as pd
import dash
from dash import html, dcc
import plotly.express as px

# Passo 2: Carregamento e Preparação dos Dados
df = pd.read_excel("C:\\Users\\Danie\\OneDrive\\Área de Trabalho\\TCC\\book_ti_dados_tratados.xlsx")

# Definição da função de categorização
def categorizar_tipo(valor):
    if valor == 21:
        return 'Incidente - Sistema'
    elif valor == 22:
        return 'Solicitação - Sistema'
    elif valor == 31:
        return 'Incidente - Infra'
    elif valor == 32:
        return 'Solicitação - Infra'
    else:
        return 'Outro'

df['Categoria_Detalhada'] = df['Tipo'].apply(categorizar_tipo)

# Remove entradas com a categoria "Outro"
df = df[df['Categoria_Detalhada'] != 'Outro']

# Ordem desejada para as categorias
categoria_ordem = ['Solicitação - Sistema', 'Incidente - Sistema', 'Solicitação - Infra', 'Incidente - Infra']

# Assegura que os dados estejam na ordem desejada
df['Categoria_Detalhada'] = pd.Categorical(df['Categoria_Detalhada'], categories=categoria_ordem, ordered=True)

# Prepara os dados para o gráfico
categoria_detalhada_counts = df['Categoria_Detalhada'].value_counts().sort_index().reset_index()
categoria_detalhada_counts.columns = ['Categoria Detalhada', 'Total']

# Criação do gráfico
fig_detalhado = px.bar(categoria_detalhada_counts, x='Categoria Detalhada', y='Total', title="Volume por Categoria Detalhada", color='Categoria Detalhada', barmode='group')

# Calcula o total de OS
total_os = len(df)

# Passo 3: Configuração do Dashboard Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Dashboard de Análise de Desempenho do Setor de TI'),
    html.H2(f"Total de OS: {total_os}"),
    dcc.Graph(
        id='detalhamento-categorias',
        figure=fig_detalhado  # Insere a figura gerada com detalhamento
    )
])

# Passo 4: Execução do Servidor
if __name__ == '__main__':
    app.run_server(debug=True)


    