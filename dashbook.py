import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

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
categoria_detalhada_counts = df['Categoria_Detalhada'].value_counts().sort_index().reset_index()
categoria_detalhada_counts.columns = ['Categoria Detalhada', 'Total']

# Função para preparar os dados da segunda entrega
def preparar_dados_segunda_entrega(df):
    df['Data'] = pd.to_datetime(df['Data'])
    df['Mês'] = df['Data'].dt.to_period('M').dt.strftime('%Y-%m')  # Convertendo para string
    abertos_por_mes = df.groupby(['Mês', 'area_TI'])['OS'].count().unstack(fill_value=0)
    resolvidos_por_mes = df[df['Status'] == 'Resolvida'].groupby(['Mês', 'area_TI'])['OS'].count().unstack(fill_value=0)
    backlog_por_mes = df[df['Status'] == 'Pendente'].groupby(['Mês', 'area_TI'])['OS'].count().unstack(fill_value=0)
    
    # Consolidar os dados para cada mês e área de TI
    df_resumo = pd.concat([abertos_por_mes, resolvidos_por_mes, backlog_por_mes], axis=1, keys=['Abertos', 'Resolvidos', 'Backlog'])
    return df_resumo

df_resumo_segunda_entrega = preparar_dados_segunda_entrega(df)

# Gráficos de volume por categoria detalhada
fig_detalhado = px.bar(categoria_detalhada_counts, x='Categoria Detalhada', y='Total', title="Volume por Categoria Detalhada",
                        color='Categoria Detalhada', barmode='group')

# Preparação dos dados para a terceira entrega
df['Nível de Suporte'] = df['Nível'].replace({'N2': 'N2, N3', 'N3': 'N2, N3'})  # Agrupa N2 e N3
nivel_suporte_counts = df['Nível de Suporte'].value_counts().reset_index()
nivel_suporte_counts.columns = ['Nível de Suporte', 'Count']

# Gráficos para a terceira entrega
fig_pizza = px.pie(nivel_suporte_counts, values='Count', names='Nível de Suporte', title='Proporção dos Níveis de Suporte')
fig_barras = px.bar(nivel_suporte_counts, x='Nível de Suporte', y='Count', title='Volume por Nível de Suporte')

# Inicialização do aplicativo Dash
app = dash.Dash(__name__)

# Definindo o layout do aplicativo
app.layout = html.Div([
    html.H1('Dashboard de Análise de Desempenho do Setor de TI'),
    dcc.Graph(id='grafico-categoria-detalhada', figure=fig_detalhado),
    dcc.Dropdown(
        id='equipe-dropdown',
        options=[{'label': equipe, 'value': equipe} for equipe in df_resumo_segunda_entrega.columns.levels[1]],
        value=df_resumo_segunda_entrega.columns.levels[1][0],
        clearable=False
    ),
    dcc.Graph(id='linha-evolucao-tickets'),
    dcc.Graph(id='grafico-pizza-suporte', figure=fig_pizza),
    dcc.Graph(id='grafico-barras-suporte', figure=fig_barras)
])

# Callbacks para a atualização dos gráficos dinâmicos
@app.callback(
    Output('linha-evolucao-tickets', 'figure'),
    [Input('equipe-dropdown', 'value')]
)
def update_line_chart(equipe_selecionada):
    df_filtrado = df_resumo_segunda_entrega.xs(equipe_selecionada, level=1, axis=1)
    fig = px.line(
        df_filtrado,
        x=df_filtrado.index,
        y=df_filtrado.columns,
        markers=True,
        title=f'Evolução dos Tickets - Equipe {equipe_selecionada}'
    )
    fig.update_layout(xaxis_title='Mês', yaxis_title='Total de Tickets')
    return fig

# Execução do servidor
if __name__ == '__main__':
    app.run_server(debug=True)
