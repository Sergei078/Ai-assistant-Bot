import asyncio
from aiogram import Dispatcher
from handler_user import router
import logging
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from dotenv import load_dotenv
from Telegram_Bot import bot
from aiogram.enums import ParseMode
from Buttons import menu_kb
from FSM import FSMFillForm
from Speechkit import speech_to_text, text_to_speech, is_stt_block_limit, stt_symbols_db_to_text
from database import CreateDatabase, TtsSymbolsInfo, TtsSymbolsAdd

load_dotenv()
administrators = [5586674988]
dp = Dispatcher()
logging.basicConfig(filename='errors.cod.log', level=logging.ERROR, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


@router.message(Command('log'))
async def logging_info(message: Message):
    user_id = message.chat.id
    if user_id in administrators:
        file = FSInputFile('errors.cod.log')
        await message.answer_document(file)


@dp.message(CommandStart())
async def start_command(message: Message):
    try:
        user_id = message.chat.id
        if user_id in administrators:
            create_db_user = CreateDatabase()
            if not await create_db_user.check_user_exists(message.chat.id):
                await create_db_user.add_user(message.chat.id)
            await create_db_user.close()
            await message.answer(f'<b>Привет, {message.chat.first_name}👋\n\n</b>'
                                 'Я твой голосовой\n'
                                 'AI ассистент.', parse_mode=ParseMode.HTML, reply_markup=menu_kb)
    except:
        await message.answer('Произошла неизвестная ошибка!')


@dp.message(Command('tts'))
async def text_input_command(message: Message, state: FSMContext):
    await state.set_state(FSMFillForm.tts_text)
    await message.answer('Введи свой текст:', reply_markup=ReplyKeyboardRemove())


@dp.message(FSMFillForm.tts_text)
async def generating_voice_messages_command(message: Message, state: FSMContext):
    try:
        await state.update_data(text=message.text)
        data = await state.get_data()
        tekens_control = len((data['text']))
        user_id = message.chat.id
        if tekens_control <= 150:
            info_tts = TtsSymbolsInfo()
            result_tts = await info_tts.tts_symbols_user(user_id)
            await info_tts.close()
            if result_tts is None or result_tts < 0:
                result_tts = 0
            if int(result_tts) is None or int(result_tts) > 0:
                await stt_symbols_db_to_text(user_id, data['text'])
                result = result_tts - tekens_control
                save_tokens = TtsSymbolsAdd()
                await save_tokens.add_tts_symbols(result, user_id)
                await save_tokens.close()
                await message.answer(f'Ожидай ответа⏳')
                result_text = await text_to_speech(data['text'])
                if result_text != 'При запросе возникла ошибка':
                    audio = FSInputFile('result_audio.ogg')
                    await message.answer_voice(audio, reply_markup=menu_kb)
                else:
                    await message.answer('При запросе возникла ошибка!', reply_markup=menu_kb)
            else:
                await message.answer('<i>Символы закончились❗️</i>', parse_mode='html', reply_markup=menu_kb)
        else:
            await message.answer('<i>Вы превисили допускаемое\n'
                                 'значение❗️</i>', parse_mode='html', reply_markup=menu_kb)
    except:
        await message.answer('Произошла неизвестная ошибка!')
    finally:
        await state.clear()


@dp.message(Command('stt'))
async def voice_user_command(message: Message, state: FSMContext):
    await state.set_state(FSMFillForm.stt_text)
    await message.answer('Запиши голосовое', reply_markup=ReplyKeyboardRemove())


@dp.message(FSMFillForm.stt_text)
async def voice_message_user_command(message: Message, state: FSMContext):
    try:
        await state.update_data(voice=message.voice.file_id)
        data = await state.get_data()
        file_info = await bot.get_file(data['voice'])
        file = await bot.download_file(file_info.file_path)
        user_id = message.chat.id
        info_tts = TtsSymbolsInfo()
        result_tts = await info_tts.tts_symbols_user(user_id)
        await info_tts.close()
        if result_tts is None or result_tts < 0:
            result_tts = 0
        if int(result_tts) > 0:
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
                await stt_symbols_db_to_text(user_id, voice_speechkit)
                await message.answer(f'{voice_speechkit}.', parse_mode='html', reply_markup=menu_kb)
        else:
            await message.answer('Запросы закончились!', reply_markup=menu_kb)
    except:
        await message.answer('Произошла неизвестная ошибка!')
    finally:
        await state.clear()


async def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except Exception as e:
        logging.error(str(e))
