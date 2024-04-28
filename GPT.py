import requests
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('IAM_TOKEN')

folder_id = os.getenv('FOLDER_ID')


async def promt_gpt(text):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.8,
            "maxTokens": 50
        },
        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }
    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)
    if response.status_code == 200:
        text = response.json()["result"]["alternatives"][0]["message"]["text"]
        return text
    else:
        return 'Ошибка'
