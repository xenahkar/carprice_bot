import asyncio
import logging
from config_reader import config

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from texts import helptext, starttext, canceltext1, canceltext2, errortext1, errortext2, misunderstandtext, zerorates
from keyboards import markup_fuel, markup_seller, markup_transmission, markup_owner, markup_rate

import boto3
import json
from private_key import s3_access_key, s3_secret_key, BUCKET

s3 = boto3.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())
# Диспетчер
dp = Dispatcher()

# Создаем словарик как "базу данных"
user_dict = {}


# Создаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_car_name = State()  # Состояние ожидания ввода названия машины
    fill_year = State()  # Состояние ожидания ввода года выпуска
    fill_km_driven = State()  # Состояние ожидания ввода пробега
    fill_fuel = State()  # Состояние ожидания выбора типа топлива
    fill_seller_type = State()  # Состояние ожидания выбора типа продавца
    fill_transmission = State()  # Состояние ожидания выбора коробки передач
    fill_owner = State()  # Состояние ожидания выбора количества владельцев
    fill_mileage = State()  # Состояние ожидания ввода расхода топлива автомобиля
    fill_engine = State()  # Состояние ожидания ввода объема двигателя
    fill_max_power = State()   # Состояние ожидания ввода максимальной мощности
    fill_seats = State()  # Состояние ожидания ввода количества сидений


# Хэндлер на команду /start
@dp.message(Command("start"), StateFilter(default_state))
async def cmd_start(message: types.Message):
    await message.answer(f'{message.from_user.full_name}, привет! 👋\n')
    await message.answer(text=starttext)


# Хэндлер на команду /help
@dp.message(Command('help'), StateFilter(default_state))
async def cmd_help(message: types.Message):
    await message.answer(text='Список возможных команд:')
    await message.answer(text=helptext)


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def cmd_cancel(message: Message):
    await message.answer(
        text=canceltext1
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def cmd_cancel_state(message: Message, state: FSMContext):
    await message.answer(
        text=canceltext2
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода названия машины
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def cmd_fillform(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите название машины на английском')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_car_name)


# Этот хэндлер будет срабатывать, если введено корректное название
# и переводить в состояние ожидания ввода года выпуска
@dp.message(StateFilter(FSMFillForm.fill_car_name), F.text.isascii())
async def process_name_sent(message: Message, state: FSMContext):
    # Сохраняем введенное название
    await state.update_data(name=message.text)
    await message.answer(text='Введите год выпуска автомобиля')
    # Устанавливаем состояние ожидания ввода года выпуска
    await state.set_state(FSMFillForm.fill_year)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_car_name))
async def warning_not_name(message: Message):
    await message.answer(
        text=errortext1
    )


# Этот хэндлер будет срабатывать, если введен корректный год выпуска
# и переводить в состояние ввода пробега
@dp.message(StateFilter(FSMFillForm.fill_year),
            lambda x: x.text.isdigit() and 1950 <= int(x.text) <= 2024)
async def process_year_sent(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer(text='Введите пробег автомобиля (км)')
    # Устанавливаем состояние ожидания ввода пробега
    await state.set_state(FSMFillForm.fill_km_driven)


# Этот хэндлер будет срабатывать, если во время ввода года выпуска
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_year))
async def warning_not_year(message: Message):
    await message.answer(
        text=errortext1
    )


# Этот хэндлер будет срабатывать, если введен корректный пробег
@dp.message(StateFilter(FSMFillForm.fill_km_driven),
            lambda x: x.text.isdigit() and int(x.text) >= 0)
async def process_km_driven_sent(message: Message, state: FSMContext):
    # Сохраняем пробег в хранилище по ключу "km_driven"
    await state.update_data(km_driven=message.text)
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Укажите тип топлива',
        reply_markup=markup_fuel
    )
    # Устанавливаем состояние ожидания выбора типа топлива автомобиля
    await state.set_state(FSMFillForm.fill_fuel)


