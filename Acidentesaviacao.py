import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt

# Caminho para o banco de dados
db_path = r"C:\Users\User\Documents\portfolio\recomendacoes.db"

# Caminho para a pasta onde estão os arquivos Excel
excel_path = r"C:\Users\User\Documents\portfolio"

# Conectando ao banco de dados (ou criando-o se não existir)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criando a tabela recomendacao
cursor.execute('''
CREATE TABLE IF NOT EXISTS recomendacao (
    codigo_ocorrencia4 TEXT,
    recomendacao_numero TEXT,
    recomendacao_dia_assinatura TEXT,
    recomendacao_dia_encaminhamento TEXT,
    recomendacao_dia_feedback TEXT,
    recomendacao_conteudo TEXT,
    recomendacao_status TEXT,
    recomendacao_destinatario_sigla TEXT,
    recomendacao_destinatario TEXT
)
''')

# Criando a tabela fator_contribuinte
cursor.execute('''
CREATE TABLE IF NOT EXISTS fator_contribuinte (
    codigo_ocorrencia3 TEXT,
    fator_nome TEXT,
    fator_aspecto TEXT,
    fator_condicionante TEXT,
    fator_area TEXT
)
''')

# Criando a tabela aeronave
cursor.execute('''
CREATE TABLE IF NOT EXISTS aeronave (
    codigo_ocorrencia2 TEXT,
    aeronave_matricula TEXT,
    aeronave_operador_categoria TEXT,
    aeronave_tipo_veiculo TEXT,
    aeronave_fabricante TEXT,
    aeronave_modelo TEXT,
    aeronave_tipo_icao TEXT,
    aeronave_motor_tipo TEXT,
    aeronave_motor_quantidade TEXT,
    aeronave_pmd TEXT,
    aeronave_pmd_categoria TEXT,
    aeronave_assentos TEXT,
    aeronave_ano_fabricacao TEXT,
    aeronave_pais_fabricante TEXT,
    aeronave_pais_registro TEXT,
    aeronave_registro_categoria TEXT,
    aeronave_registro_segmento TEXT,
    aeronave_voo_origem TEXT,
    aeronave_voo_destino TEXT,
    aeronave_fase_operacao TEXT,
    aeronave_tipo_operacao TEXT,
    aeronave_nivel_dano TEXT,
    aeronave_fatalidades_total TEXT
)
''')

# Criando a tabela ocorrencia_tipo
cursor.execute('''
CREATE TABLE IF NOT EXISTS ocorrencia_tipo (
    codigo_ocorrencia1 TEXT,
    ocorrencia_tipo TEXT,
    ocorrencia_tipo_categoria TEXT,
    taxonomia_tipo_icao TEXT
)
''')

# Criando a tabela ocorrencia
cursor.execute('''
CREATE TABLE IF NOT EXISTS ocorrencia (
    codigo_ocorrencia TEXT,
    codigo_ocorrencia1 TEXT,
    codigo_ocorrencia2 TEXT,
    codigo_ocorrencia3 TEXT,
    codigo_ocorrencia4 TEXT,
    ocorrencia_classificacao TEXT,
    ocorrencia_latitude TEXT,
    ocorrencia_longitude TEXT,
    ocorrencia_cidade TEXT,
    ocorrencia_uf TEXT,
    ocorrencia_pais TEXT,
    ocorrencia_aerodromo TEXT,
    ocorrencia_dia TEXT,
    ocorrencia_hora TEXT,
    investigacao_aeronave_liberada TEXT,
    investigacao_status TEXT,
    divulgacao_relatorio_numero TEXT,
    divulgacao_relatorio_publicado TEXT,
    divulgacao_dia_publicacao TEXT,
    total_recomendacoes TEXT,
    total_aeronaves_envolvidas TEXT,
    ocorrencia_saida_pista TEXT
)
''')

