import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
import db_service
import llm_service

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Описываем шаги опроса
class OnboardingForm(StatesGroup):
    waiting_for_fio = State()
    waiting_for_position = State()
    waiting_for_department = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("👋 Добро пожаловать в УМТО! Введите ваш **ФИО**:")
    await state.set_state(OnboardingForm.waiting_for_fio)

@dp.message(OnboardingForm.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Укажите вашу **Должность**:")
    await state.set_state(OnboardingForm.waiting_for_position)

@dp.message(OnboardingForm.waiting_for_position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("Укажите ваш **Отдел** (например: ИТ или Маркетинг):")
    await state.set_state(OnboardingForm.waiting_for_department)

@dp.message(OnboardingForm.waiting_for_department)
async def process_department(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dept_input = message.text
    
    # 1. Проверяем, есть ли такой отдел в нашей "базе"
    company_data = db_service.get_department_data(dept_input)
    
    if not company_data:
        await message.answer("⚠️ Такой отдел не найден в системе (попробуйте ввести 'ИТ' или 'Маркетинг'). Введите отдел заново:")
        return

    # Отправляем статус "печатает", так как ИИ отвечает не мгновенно
    await message.answer("⏳ Собираем данные, подождите пару секунд...")
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # 2. Генерируем пакет через LLM-сервис
    welcome_book_text = await llm_service.generate_welcome_book(
        fio=user_data['fio'],
        position=user_data['position'],
        company_data=company_data
    )

    # 3. Выдаем результат пользователю
    await message.answer(welcome_book_text, parse_mode="Markdown")
    
    # Сбрасываем состояние FSM
    await state.clear()

async def main():
    print("Бот успешно запущен в режиме Long Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())