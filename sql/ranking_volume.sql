SELECT id_moeda, volume_24h, id_data 
FROM camada_ouro.fato_precos 
WHERE id_data = '2026-09-20'
ORDER BY volume_24h DESC;


