import requests
import os
import math
from dotenv import load_dotenv
from database import TtsSymbolsInfo, TtsSymbolsAdd, SttBlocksAdd, SttBlocksInfo, MessageAdd, MessageInfo

load_dotenv()
token = os.getenv('IAM_TOKEN')
folder_id = os.getenv('FOLDER_ID')


async def speech_to_text(voice):
    params = "&".join([
        "topic=general",
        f"folderId={folder_id}",
        "lang=ru-RU"
    ])

    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.post(f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
                             headers=headers,
                             data=voice
                             )

    decoded_data = response.json()
    if decoded_data.get("error_code") is None:
        return decoded_data.get("result")
    else:
        return "При запросе возникла ошибка"


async def is_stt_block_limit(user_id, duration):
    audio_blocks = math.ceil(duration / 15)
    stt_user = SttBlocksInfo()
    result_stt = await stt_user.stt_blocks_user(user_id)
    await stt_user.close()
    if duration >= 30:
        return "Превышено длительность голосового сообщения"
    if result_stt >= 6:
        return f"Превышен лимит для пользователя"
    all_blocks = result_stt + audio_blocks
    voice_control_add_user = SttBlocksAdd()
    await voice_control_add_user.add_stt_blocks(all_blocks, user_id)
    await voice_control_add_user.close()


async def stt_symbols_db_to_text(user_id, text):
    info_db_tokens1 = TtsSymbolsInfo()
    tokens_db1 = await info_db_tokens1.tts_symbols_user(user_id)
    result = tokens_db1 - len(text)
    await info_db_tokens1.close()

    save_tokens = TtsSymbolsAdd()
    await save_tokens.add_tts_symbols(result, user_id)
    await save_tokens.close()

    text_db = MessageInfo()
    result_text = await text_db.select_message(user_id)
    await text_db.close()
    save_text = MessageAdd()
    if result_text is None:
        await save_text.add_message(text, user_id)
    else:
        await save_text.add_message(f'{result_text}\n\n' + text, user_id)
    await save_text.close()


async def text_to_speech(text):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': folder_id,
    }
    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)
    if response.status_code == 200:
        result = response.content
        with open('result_audio.ogg', 'wb') as f:
            f.write(result)
    else:
        return "При запросе возникла ошибка"