# Função para substituir "***" e NULL por "" e inserir dados de um arquivo Excel em uma tabela
def insert_data_from_excel(table_name):
    file_path = os.path.join(excel_path, f"{table_name}.xlsx")
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)

        # Substituindo "***" e valores NULL por ""
        df.replace({"***": "", pd.NA: "", None: ""}, inplace=True)

        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Dados inseridos na tabela {table_name} com sucesso!")
    else:
        print(f"Arquivo {table_name}.xlsx não encontrado.")

# Inserindo dados nas tabelas
insert_data_from_excel('recomendacao')
insert_data_from_excel('fator_contribuinte')
insert_data_from_excel('aeronave')
insert_data_from_excel('ocorrencia_tipo')
insert_data_from_excel('ocorrencia')

# Criando a view com as tabelas combinadas
cursor.execute('''
CREATE VIEW IF NOT EXISTS view_ocorrencias AS
SELECT *
FROM ocorrencia
LEFT JOIN ocorrencia_tipo ON ocorrencia.codigo_ocorrencia1 = ocorrencia_tipo.codigo_ocorrencia1
LEFT JOIN aeronave ON ocorrencia.codigo_ocorrencia2 = aeronave.codigo_ocorrencia2
LEFT JOIN fator_contribuinte ON ocorrencia.codigo_ocorrencia3 = fator_contribuinte.codigo_ocorrencia3
LEFT JOIN recomendacao ON ocorrencia.codigo_ocorrencia4 = recomendacao.codigo_ocorrencia4
''')

# Salvando a view em um DataFrame e exportando para Excel
query = "SELECT * FROM view_ocorrencias"
df_view = pd.read_sql_query(query, conn)

# Caminho para o arquivo Excel da view
view_excel_path = os.path.join(excel_path, "view_ocorrencias.xlsx")
df_view.to_excel(view_excel_path, index=False)

# Função para criar gráficos a partir da coluna ocorrencia_cidade
def plot_ocorrencias_cidade(df):
    # Gráfico das 10 cidades com mais ocorrências
    cidade_counts = df['ocorrencia_cidade'].value_counts().head(10)
    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    cidade_counts.plot(kind='bar', color='navy')
    plt.title('Top 10 Cidades com Mais Ocorrências')
    plt.xlabel('Cidades')
    plt.ylabel('Número de Ocorrências')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_10_cidades_ocorrencias.png"))
    plt.show()

    # Gráfico das 10 cidades com mais ocorrências filtradas para "ACIDENTE"
    acidente_counts = df[df['ocorrencia_classificacao'] == 'ACIDENTE']['ocorrencia_cidade'].value_counts().head(10)
    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    acidente_counts.plot(kind='bar', color='navy')
    plt.title('Top 10 Cidades com Mais Ocorrências (Classificação: ACIDENTE)')
    plt.xlabel('Cidades')
    plt.ylabel('Número de Ocorrências')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_10_cidades_acidente.png"))
    plt.show()

# Chamando a função para plotar os gráficos
plot_ocorrencias_cidade(df_view)

# Commitando as mudanças e fechando a conexão
conn.commit()
conn.close()

print("Banco de dados criado, dados inseridos, view criada, exportada para Excel e gráficos gerados com sucesso!")

