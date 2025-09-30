-- consultas_sql.sql

-- 1. Nome do produto, categoria e soma total de vendas
-- (Quantidade * Preço) para cada produto, ordenado em ordem decrescente
SELECT
Produto,
Categoria,
SUM(Quantidade * Preco) AS Total_Vendas
FROM vendas
GROUP BY Produto, Categoria
ORDER BY Total_Vendas DESC;

-- 2. Produtos que venderam menos no mês de junho de 2024
-- Observação: dataset simulado cobre apenas 2023,
-- portanto, esta consulta não retornará registros.
SELECT
Produto,
Categoria,
SUM(Quantidade * Preco) AS Vendas_Junho_2024
FROM vendas
WHERE strftime('%Y-%m', Data) = '2024-06'
GROUP BY Produto, Categoria
ORDER BY Vendas_Junho_2024 ASC;
