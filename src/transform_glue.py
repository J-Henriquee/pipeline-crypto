"""
Job AWS Glue (Python Shell) - Camada Bronze para Silver
-------------------------------------------------------
Objetivo: Ler o último arquivo JSON bruto de preços de criptomoedas 
da camada Bronze no S3, achatar a estrutura aninhada, tratar nulos 
e converter para formato colunar (Parquet) particionado por data de extração.
"""

import boto3
import json
import pandas as pd
from datetime import datetime
import awswrangler as wr

def main():
    bucket_name = "aws-crypto-bucket-nean"
    cliente = boto3.client('s3')

    # 1. Busca os arquivos na Bronze e isola o mais recente
    objetos = cliente.list_objects_v2(Bucket=bucket_name, Prefix="bronze/")
    arquivos = objetos.get('Contents', [])
    
    if not arquivos:
        print("Nenhum arquivo encontrado na camada Bronze.")
        return

    caminho_ultimo_arquivo = arquivos[-1]['Key']
    print(f"Lendo arquivo: {caminho_ultimo_arquivo}")

    # 2. Carrega o JSON da rede direto para a memória
    response = cliente.get_object(Bucket=bucket_name, Key=caminho_ultimo_arquivo)
    conteudo_string = response['Body'].read().decode('utf-8')
    dados_brutos = json.loads(conteudo_string)

    # 3. Transformação com Pandas
    df = pd.DataFrame.from_dict(dados_brutos, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'coin_id'}, inplace=True)
    
    # Tratamento de nulos para evitar quebra de cálculos no Data Warehouse
    df.fillna(0, inplace=True)

    # Particionamento por dia para otimizar o I/O no Redshift (Partition Pruning)
    time_now = datetime.now().strftime("%Y-%m-%d")
    df["dt_extracao"] = time_now

    # 4. Carga na Silver no formato Parquet
    caminho_silver = f"s3://{bucket_name}/silver/precos_cripto/"
    wr.s3.to_parquet(
            df=df,
            path=caminho_silver,
            dataset=True,
            mode="overwrite_partitions", 
            partition_cols=['dt_extracao']
        )
    
    print(f"Sucesso! Dados processados e particionados em dt_extracao={time_now}")

if __name__ == "__main__":
    main()