# Função para criar gráfico do percentual de ACIDENTE por cidade
def plot_percentual_acidente(df):
    # Contando ocorrências totais por cidade
    total_counts = df['ocorrencia_cidade'].value_counts()
    
    # Contando ocorrências de ACIDENTE por cidade
    acidente_counts = df[df['ocorrencia_classificacao'] == 'ACIDENTE']['ocorrencia_cidade'].value_counts()
    
    # Calculando o percentual de ACIDENTE
    percentual_acidente = (acidente_counts / total_counts * 100).fillna(0)
    
    # Excluindo cidades com percentual igual a 100
    percentual_acidente = percentual_acidente[percentual_acidente != 100]

    # Selecionando as 10 cidades com maior percentual
    top_percentual_acidente = percentual_acidente.nlargest(10)

    # Preparando dados para o gráfico
    top_cidades = top_percentual_acidente.index
    top_percentuais = top_percentual_acidente.values
    acidentes = acidente_counts[top_cidades].values
    totais = total_counts[top_cidades].values
    
    # Plotando o gráfico
    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    bars = plt.bar(top_cidades, top_percentuais, color='navy')

    # Adicionando rótulos de valor
    for bar, acidente, total in zip(bars, acidentes, totais):
        height = bar.get_height()
        label = f'{acidente}/{total}'
        plt.text(bar.get_x() + bar.get_width() / 2, height, label, ha='center', va='bottom')

    plt.title('Top 10 Cidades com Maior Percentual de ACIDENTE')
    plt.xlabel('Cidades')
    plt.ylabel('Percentual de ACIDENTE (%)')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_10_percentual_acidente.png"))
    plt.show()

# Chamando a função para plotar o gráfico de percentual
plot_percentual_acidente(df_view)

# Função para criar gráfico dos 10 maiores motivos de acidentes
def plot_maiores_motivos_acidente(df):
    # Filtrando para obter apenas os acidentes
    df_acidentes = df[df['ocorrencia_classificacao'] == 'ACIDENTE']
    
    # Contando a ocorrência de cada tipo de acidente
    maiores_motivos = df_acidentes['ocorrencia_tipo'].value_counts().nlargest(10)

    # Reduzindo os nomes dos tipos de ocorrência
    maiores_motivos.index = [tipo[:10] + '...' if len(tipo) > 10 else tipo for tipo in maiores_motivos.index]

    # Plotando o gráfico
    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    bars = maiores_motivos.plot(kind='bar', color='navy')
    
    # Adicionando rótulos de valor
    for bar in bars.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
                 bar.get_height(), ha='center', va='bottom')

    plt.title('Top 10 Motivos de ACIDENTE')
    plt.xlabel('Tipos de Ocorrência')
    plt.ylabel('Número de Ocorrências')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_10_motivos_acidente.png"))
    plt.show()

# Chamando a função para plotar o gráfico dos maiores motivos de acidentes
plot_maiores_motivos_acidente(df_view)


# Função para criar gráficos de ocorrências de aeronaves
def plot_ocorrencias_aeronaves(df):
    # Gráfico das 5 aeronaves com mais ocorrências
    top_aeronaves = df['aeronave_modelo'].value_counts().nlargest(5)

    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    top_aeronaves.plot(kind='bar', color='navy')
    plt.title('Top 5 Aeronaves com Mais Ocorrências')
    plt.xlabel('Modelo da Aeronave')
    plt.ylabel('Número de Ocorrências')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_5_aeronaves_ocorrencias.png"))
    plt.show()

    # Gráfico das 5 aeronaves com mais ACIDENTES
    top_aeronaves_acidente = df[df['ocorrencia_classificacao'] == 'ACIDENTE']['aeronave_modelo'].value_counts().nlargest(5)

    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    top_aeronaves_acidente.plot(kind='bar', color='navy')
    plt.title('Top 5 Aeronaves com Mais ACIDENTES')
    plt.xlabel('Modelo da Aeronave')
    plt.ylabel('Número de ACIDENTES')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_5_aeronaves_acidentes.png"))
    plt.show()

    # Gráfico dos 5 fabricantes com mais ACIDENTES
    top_fabricantes_acidente = df[df['ocorrencia_classificacao'] == 'ACIDENTE']['aeronave_fabricante'].value_counts().nlargest(5)

    plt.figure(figsize=(10, 6), facecolor='lightgray')
    plt.gca().set_facecolor('lightgray')  # Definir o fundo como cinza

    top_fabricantes_acidente.plot(kind='bar', color='navy')
    plt.title('Top 5 Fabricantes com Mais ACIDENTES')
    plt.xlabel('Fabricante')
    plt.ylabel('Número de ACIDENTES')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "top_5_fabricantes_acidentes.png"))
    plt.show()

