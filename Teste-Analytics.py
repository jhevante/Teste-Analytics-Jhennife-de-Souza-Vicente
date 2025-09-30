#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para o Teste de Estagiário de Analytics (Quod)
- Simula dataset de vendas (01/01/2023 a 31/12/2023)
- Introduz valores faltantes e duplicatas
- Faz limpeza e salva data_clean.csv
- Gera análises (vendas por produto) e gráficos
- Cria banco SQLite com tabela 'vendas'
- Gera arquivo sql/consultas_sql.sql com as consultas solicitadas
- Executa as consultas no SQLite e salva resultados
- Cria docs/relatorio_insights.md com resumo e recomendações (<=300 palavras)
Autor: Seu Nome
Data: (gerado automaticamente)
Dependências: pandas, numpy, matplotlib
Instalação: pip install pandas numpy matplotlib
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# CONFIGURAÇÕES / PATHS
# -------------------------

RANDOM_SEED = 42
N_RECORDS = 120  # >= 50
OUTPUT_DIRS = ['data', 'outputs', 'sql', 'docs']

for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

RAW_CSV = os.path.join('data', 'dataset_raw.csv')
CLEAN_CSV = os.path.join('data', 'data_clean.csv')
SALES_BY_PRODUCT_CSV = os.path.join('data', 'sales_by_product.csv')
DB_PATH = os.path.join('data', 'vendas.db')
SQL_FILE = os.path.join('sql', 'consultas_sql.sql')
SQL_Q1_RESULT = os.path.join('data', 'sql_query1_results.csv')
SQL_Q2_RESULT = os.path.join('data', 'sql_query2_results.csv')
REPORT_MD = os.path.join('docs', 'relatorio_insights.md')
PLOT_MONTHLY = os.path.join('outputs', 'monthly_sales_trend.png')
PLOT_TOP_PRODUCTS = os.path.join('outputs', 'top_products_bar.png')
PLOT_CATEGORY = os.path.join('outputs', 'sales_by_category_pie.png')

# -------------------------
# 1) SIMULAÇÃO DO DATASET (2023)
# -------------------------

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

products = [
    {'Produto': 'Fone de Ouvido A', 'Categoria': 'Eletrônicos', 'Preco_base': 120.0},
    {'Produto': 'Carregador B', 'Categoria': 'Eletrônicos', 'Preco_base': 50.0},
    {'Produto': 'Caneca C', 'Categoria': 'Casa', 'Preco_base': 25.0},
    {'Produto': 'Camiseta D', 'Categoria': 'Vestuário', 'Preco_base': 45.0},
    {'Produto': 'Notebook E', 'Categoria': 'Eletrônicos', 'Preco_base': 3500.0},
    {'Produto': 'Mochila F', 'Categoria': 'Vestuário', 'Preco_base': 150.0},
    {'Produto': 'Teclado G', 'Categoria': 'Eletrônicos', 'Preco_base': 260.0},
    {'Produto': 'Livro H', 'Categoria': 'Livros', 'Preco_base': 40.0},
]

def random_date(start, end):
    """Gera data aleatória entre start e end (datetime.date)"""
    delta = end - start
    rand_days = random.randint(0, delta.days)
    return start + timedelta(days=rand_days)

start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

rows = []
for i in range(1, N_RECORDS + 1):
    p = random.choice(products)
    date = random_date(start_date, end_date)
    # Preço com variação +/-20%
    preco = round(p['Preco_base'] * (1 + np.random.normal(0, 0.08)), 2)
    quantidade = random.randint(1, 6)
    rows.append({
        'ID': i,
        'Data': date.strftime('%Y-%m-%d'),
        'Produto': p['Produto'],
        'Categoria': p['Categoria'],
        'Quantidade': quantidade,
        'Preco': preco
    })

df_raw = pd.DataFrame(rows)

# introduzir alguns valores faltantes aleatórios
n_missing = max(3, int(0.03 * len(df_raw)))  # ~3% ou pelo menos 3
missing_indices = np.random.choice(df_raw.index, n_missing, replace=False)
for idx in missing_indices:
    col = random.choice(['Produto', 'Categoria', 'Quantidade', 'Preco'])
    df_raw.at[idx, col] = None

# introduzir duplicatas (repetir algumas linhas)
dup_indices = np.random.choice(df_raw.index, 3, replace=False)
df_raw = pd.concat([df_raw, df_raw.loc[dup_indices]], ignore_index=True).reset_index(drop=True)

