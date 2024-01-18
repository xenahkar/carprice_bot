from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def keyboard_fuel() -> InlineKeyboardMarkup:
    # Создаем клавиатуру типа топлива
    kb_fuel = [
        [InlineKeyboardButton(text="Дизель", callback_data='Diesel'),
         InlineKeyboardButton(text="Бензин", callback_data='Petrol')]
    ]
    markup_fuel = InlineKeyboardMarkup(inline_keyboard=kb_fuel)
    return markup_fuel


def keyboard_seller() -> InlineKeyboardMarkup:
    # Создаем клавиатуру продавца
    kb_seller = [
        [InlineKeyboardButton(text="Дилер", callback_data='Dealer'),
         InlineKeyboardButton(text="Собственник", callback_data='Individual')]
    ]
    markup_seller = InlineKeyboardMarkup(inline_keyboard=kb_seller)
    return markup_seller


def keyboard_transmission() -> InlineKeyboardMarkup:
    # Создаем клавиатуру коробки передач
    kb_transmission = [
        [InlineKeyboardButton(text="Механика", callback_data='Manual'),
         InlineKeyboardButton(text="Автомат", callback_data='Automatic')]
    ]
    markup_transmission = InlineKeyboardMarkup(inline_keyboard=kb_transmission)
    return markup_transmission

def keyboard_owner() -> InlineKeyboardMarkup:
    # Создаем клавиатуру количества владельцев
    kb_owner = [
        [InlineKeyboardButton(text="1", callback_data='First Owner'),
         InlineKeyboardButton(text="2", callback_data='Second Owner'),
         InlineKeyboardButton(text="3", callback_data='Third Owner'),
         InlineKeyboardButton(text="4+", callback_data='Fourth & Above Owner')]
    ]
    markup_owner = InlineKeyboardMarkup(inline_keyboard=kb_owner)
    return markup_owner

def keyboard_rate() -> InlineKeyboardMarkup:
    # Создаем клавиатуру для оценки бота
    kb_rate = [
        [InlineKeyboardButton(text="👍", callback_data='1'),
         InlineKeyboardButton(text="👎", callback_data='0')]
    ]
    markup_rate = InlineKeyboardMarkup(inline_keyboard=kb_rate)
    return markup_rate



