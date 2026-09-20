CREATE SCHEMA IF NOT EXISTS camada_ouro;

CREATE TABLE camada_ouro.dim_moeda (
    id_moeda VARCHAR PRIMARY KEY,
    nome_completo VARCHAR,
    simbolo VARCHAR
);

CREATE TABLE camada_ouro.dim_data (
    id_data DATE PRIMARY KEY,
    ano INTEGER, 
    mes INTEGER, 
    dia INTEGER 
);

CREATE TABLE camada_ouro.fato_precos (
    id_moeda VARCHAR REFERENCES camada_ouro.dim_moeda(id_moeda),
    id_data DATE REFERENCES camada_ouro.dim_data(id_data),
    preco_brl DOUBLE PRECISION,
    volume_24h DOUBLE PRECISION,
    market_cap DOUBLE PRECISION 
);