# salvar raw
df_raw.to_csv(RAW_CSV, index=False, encoding='utf-8')
print(f"[1] Dataset raw salvo em: {RAW_CSV} (registros: {len(df_raw)})")

# -------------------------
# 2) LIMPEZA DOS DADOS
# -------------------------

df = df_raw.copy()
# remover duplicatas completas
before = len(df)
df = df.drop_duplicates()
after = len(df)
print(f"[2] Duplicatas removidas: {before - after}")

# converter Data para datetime
df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')

# tratar Quantidade faltante -> preencher com mediana arredondada
if df['Quantidade'].isnull().any():
    med_q = int(df['Quantidade'].median(skipna=True) if not df['Quantidade'].median(skipna=True) != np.nan else 1)
    df['Quantidade'] = df['Quantidade'].fillna(med_q)
    print(f"    Preenchido Quantidade faltante com mediana = {med_q}")

# tratar Preco faltante -> preencher com mediana por produto, senão mediana geral
if df['Preco'].isnull().any():
    df['Preco'] = df.groupby('Produto')['Preco'].transform(lambda x: x.fillna(x.median()))
    # se ainda faltar (produto tinha NaN tudo), preencher com mediana geral
    if df['Preco'].isnull().any():
        med_preco = df['Preco'].median(skipna=True)
        df['Preco'] = df['Preco'].fillna(med_preco)
        print(f"    Preenchido Preco faltante com mediana geral = {med_preco}")

# tratar Produto/Categoria faltantes -> preencher com modo (mais frequente)
if df['Produto'].isnull().any():
    mode_prod = df['Produto'].mode(dropna=True)
    if len(mode_prod) > 0:
        df['Produto'] = df['Produto'].fillna(mode_prod[0])
        print(f"    Preenchido Produto faltante com modo = {mode_prod[0]}")
    else:
        df['Produto'] = df['Produto'].fillna('Produto_Desconhecido')

if df['Categoria'].isnull().any():
    mode_cat = df['Categoria'].mode(dropna=True)
    if len(mode_cat) > 0:
        df['Categoria'] = df['Categoria'].fillna(mode_cat[0])
        print(f"    Preenchido Categoria faltante com modo = {mode_cat[0]}")
    else:
        df['Categoria'] = df['Categoria'].fillna('Categoria_Desconhecida')

# garantir tipos
df['Quantidade'] = df['Quantidade'].astype(int)
df['Preco'] = df['Preco'].astype(float)

# salvar cleaned
df.to_csv(CLEAN_CSV, index=False, encoding='utf-8')
print(f"[3] Dataset limpo salvo em: {CLEAN_CSV} (registros: {len(df)})")

# -------------------------
# 3) ANÁLISE (Total de Vendas por produto)
# -------------------------

# criar coluna Total (Quantidade * Preco)
df['Total'] = (df['Quantidade'] * df['Preco']).round(2)

sales_by_product = (
    df.groupby(['Produto', 'Categoria'], as_index=False)
      .agg(total_vendas=('Total', 'sum'),
           total_quantidade=('Quantidade', 'sum'),
           transacoes=('ID', 'count'))
      .sort_values('total_vendas', ascending=False)
)
sales_by_product.to_csv(SALES_BY_PRODUCT_CSV, index=False, encoding='utf-8')
print(f"[4] Vendas por produto salvas em: {SALES_BY_PRODUCT_CSV}")

# identificar produto com maior venda total
top_product_row = sales_by_product.iloc[0]
top_product = top_product_row['Produto']
top_product_val = top_product_row['total_vendas']
print(f"[5] Produto com maior total de vendas: {top_product} -> R$ {top_product_val:.2f}")

# -------------------------
# 4) VISUALIZAÇÕES (salvar em outputs/)
# -------------------------

