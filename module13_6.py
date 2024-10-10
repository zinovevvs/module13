from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ["Рассчитать", "Информация"]
keyboard.add(*[types.KeyboardButton(button) for button in buttons])


inline_keyboard = types.InlineKeyboardMarkup()
inline_keyboard.add(types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'))
inline_keyboard.add(types.InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas'))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup= inline_keyboard)

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Формула Миффлина-Сан Жеора:\n\n"
                              "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                              "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161")

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.answer()
    await call.message.answer('Введите свой возраст:')

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await UserState.growth.set()
    await message.answer('Введите свой рост (в см):')

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
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

@dp.message_handler(lambda message: message.text == 'Информация')
async def info(message: types.Message):
    await message.answer('Это бот, который поможет вам рассчитать вашу норму калорий.')

@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer('Пожалуйста, используйте кнопки: "Рассчитать" или "Информация".')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

