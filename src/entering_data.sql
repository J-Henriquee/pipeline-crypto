-- 1. Staging: espelho exato do que existe no Parquet
DROP TABLE IF EXISTS camada_ouro.stg_precos;

CREATE TABLE camada_ouro.stg_precos (
    coin_id VARCHAR,
    brl DOUBLE PRECISION,
    brl_market_cap DOUBLE PRECISION,
    brl_24h_vol DOUBLE PRECISION
);

-- 2. COPY do S3
COPY camada_ouro.stg_precos
FROM 's3://aws-crypto-bucket-nean/silver/precos_cripto/'
IAM_ROLE ''
FORMAT AS PARQUET;

-- 3. Popula dim_moeda (só id_moeda, é tudo que existe)
INSERT INTO camada_ouro.dim_moeda (id_moeda)
SELECT DISTINCT coin_id
FROM camada_ouro.stg_precos
WHERE coin_id NOT IN (SELECT id_moeda FROM camada_ouro.dim_moeda);

-- 4. Popula dim_data
INSERT INTO camada_ouro.dim_data (id_data, ano, mes, dia)
SELECT DISTINCT
    CURRENT_DATE,
    EXTRACT(YEAR FROM CURRENT_DATE),
    EXTRACT(MONTH FROM CURRENT_DATE),
    EXTRACT(DAY FROM CURRENT_DATE)
WHERE CURRENT_DATE NOT IN (SELECT id_data FROM camada_ouro.dim_data);

-- 5. Popula fato_precos
INSERT INTO camada_ouro.fato_precos (id_moeda, id_data, preco_brl, volume_24h, market_cap)
SELECT coin_id, CURRENT_DATE, brl, brl_24h_vol, brl_market_cap
FROM camada_ouro.stg_precos;