SELECT id_moeda, id_data, preco_brl, 
       LAG(preco_brl) OVER (PARTITION BY id_moeda ORDER BY id_data) AS preco_anterior,
       ROUND(
           (preco_brl - LAG(preco_brl) OVER (PARTITION BY id_moeda ORDER BY id_data))
           / NULLIF(LAG(preco_brl) OVER (PARTITION BY id_moeda ORDER BY id_data), 0)
       ) AS variação_percentual
       FROM camada_ouro.fato_precos
       ORDER BY id_data;