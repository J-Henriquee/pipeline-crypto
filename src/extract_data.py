import os
import json
from datetime import datetime
import time

from requests.exceptions import RequestException
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env — só usado para a API key do CoinGecko.
# Credenciais AWS não passam por aqui: a EC2 já tem uma IAM Role anexada,
# então o boto3 pega as credenciais automaticamente do metadata da instância.
load_dotenv()

api_key = os.getenv("COINGECKO_API_KEY")
bucket_name = os.getenv("AWS_BUCKET_NAME")
S3_PREFIX = "bronze"

url = "https://api.coingecko.com/api/v3/simple/price"

headers = {
    "x-cg-demo-api-key": api_key
}

params = {
    "vs_currencies": "brl",
    "ids": "bitcoin,ethereum,solana,cardano,chainlink",
    "include_market_cap": "true",
    "include_24hr_vol": "true"
}

# Loop de retry com dois tratamentos distintos, porque são falhas de natureza diferente:
# - 429 (rate limit): a API está dizendo "você já pediu demais". Insistir rápido
#   piora o problema, então o backoff cresce a cada tentativa (5s, 10s, 20s).
# - Falha de rede genérica: internet oscilou. Espera fixa de 5s é suficiente.
# A ordem dos "except" importa: HTTPError é subclasse de RequestException, então
# ele precisa vir primeiro, senão o except genérico captura tudo antes de chegar
# no tratamento específico do 429.
for attempt in range(3):
    try:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()

        print("A requisição foi bem sucedida")
        data = r.json()
        break

    except requests.exceptions.HTTPError as e:
        if r.status_code == 429:
            if attempt == 2:
                raise Exception(f"Limite de requisições excedido após 3 tentativas. Erro original: {e}")

            sleep_time = 5 * (2 ** attempt)
            print(f"Rate limit atingido (429). Tentando novamente em {sleep_time} segundos...")
            time.sleep(sleep_time)
        else:
            raise Exception(f"Erro HTTP inesperado: {e}")

    except requests.exceptions.RequestException as e:
        if attempt == 2:
            raise Exception(f"Falha de conexão após 3 tentativas. Erro original: {e}")

        print("Falha de rede. Tentando novamente em 5 segundos...")
        time.sleep(5)

# Nome do arquivo com timestamp — vira a chave (Key) do objeto no S3,
# não um arquivo físico: o container é efêmero e nada é salvo em disco.
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"crypto_prices_{timestamp}.json"


def upload_to_s3(data, filename):
    # Cliente sem credenciais explícitas: o boto3 resolve sozinho via IAM Role
    # quando rodando dentro da EC2.
    s3 = boto3.client('s3')
    s3_key = f"{S3_PREFIX}/{filename}"

    print(f"Starting upload files to S3 (bucket: {bucket_name}).....")

    try:
        # put_object envia bytes/string direto da memória (via json.dumps),
        # ao contrário de upload_file, que exigiria um arquivo em disco.
        # Isso evita qualquer persistência local nesse container efêmero.
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(data)
        )
    except NoCredentialsError:
        print("Error: AWS credentials not found. Verifique se a IAM Role está anexada à instância.")
        return
    except ClientError as e:
        print(f"AWS error on file {filename}: {e})")
        return

    print(f"Upload concluído: s3://{bucket_name}/{s3_key}")


upload_to_s3(data, filename)