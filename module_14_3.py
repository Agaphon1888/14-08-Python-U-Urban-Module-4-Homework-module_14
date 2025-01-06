# Домашнее задание по теме "Доработка бота".
# Задача "Витамины для всех!".

import hashlib
from aiogram import Bot, Dispatcher, executor, types  # Добавляем import для types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import API_TOKEN  # Импортируем токен из модуля config


# Хеширование токена
def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# Определяем состояния пользователя
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


# Создание клавиатур
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Рассчитать', 'Информация', 'Купить']
    keyboard.add(*[KeyboardButton(button) for button in buttons])
    return keyboard


def create_inline_keyboard():
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
        InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
    ]
    inline_keyboard.add(*buttons)
    return inline_keyboard


def create_buy_keyboard():
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    products = ["Вода мёртвая", "Вода живая", "Яблочко молодильное", "Подорожник"]
    buttons = [InlineKeyboardButton(f'Купить {product}', callback_data=f'buy_{product}') for product in products]
    inline_keyboard.add(*buttons)
    return inline_keyboard


def create_gender_keyboard():
    gender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    gender_keyboard.add(
        KeyboardButton("Мужской"),
        KeyboardButton("Женский")
    )
    return gender_keyboard


main_keyboard = create_main_keyboard()
inline_keyboard = create_inline_keyboard()
buy_keyboard = create_buy_keyboard()
gender_keyboard = create_gender_keyboard()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я - бот, помогающий твоему здоровью.", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formulas_text = (
        "Формулы расчета нормы калорий:\n"
        "- Для мужчин: K = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
        "- Для женщин: K = 10 * вес + 6.25 * рост - 5 * возраст - 161"
    )
    await bot.send_message(call.from_user.id, formulas_text)


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await bot.send_message(call.from_user.id, "Введите свой возраст:")


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст (число).")
        return
    await state.update_data(age=int(message.text))
    await UserState.growth.set()
    await message.answer("Введите свой рост в сантиметрах:")


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный рост (число).")
        return
    await state.update_data(growth=int(message.text))
    await UserState.weight.set()
    await message.answer("Введите свой вес в килограммах:")


@dp.message_handler(state=UserState.weight)
async def set_gender(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный вес (число).")
        return
    await state.update_data(weight=int(message.text))
    await UserState.gender.set()
    await message.answer("Выберите свой пол:", reply_markup=gender_keyboard)


@dp.message_handler(state=UserState.gender)
async def send_calories(message: types.Message, state: FSMContext):
    gender = message.text.strip().lower()
    if gender not in ["мужской", "женский"]:
        await message.answer("Пожалуйста, выберите пол, нажав на кнопку.")
        return

    user_data = await state.get_data()
    age = user_data.get('age')
    growth = user_data.get('growth')
    weight = user_data.get('weight')

    # Проверка на наличие всех необходимых данных
    if age is None or growth is None or weight is None:
        await message.answer("Ошибка в данных. Пожалуйста, введите все параметры заново.")
        await state.finish()  # Завершаем состояние
        return

    # Вычисляем норму калорий
    calories = (
            10 * weight +
            6.25 * growth -
            5 * age +
            (5 if gender == "мужской" else -161)
    )
    await message.answer(f"Ваша норма калорий: {calories:.2f} калорий в день.")
    await state.finish()  # Завершаем состояние

    # Возвращаем пользователя к главной клавиатуре
    await message.answer("Выберите опцию:", reply_markup=main_keyboard)

    await state.finish()  # Завершаем состояние


@dp.message_handler(lambda message: message.text == 'Информация')
async def info(message: types.Message):
    await message.answer("Это бот для расчёта вашей нормы калорий. Нажмите 'Рассчитать', чтобы начать!")


@dp.message_handler(lambda message: message.text == 'Купить')
async def get_buying_list(message: types.Message):
    products = [
        {"name": "Вода мёртвая", "description": "Сращивает", "price": 100, "image": "product1.png"},
        {"name": "Вода живая", "description": "Заживляет", "price": 200, "image": "product2.png"},
        {"name": "Яблочко молодильное", "description": "Омолаживает", "price": 300, "image": "product3.png"},
        {"name": "Подорожник", "description": "Универсальное средство", "price": 400, "image": "product4.png"}
    ]

    for product in products:
        buy_button = InlineKeyboardButton(f'Купить {product["name"]}', callback_data=f'buy_{product["name"]}')
        inline_keyboard = InlineKeyboardMarkup().add(buy_button)

        with open(product['image'], 'rb') as img:
            await bot.send_photo(
                message.chat.id,
                img,
                caption=f"{product['name']}\n{product['description']}\nЦена: {product['price']} \n\nНажмите на кнопку "
                        f"ниже, чтобы купить.",
                reply_markup=inline_keyboard
            )

    all_products_keyboard = InlineKeyboardMarkup(row_width=2)
    for product in products:
        all_products_keyboard.add(
            InlineKeyboardButton(f'Купить {product["name"]}', callback_data=f'buy_{product["name"]}'))

    await message.answer("Выберите товар, который хотите купить:", reply_markup=all_products_keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def process_buy_request(call: types.CallbackQuery):
    product_name = call.data.split('_', 1)[1]
    await bot.answer_callback_query(call.id, text=f"Вы выбрали: {product_name}. Спасибо за покупку!")


@dp.message_handler(lambda message: message.text not in ['Рассчитать', 'Информация', 'Купить'])
async def unknown_message(message: types.Message):
    await message.answer("Пожалуйста, выберите одну из доступных опций: 'Рассчитать', 'Информация', 'Купить'.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