# Этот хэндлер будет срабатывать, если во время ввода пробега
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_km_driven))
async def warning_not_km_driven(message: Message):
    await message.answer(
        text=errortext1
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе типа топлива и переводить в состояние выбора типа продавца
@dp.callback_query(StateFilter(FSMFillForm.fill_fuel),
                   F.data.in_(['Diesel', 'Petrol']))
async def process_fuel(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fuel=callback.data)
    await callback.message.answer(text=f'Вы выбрали значение: {callback.data}')
    await callback.message.answer(
        text='Выберите, кто продает автомобиль',
        reply_markup=markup_seller
    )
    # Устанавливаем состояние выбора продавца
    await state.set_state(FSMFillForm.fill_seller_type)


# Этот хэндлер будет срабатывать, если во время выбора типа топлива
# будет отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_fuel))
async def warning_not_fuel(message: Message):
    await message.answer(
        text=errortext2
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при выборе типа продавца
@dp.callback_query(StateFilter(FSMFillForm.fill_seller_type),
                   F.data.in_(['Individual', 'Dealer']))
async def process_seller_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(seller=callback.data)
    await callback.message.answer(text=f'Вы выбрали значение: {callback.data}')
    await callback.message.answer(
        text='Выберите коробку передач',
        reply_markup=markup_transmission
    )
    # Устанавливаем состояние выбора коробки передач
    await state.set_state(FSMFillForm.fill_transmission)


# Этот хэндлер будет срабатывать, если во время выбора продавца
# будет отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_seller_type))
async def warning_not_seller(message: Message):
    await message.answer(
        text=errortext2
    )


# Этот хэндлер будет срабатывать на нажатие кнопки выбора коробки передач
@dp.callback_query(StateFilter(FSMFillForm.fill_transmission),
                   F.data.in_(['Manual', 'Automatic']))
async def process_transmission(callback: CallbackQuery, state: FSMContext):
    await state.update_data(transmission=callback.data)
    await callback.message.answer(text=f'Вы выбрали значение: {callback.data}')
    await callback.message.answer(
        text='Выберите, сколько владельцев было у автомобиля',
        reply_markup=markup_owner
    )
    # Устанавливаем состояние выбора владельцев
    await state.set_state(FSMFillForm.fill_owner)


# Этот хэндлер будет срабатывать, если во время выбора коробки передач
# будет отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_transmission))
async def warning_not_transmission(message: Message):
    await message.answer(
        text=errortext2
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при количества владельцев
@dp.callback_query(StateFilter(FSMFillForm.fill_owner),
                   F.data.in_(['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner']))
async def process_owner(callback: CallbackQuery, state: FSMContext):
    await state.update_data(owner=callback.data)
    await callback.message.answer(text=f'Вы выбрали значение: {callback.data}')
    await callback.message.answer(text='Ввведите расход топлива (км за один литр)')
    # Устанавливаем состояние выбора
    await state.set_state(FSMFillForm.fill_mileage)


# Этот хэндлер будет срабатывать, если во время выбора количества владельцев
# будет отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_owner))
async def warning_not_owner(message: Message):
    await message.answer(
        text=errortext2
    )


# Этот хэндлер будет срабатывать, если введен расход топлива
@dp.message(StateFilter(FSMFillForm.fill_mileage),
            lambda x: float(x.text) >= 0)
async def process_year_sent(message: Message, state: FSMContext):
    # Cохраняем в хранилище по ключу "mileage"
    await state.update_data(mileage=message.text)
    await message.answer(text='Введите объем двигателя (кубические см)')
    # Устанавливаем состояние ожидания ввода объема двигателя
    await state.set_state(FSMFillForm.fill_engine)


# Этот хэндлер будет срабатывать, если во время ввода
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_mileage))
async def warning_not_mileage(message: Message):
    await message.answer(
        text=errortext1
    )


# Этот хэндлер будет срабатывать, если введен корректный объем двигателя
@dp.message(StateFilter(FSMFillForm.fill_engine),
            lambda x: float(x.text) >= 0)
async def process_year_sent(message: Message, state: FSMContext):
    await state.update_data(engine=message.text)
    # Добавляем в "базу данных" заполненную форму по ключу id пользователя
    user_dict[message.from_user.id] = await state.get_data()
    # Завершаем "машину состояний"
    await state.clear()
    await message.answer(text='Спасибо!\n\nЗаполнение формы закончено.\n\nВаши данные сохранены!')
    await message.answer(
        text='Чтобы посмотреть данные автомобиля - отправьте команду /showdata'
    )


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные об автомобиле или сообщение об отсутствии данных
@dp.message(Command(commands='showdata'), StateFilter(default_state))
async def cmd_showdata(message: Message):
    # Отправляем пользователю данные об автомобиле, если она заполнена
    if message.from_user.id in user_dict:
        car_info = f'Название: {user_dict[message.from_user.id]["name"]}\n' \
                   f'Год выпуска: {user_dict[message.from_user.id]["year"]}\n' \
                   f'Пробег: {user_dict[message.from_user.id]["km_driven"]}\n' \
                   f'Тип топлива: {user_dict[message.from_user.id]["fuel"]}\n' \
                   f'Тип продавца: {user_dict[message.from_user.id]["seller"]}\n' \
                   f'Тип коробки передач: {user_dict[message.from_user.id]["transmission"]}\n' \
                   f'Количество владельцев: {user_dict[message.from_user.id]["owner"]}\n' \
                   f'Тип продавца: {user_dict[message.from_user.id]["seller"]}\n' \
                   f'Расход топлива: {user_dict[message.from_user.id]["mileage"]}\n' \
                   f'Объем двигателя: {user_dict[message.from_user.id]["engine"]}' \
                   f'{user_dict[message.from_user.id]}'


        await message.answer(text=car_info)
    else:
        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
                 'отправьте команду /fillform'
        )


