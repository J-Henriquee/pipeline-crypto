SELECT id_moeda, id_data, preco_brl, volume_24h, market_cap
FROM camada_ouro.fato_precos
WHERE id_moeda IN ('bitcoin', 'ethereum', 'solana', 'chainlink', 'cardano')
ORDER BY id_moeda, id_data DESC;