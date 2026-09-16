import os 
import json 
from datetime import datetime
import time


from requests.exceptions import RequestException
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import requests 
from dotenv import load_dotenv

# Loading environment variables from the .env file
load_dotenv()

api_key = os.getenv("COINGECKO_API_KEY")
bucket_name = os.getenv("AWS_BUCKET_NAME")
S3_PREFIX =  "bronze"

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



# making a request to the server
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

# In this block, we extract the data containing the date and upload it to s3.
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"crypto_prices_{timestamp}.json"


def upload_to_s3(data, filename):
    
    s3 = boto3.client('s3')
    s3_key = f"{S3_PREFIX}/{filename}"

    print(f"Starting upload  files to S3 (bucket: {bucket_name}).....")

    try:
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
        
    print("Upload concluído: s3://{bucket_name}/{s3_key}")


upload_to_s3(data, filename)