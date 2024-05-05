import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Carregamento e Preparação dos Dados
df = pd.read_excel("C:\\Users\\Danie\\OneDrive\\Área de Trabalho\\TCC\\book_ti_dados_tratados.xlsx")

# Função de categorização para a primeira entrega
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
df = df[df['Categoria_Detalhada'] != 'Outro']
categoria_detalhada_counts = df['Categoria_Detalhada'].value_counts().reset_index()
categoria_detalhada_counts.columns = ['Categoria Detalhada', 'Total']

# Preparação dos dados para a segunda e terceira entregas
df['Data'] = pd.to_datetime(df['Data'])
df['Mês'] = df['Data'].dt.to_period('M').dt.strftime('%Y-%m')  # Convertendo para string para evitar problemas de serialização
df['Nível de Suporte'] = df['Nível'].replace({'N2': 'N2, N3', 'N3': 'N2, N3'})
nivel_suporte_counts = df['Nível de Suporte'].value_counts().reset_index()
nivel_suporte_counts.columns = ['Nível de Suporte', 'Count']

# Preparação dos dados para a quarta entrega
top_usuarios = df.groupby('Usuário')['OS'].count().nlargest(10).reset_index()
top_areas = df.groupby('Área')['OS'].count().nlargest(10).reset_index()
top_filas = df.groupby('Fila')['OS'].count().nlargest(10).reset_index()

# Gráficos
fig_detalhado = px.bar(categoria_detalhada_counts, x='Categoria Detalhada', y='Total', title="Volume por Categoria Detalhada", color='Categoria Detalhada')
fig_pizza = px.pie(nivel_suporte_counts, values='Count', names='Nível de Suporte', title='Proporção dos Níveis de Suporte')
fig_barras = px.bar(nivel_suporte_counts, x='Nível de Suporte', y='Count', title='Volume por Nível de Suporte')
fig_top_usuarios = px.bar(top_usuarios, x='Usuário', y='OS', title='Top 10 Usuários por OS')
fig_top_areas = px.bar(top_areas, x='Área', y='OS', title='Top 10 Áreas por OS')
fig_top_filas = px.bar(top_filas, x='Fila', y='OS', title='Top 10 Filas por OS')

# App Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Dashboard de Análise de Desempenho do Setor de TI'),
    dcc.Graph(id='grafico-categoria-detalhada', figure=fig_detalhado),
    dcc.Graph(id='grafico-pizza-suporte', figure=fig_pizza),
    dcc.Graph(id='grafico-barras-suporte', figure=fig_barras),
    dcc.Graph(id='top-usuarios', figure=fig_top_usuarios),
    dcc.Graph(id='top-areas', figure=fig_top_areas),
    dcc.Graph(id='top-filas', figure=fig_top_filas)
])

if __name__ == '__main__':
    app.run_server(debug=True)