# Этот хэндлер будет срабатывать на отправку команды /rate
@dp.message(Command(commands='rate'), StateFilter(default_state))
async def cmd_rate(message: Message):
    await message.answer(
        text='Поставьте оценку этому боту:',
        reply_markup=markup_rate
    )


# Этот хэндлер будет срабатывать, если пользователь поставил оценку
@dp.callback_query(F.data.in_(['0', '1']))
async def process_rate(callback: CallbackQuery):
    await callback.message.answer(text=f'Благодарю за оценку!\n\nЯ зафиксировал её✍️')
    # json куда буду записывать оценки бота от пользователей
    rating_bot = json.loads(s3.get_object(Bucket=BUCKET, Key="rating_bot1.json").get('Body').read())
    # Записываю оценку
    rating_bot[callback.data] += 1
    # Сохраняю
    s3.put_object(Bucket=BUCKET, Key="rating_bot1.json", Body=json.dumps(rating_bot))


# Этот хэндлер будет срабатывать на отправку команды /statistic
@dp.message(Command(commands='statistic'), StateFilter(default_state))
async def cmd_statistic(message: Message):
    rating_bot = json.loads(s3.get_object(Bucket=BUCKET, Key="rating_bot1.json").get('Body').read())
    num_rates = sum([v for k, v in rating_bot.items()])
    if num_rates == 0:
        await message.answer(
            text=zerorates
        )
    else:
        rating_score = sum([int(k) * int(v) for k, v in rating_bot.items()]) / num_rates
        await message.answer(
            text=f'Рейтинг бота: {round(rating_score, 2)}\nКоличество оценок: {num_rates}'
        )


# Этот хэндлер будет срабатывать на отправку команды /predict
@dp.message(Command(commands='predict'), StateFilter(default_state))
async def cmd_predict(message: Message):
    await message.answer(
        text='✨Твоя машина бесценна!✨'
    )


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.answer(
        text=misunderstandtext
    )


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