# 4.1 Tendência mensal
df_monthly = df.set_index('Data').resample('M')['Total'].sum()
plt.figure(figsize=(10, 5))
plt.plot(df_monthly.index, df_monthly.values, marker='o')
plt.title('Tendência mensal de vendas (2023)')
plt.xlabel('Mês')
plt.ylabel('Total de Vendas (R$)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(PLOT_MONTHLY)
plt.close()
print(f"[6] Gráfico de tendência mensal salvo em: {PLOT_MONTHLY}")

# 4.2 Top produtos (barras)
top_n = 10
top_products = sales_by_product.head(top_n).sort_values('total_vendas')
plt.figure(figsize=(8, 6))
plt.barh(top_products['Produto'], top_products['total_vendas'])
plt.title(f'Top {top_n} produtos por total de vendas (2023)')
plt.xlabel('Total de vendas (R$)')
plt.tight_layout()
plt.savefig(PLOT_TOP_PRODUCTS)
plt.close()
print(f"[7] Gráfico de top produtos salvo em: {PLOT_TOP_PRODUCTS}")

# 4.3 Vendas por categoria (pizza)
cat_sales = df.groupby('Categoria', as_index=False)['Total'].sum().sort_values('Total', ascending=False)
plt.figure(figsize=(7, 7))
plt.pie(cat_sales['Total'], labels=cat_sales['Categoria'], autopct='%1.1f%%', startangle=140)
plt.title('Distribuição de vendas por categoria (2023)')
plt.tight_layout()
plt.savefig(PLOT_CATEGORY)
plt.close()
print(f"[8] Gráfico de vendas por categoria salvo em: {PLOT_CATEGORY}")

# -------------------------
# 5) CRIAR BANCO SQLITE E SALVAR TABELA 'vendas'
# -------------------------

conn = sqlite3.connect(DB_PATH)
# Salvar df limpo no banco (colunas: ID, Data, Produto, Categoria, Quantidade, Preco, Total)
df.to_sql('vendas', conn, if_exists='replace', index=False)
print(f"[9] Banco SQLite criado em: {DB_PATH} com tabela 'vendas'")

# -------------------------
# 6) GERAR ARQUIVO SQL (consultas solicitadas)
# -------------------------

sql_text = textwrap.dedent(f"""
-- consultas_sql.sql
-- Consulta 1: listar produto, categoria e soma total de vendas (quantidade * preco) por produto, ordenado desc.
-- Sintaxe padrão SQL:
SELECT Produto, Categoria, SUM(Quantidade * Preco) AS total_vendas
FROM vendas
GROUP BY Produto, Categoria
ORDER BY total_vendas DESC;

-- Consulta 2: identificar produtos que venderam menos no mês de junho de 2024.
-- Observação: nosso dataset simulado cobre apenas 2023. A consulta abaixo é genérica e válida,
-- mas no banco atual ela retornará vazio (nenhum registro em junho/2024).
-- Versão padrão (caso o SGDB suporte EXTRACT):
SELECT Produto, Categoria, SUM(Quantidade * Preco) AS total_vendas
FROM vendas
WHERE EXTRACT(MONTH FROM Data) = 6 AND EXTRACT(YEAR FROM Data) = 2024
GROUP BY Produto, Categoria
ORDER BY total_vendas ASC;

-- Versão específica para SQLite (utilize se estiver usando SQLite):
SELECT Produto, Categoria, SUM(Quantidade * Preco) AS total_vendas
FROM vendas
WHERE strftime('%m', Data) = '06' AND strftime('%Y', Data) = '2024'
GROUP BY Produto, Categoria
ORDER BY total_vendas ASC;
""").strip()

with open(SQL_FILE, 'w', encoding='utf-8') as f:
    f.write(sql_text)
print(f"[10] Arquivo SQL salvo em: {SQL_FILE}")

# -------------------------
# 7) EXECUTAR AS CONSULTAS NO SQLITE E SALVAR RESULTADOS
# -------------------------

# Q1
q1 = "SELECT Produto, Categoria, SUM(Quantidade * Preco) AS total_vendas FROM vendas GROUP BY Produto, Categoria ORDER BY total_vendas DESC;"
q1_df = pd.read_sql_query(q1, conn)
q1_df.to_csv(SQL_Q1_RESULT, index=False, encoding='utf-8')
print(f"[11] Resultado SQL Q1 salvo em: {SQL_Q1_RESULT}")

# Q2 (SQLite version for June 2024)
q2 = "SELECT Produto, Categoria, SUM(Quantidade * Preco) AS total_vendas FROM vendas WHERE strftime('%m', Data) = '06' AND strftime('%Y', Data) = '2024' GROUP BY Produto, Categoria ORDER BY total_vendas ASC;"
q2_df = pd.read_sql_query(q2, conn)
q2_df.to_csv(SQL_Q2_RESULT, index=False, encoding='utf-8')
print(f"[12] Resultado SQL Q2 salvo em: {SQL_Q2_RESULT} (provavelmente vazio, pois não há dados 2024)")

conn.close()

# -------------------------
# 8) GERAR RELATÓRIO RESUMO (<=300 palavras)
# -------------------------

# Construir insights automáticos baseados nos resultados simulados:
# Insight 1: produto com maior venda
# Insight 2: mês com maior venda
month_total = df_monthly.sum()
best_month_idx = df_monthly.idxmax()
best_month_val = df_monthly.max()
worst_month_idx = df_monthly.idxmin()
worst_month_val = df_monthly.min()

insight_lines = []
insight_lines.append(f"- Produto com maior faturamento: **{top_product}** (R$ {top_product_val:.2f}).")
insight_lines.append(f"- Mês com maior faturamento: **{best_month_idx.strftime('%B %Y')}** (R$ {best_month_val:.2f}).")
insight_lines.append(f"- Mês com menor faturamento: **{worst_month_idx.strftime('%B %Y')}** (R$ {worst_month_val:.2f}).")

# Sugestões de ação (baseadas em padrões simples)
suggestions = [
    f"1) Reforçar estoque do produto {top_product} e analisar estratégias de promoção para produtos com baixa participação.",
    "2) Investigar sazonalidade: verificar causas do pico (promoções, sazonalidade) em meses de maior venda e replicar estratégias.",
    "3) Monitorar categorias com menor share e avaliar bundles ou cross-sell para aumentar ticket médio."
]

# Montar texto do relatório (máximo 300 palavras)
report_text = textwrap.dedent(f"""
# Relatório de Insights — Teste Analytics (simulação)

Resumo rápido:
{' '.join(insight_lines)}

Principais insights:
1. Produto campeão de vendas: {top_product} (R$ {top_product_val:.2f}), responsável por grande parcela do faturamento por produto.
2. Observa-se sazonalidade ao longo de 2023: pico em {best_month_idx.strftime('%B %Y')} e menor desempenho em {worst_month_idx.strftime('%B %Y')}. Isso indica oportunidades de ações promocionais em meses fracos.

Recomendações práticas:
- {suggestions[0]}
- {suggestions[1]}
- {suggestions[2]}

Observações metodológicas:
- Dataset simulado com período 01/01/2023 a 31/12/2023. Por isso, a consulta pedida para junho de 2024 retornará vazio; incluí no arquivo `sql/consultas_sql.sql` tanto a versão padrão quanto a específica para SQLite.
- Todos os códigos, gráficos (.png) e arquivos CSV gerados foram salvos nas pastas `data/`, `outputs/`, `sql/` e `docs/`.

(Esse relatório é curto e objetivo para facilitar apresentação oral — se desejar, posso convertê-lo para PDF automaticamente.)
""").strip()

# Garantir menos de 300 palavras: contar palavras
word_count = len(report_text.split())
if word_count > 300:
    # Truncar (raro, mas por segurança)
    words = report_text.split()[:300]
    report_text = ' '.join(words)
    report_text += "\n\n*Relatório truncado para 300 palavras.*"

with open(REPORT_MD, 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"[13] Relatório resumido salvo em: {REPORT_MD}  (palavras: {word_count})")

# -------------------------
# 9) MENSAGEM FINAL (como executar / próximos passos)
# -------------------------
final_message = f"""
Execução concluída ✅

Arquivos gerados:
- Raw CSV: {RAW_CSV}
- Clean CSV: {CLEAN_CSV}
- Vendas por produto: {SALES_BY_PRODUCT_CSV}
- Banco SQLite: {DB_PATH}
- SQL: {SQL_FILE}
- Resultados das consultas: {SQL_Q1_RESULT}, {SQL_Q2_RESULT}
- Gráficos: {PLOT_MONTHLY}, {PLOT_TOP_PRODUCTS}, {PLOT_CATEGORY}
- Relatório: {REPORT_MD}

Como rodar localmente:
1) Instale dependências:
   pip install pandas numpy matplotlib

2) Execute:
   python3 {os.path.basename(__file__)}

Observação importante:
- O dataset foi simulado apenas para 2023 (conforme enunciado). A consulta sobre junho/2024 está incluída no arquivo SQL, mas retornará vazio no banco atual.
"""
print(final_message)
