from aiogram.fsm.state import StatesGroup, State


class FSMFillForm(StatesGroup):
    voice_message = State()
    text_message = State()
    tts_text = State()
    stt_text = State()
