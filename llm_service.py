import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Инициализируем нового клиента. Он автоматически подтянет GEMINI_API_KEY из .env
client = genai.Client()

async def generate_welcome_book(fio: str, position: str, company_data: dict) -> str:
    # Определяем системную инструкцию
    system_instruction = (
        "Ты — автоматизированный HR-ассистент компании УМТО. Твоя задача — сгенерировать "
        "красивую, структурированную, вдохновляющую интерактивную 'Книгу приветствия' для нового сотрудника. "
        "Используй Markdown-разметку (жирный текст, списки, цитаты) для удобства чтения в Telegram.\n\n"
        "ПРАВИЛА:\n"
        "1. Не выдумывай имена директоров и контакты! Используй ТОЛЬКО те данные, которые предоставлены пользователем.\n"
        "2. Тон сообщения: профессиональный, строго под делу."
    )

    # Собираем пользовательский промпт
    user_prompt = f"""
    Данные нового сотрудника:
    - ФИО: {fio}
    - Должность: {position}
    
    Официальные данные из базы компании:
    - Компания: {company_data['company_name']}
    - Директор: {company_data['director']}
    - Отдел: {company_data['dept_full_name']}
    - Наставник в отделе: {company_data['mentor']}
    - Уполномоченный по этике: {company_data['ethics']}
    
    Сгенерируй ответ, содержащий следующие разделы:
    1. 🌟 Приветствие (обратись по имени-отчеству) и теплое слово от лица директора, не пиши в аутпуте само слово "приветствие" как отдельный раздел {company_data['director']}.
    2. 🏢 Твое место в структуре: кратко опиши значимость должности {position} в рамках отдела {company_data['dept_full_name']}.
    3. 🤝 Твоя команда поддержки: красиво оформи контакты наставника и уполномоченного по этике, объяснив к кому по каким вопросам обращаться.
    """

    # Получаем имя модели из .env, по умолчанию ставим актуальную gemini-2.0-flash
    model_name = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")

    try:
        # В новом SDK для асинхронности используется client.aio
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        return response.text
    except Exception as e:
        # Печатаем полную ошибку только в консоль сервера (скрыто от пользователя)
        print("\n" + "="*50)
        print(f"🔴 ОШИБКА GEMINI API: {e}")
        print("="*50 + "\n")
        
        # Пользователю в Telegram отдаем только безопасную заглушку
        return "❌ Произошла ошибка при генерации Книги приветствия. Пожалуйста, попробуйте позже."