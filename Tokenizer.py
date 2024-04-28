import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('IAM_TOKEN')

folder_id = os.getenv('FOLDER_ID')


async def count_tokens(text):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",
        "text": text
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    )
