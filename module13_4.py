from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

api = "TOKEN"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.')

@dp.message_handler(lambda message: message.text.lower() == 'calories')
async def set_age(message: types.Message):
    await UserState.age.set()
    await message.answer('Введите свой возраст:')

@dp.message_handler(state= UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age= message.text)
    await UserState.growth.set()
    await message.answer('Введите свой рост (в см):')

@dp.message_handler(state= UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth= message.text)
    await UserState.weight.set()
    await message.answer('Введите свой вес (в кг):')

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f'Ваша ежедневная норма калорий: {calories:.2f} калорий.')

    await state.finish()

@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

