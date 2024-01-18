from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаем клавиатуру типа топлива
keyboard_fuel = [
    [InlineKeyboardButton(text="Дизель", callback_data='Diesel'),
     InlineKeyboardButton(text="Бензин", callback_data='Petrol')]
]
markup_fuel = InlineKeyboardMarkup(inline_keyboard=keyboard_fuel)

# Создаем клавиатуру продавца
keyboard_seller = [
    [InlineKeyboardButton(text="Дилер", callback_data='Dealer'),
     InlineKeyboardButton(text="Собственник", callback_data='Individual')]
]
markup_seller = InlineKeyboardMarkup(inline_keyboard=keyboard_seller)

# Создаем клавиатуру коробки передач
keyboard_transmission = [
    [InlineKeyboardButton(text="Механика", callback_data='Manual'),
     InlineKeyboardButton(text="Автомат", callback_data='Automatic')]
]
markup_transmission = InlineKeyboardMarkup(inline_keyboard=keyboard_transmission)

# Создаем клавиатуру количества владельцев
keyboard_owner = [
    [InlineKeyboardButton(text="1", callback_data='First Owner'),
     InlineKeyboardButton(text="2", callback_data='Second Owner'),
     InlineKeyboardButton(text="3", callback_data='Third Owner'),
     InlineKeyboardButton(text="4+", callback_data='Fourth & Above Owner')]
]
markup_owner = InlineKeyboardMarkup(inline_keyboard=keyboard_owner)

keyboard_rate = [
    [InlineKeyboardButton(text="👍", callback_data='1'),
     InlineKeyboardButton(text="👎", callback_data='0')]
]
markup_rate = InlineKeyboardMarkup(inline_keyboard=keyboard_rate)

