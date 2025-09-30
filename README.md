# Teste de Estagiário em Analytics — Quod 

Este repositório contém a solução completa do **Teste para Estagiário em Analytics**.
A implementação foi realizada em **Python 3.10**, utilizando bibliotecas como `pandas`, `numpy` e `matplotlib`.

---

# 📂 Estrutura do Repositório

```
Teste-Analytics-Jhennife-de-Souza-Vicente/
├── data/               # datasets simulados, limpos e resultados de queries
    -> dataset_raw.csv
    -> data_clean.csv
    -> sales_by_product.csv
    -> vendas.db
    -> sql_query1_results.csv
    -> sql_query2_results.csv


├── outputs/            # visualizações (gráficos)
   ->  monthly_sales_trend.png
   -> top_products_bar.png
   -> sales_by_category_pie.png

├──scripts/            # código principal
   -> teste_analytics.py
├── sql/                # consultas SQL
   -> consultas_sql.sql
├── docs/               # relatório final
   -> relatorio_insights.md
└── README.md           # arquivo md


## ⚙️ Como executar ?

1. Clone este repositório:

   ```bash
   git clone https://github.com/seuusuario/Teste-Analytics-Jhennife-de-Souza-Vicente.git
   cd Teste-Analytics-Jhennife-de-Souza-Vicente
   ```

2. Crie um ambiente virtual (opcional):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install pandas numpy matplotlib
   ```

4. Execute o script principal:

   ```bash
   python scripts/Teste-Analytics.py
   ```
   ---
## Consultas SQL

O arquivo **`consultas_sql.sql`** contém as queries solicitadas na Parte 2 do teste:

1. **Total de vendas por produto**: retorna o nome do produto, categoria e a soma total das vendas (Quantidade × Preço), ordenando do maior para o menor valor.
2. **Produtos com menor venda em junho/2024**: identifica os produtos com menor volume de vendas nesse mês.

   > Observação: como o dataset simulado cobre apenas o ano de 2023, essa consulta não retorna registros, mas foi implementada para demonstrar a lógica solicitada.

---

## 📊 O que é gerado

* Dataset **simulado** (`dataset_raw.csv`) com 120 registros de 01/01/2023 a 31/12/2023.
* Dataset **limpo** (`data_clean.csv`), após tratamento de duplicatas, valores faltantes e ajustes de tipo.
* Análises salvas em CSV (`sales_by_product.csv`) e banco SQLite (`vendas.db`).
* Gráficos em PNG na pasta `outputs/`.
* Consultas SQL no arquivo `consultas_sql.sql`.
* Relatório em Markdown (`relatorio_insights.md`) com resumo dos principais insights e recomendações.

---

## 📑 Observações

* O dataset cobre apenas **2023**. Por isso, a consulta referente a junho de 2024 foi escrita, mas retorna vazio na base atual.
* As análises são baseadas em dados simulados e podem variar a cada execução.
* O relatório final possui até 300 palavras, conforme instruções.

---

## 👩‍💻 Autor

Jhennife de Souza Vicente
Candidata à vaga de Estagiário em Analytics — Quod