# Chamando a função para plotar os gráficos de ocorrências de aeronaves
plot_ocorrencias_aeronaves(df_view)


# Função para criar gráfico de pizza com as regiões do Brasil
def plot_ocorrencias_por_regiao(df):
    # Mapeamento das UFs para as regiões
    regiao_map = {
        'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte', 'BA': 'Nordeste',
        'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste', 'GO': 'Centro-Oeste',
        'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
        'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste', 'PI': 'Nordeste',
        'RJ': 'Sudeste', 'RN': 'Nordeste', 'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
        'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
    }
    
    # Criando uma nova coluna para a região
    df['regiao'] = df['ocorrencia_uf'].map(regiao_map)

    # Contando o número de ocorrências por região
    ocorrencias_regiao = df['regiao'].value_counts()

    # Criando o gráfico de pizza
    plt.figure(figsize=(8, 8))
    plt.pie(ocorrencias_regiao, labels=ocorrencias_regiao.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title('Distribuição de Ocorrências por Região do Brasil')
    plt.axis('equal')  # Para garantir que o gráfico de pizza seja circular
    plt.tight_layout()
    plt.savefig(os.path.join(excel_path, "ocorrencias_por_regiao.png"))
    plt.show()

# Chamando a função para plotar o gráfico de ocorrências por região
plot_ocorrencias_por_regiao(df_view)

import dash
import dash_html_components as html
import dash_core_components as dcc
import os

# Criação do aplicativo Dash
app = dash.Dash(__name__)

# Caminho para a pasta de imagens
images_dir = os.path.join(excel_path)  # Substitua por onde você armazena suas imagens, se necessário

# Títulos e caminhos para os gráficos gerados
graph_paths = [
    os.path.join(images_dir, "top_10_cidades_ocorrencias.png"),
    os.path.join(images_dir, "top_10_cidades_acidente.png"),
    os.path.join(images_dir, "top_10_percentual_acidente.png"),
    os.path.join(images_dir, "top_10_motivos_acidente.png"),
    os.path.join(images_dir, "top_5_aeronaves_ocorrencias.png"),
    os.path.join(images_dir, "top_5_aeronaves_acidentes.png"),
    os.path.join(images_dir, "top_5_fabricantes_acidentes.png"),
    os.path.join(images_dir, "ocorrencias_por_regiao.png"),
]

# Layout do dashboard
app.layout = html.Div(style={'backgroundColor': 'darkgray', 'padding': '20px'}, children=[
    html.H1("Análise de Ocorrências Aeronáuticas na Aviação Civil Brasileira", style={'textAlign': 'center', 'color': 'white', 'fontFamily': 'Arial, sans-serif'}),
    
    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}, children=[
        html.Img(src=f"/assets/top_10_cidades_ocorrencias.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
        html.Img(src=f"/assets/top_10_cidades_acidente.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
        html.Img(src=f"/assets/top_10_motivos_acidente.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
        html.Img(src=f"/assets/top_5_aeronaves_ocorrencias.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
        html.Img(src=f"/assets/top_5_aeronaves_acidentes.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
        html.Img(src=f"/assets/top_5_fabricantes_acidentes.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
    ]),
    
    html.Div(style={'position': 'absolute', 'top': '20px', 'right': '20px'}, children=[
        html.Img(src=f"/assets/ocorrencias_por_regiao.png", style={'height': '300px', 'width': 'auto', 'margin': '10px'}),
    ])
])

# Crie uma pasta "assets" no mesmo diretório do seu script, se ainda não existir
assets_folder = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.exists(assets_folder):
    os.makedirs(assets_folder)

# Copie as imagens para a pasta "assets"
for path in graph_paths:
    if os.path.exists(path):
        os.rename(path, os.path.join(assets_folder, os.path.basename(path)))

# Iniciando o servidor
app.run_server(port=8050, debug=False)

# Ao executar o aplicativo, o Dash irá automaticamente abrir no seu navegador
