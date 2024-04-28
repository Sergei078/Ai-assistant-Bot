from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv
from Telegram_Bot import bot
from aiogram.enums import ChatAction
from Buttons import menu_kb
from FSM import FSMFillForm
from Speechkit import speech_to_text, text_to_speech, is_stt_block_limit, stt_symbols_db_to_text
from GPT import promt_gpt
from database import TotalGptTokensAdd, TotalGptTokensInfo, TtsSymbolsInfo, MessageInfo
from Tokenizer import count_tokens

load_dotenv()
router = Router()


@router.message(F.text == 'Голосовое общение🗣')
async def voice_input_message(message: Message, state: FSMContext):
    await state.set_state(FSMFillForm.voice_message)
    await message.answer('Запиши голосовое \n'
                         'с вопросом.', reply_markup=ReplyKeyboardRemove())


@router.message(FSMFillForm.voice_message)
async def voice_message_handler_message(message: Message, state: FSMContext):
    try:
        await state.update_data(voice=message.voice.file_id)
        data = await state.get_data()
        user_id = message.chat.id
        info_tokens = TotalGptTokensInfo()
        result_tokens = await info_tokens.total_gpt_tokens_user(user_id)
        await info_tokens.close()
        info_tts = TtsSymbolsInfo()
        result_tts = await info_tts.tts_symbols_user(user_id)
        await info_tokens.close()
        if result_tokens is None or result_tokens < 0:
            result_tokens = 0
        if result_tts is None or result_tts < 0:
            result_tts = 0
        if int(result_tokens) > 0 and int(result_tts) > 0:
            sender = ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                action=ChatAction.UPLOAD_VOICE,
            )
            async with sender:
                file_info = await bot.get_file(data['voice'])
                file = await bot.download_file(file_info.file_path)
                with open('user_voice.ogg', 'wb') as f:
                    f.write(file.read())
                duration_user = message.voice.duration
                result_info = await is_stt_block_limit(user_id=user_id, duration=duration_user)
                if result_info == 'Превышено длительность голосового сообщения' or result_info == 'Превышен лимит для пользователя':
                    await message.answer(result_info, reply_markup=menu_kb)
                else:
                    with open('user_voice.ogg', 'rb') as audio_file:
                        audio_data = audio_file.read()
                    voice_speechkit = await speech_to_text(audio_data)
                    if voice_speechkit != 'При запросе возникла ошибка':
                        gpt_response = await promt_gpt(voice_speechkit)
                        if gpt_response != 'Ошибка':
                            tokenizer = await count_tokens(voice_speechkit + gpt_response)
                            save_tokens = TotalGptTokensAdd()
                            await save_tokens.add_total_gpt_tokens(result_tokens - tokenizer, user_id)
                            await save_tokens.close()
                            result_text = await text_to_speech(gpt_response)
                            if result_text != 'При запросе возникла ошибка':
                                audio = FSInputFile('result_audio.ogg')
                                await stt_symbols_db_to_text(user_id, voice_speechkit)
                                await stt_symbols_db_to_text(user_id, gpt_response)
                                await message.answer_voice(audio, reply_markup=menu_kb)
                            else:
                                await message.answer('При запросе возникла ошибка!', reply_markup=menu_kb)
                        else:
                            await message.answer('Произошла ошибка в \n'
                                                 'нейросети!', reply_markup=menu_kb)
                    else:
                        await message.answer('При запросе возникла ошибка!', reply_markup=menu_kb)
        else:
            await message.answer('Запросы закончились!', reply_markup=menu_kb)
    except:
        await message.answer('Произошла неизвестная ошибка!')
    finally:
        await state.clear()


@router.message(F.text == 'Текстовое общение📝')
async def text_input_message(message: Message, state: FSMContext):
    await state.set_state(FSMFillForm.text_message)
    await message.answer('Напиши текст\n'
                         'со вопросом.', reply_markup=ReplyKeyboardRemove())


@router.message(FSMFillForm.text_message)
async def text_message_handler_message(message: Message, state: FSMContext):
    try:
        await state.update_data(text=message.text)
        data = await state.get_data()
        user_id = message.chat.id
        info_tokens = TotalGptTokensInfo()
        result_tokens = await info_tokens.total_gpt_tokens_user(user_id)
        await info_tokens.close()
        if result_tokens is None or result_tokens < 0:
            result_tokens = 0
        if int(result_tokens) > 0:
            gpt_response = await promt_gpt(data['text'])
            if gpt_response != 'Ошибка':
                await message.answer(gpt_response, reply_markup=menu_kb)
                await stt_symbols_db_to_text(user_id, data['text'])
                await stt_symbols_db_to_text(user_id, gpt_response)
                tokenizer = await count_tokens(data['text'] + gpt_response)
                save_tokens = TotalGptTokensAdd()
                await save_tokens.add_total_gpt_tokens(result_tokens - tokenizer, user_id)
                await save_tokens.close()
            else:
                await message.answer('Произошла ошибка в \n'
                                     'нейросети!', reply_markup=menu_kb)
        else:
            await message.answer('Запросы закончились!', reply_markup=menu_kb)
    except:
        await message.answer('Произошла неизвестная ошибка!')
    finally:
        await state.clear()


@router.message(F.text == 'Вся переписка')
async def message_user_message(message: Message):
    try:
        user_id = message.chat.id
        text_db = MessageInfo()
        result_text = await text_db.select_message(user_id)
        await text_db.close()
        if result_text is None:
            await message.answer('Пусто')
        else:
            await message.answer(result_text)
    except:
        await message.answer('Произошла неизвестная ошибка!')
