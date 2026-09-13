import os 
import json 
from datetime import datetime
import time
from requests.exceptions import RequestException 

import requests 
from dotenv import load_dotenv



os.makedirs("data/bronze", exist_ok=True)

# Loading environment variables from the .env file
load_dotenv()

api_key = os.getenv("COINGECKO_API_KEY")

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

# In this block, we extract the data containing the date and save it to a JSON file.
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"crypto_prices_{timestamp}.json"

caminho_completo = os.path.join("data/bronze", filename)

with open(caminho_completo, 'w') as crypto_file:
    json.dump(data, crypto_file)



