import telebot
from telebot import types
from config import TOKEN, ADMIN_ID
from database import (
    create_tables,
    add_user,
    update_user_phone,
    add_vacancy,
    get_all_vacancies,
    get_vacancy_by_id,
    get_vacancies_by_category,
    get_user
)
import re
import signal
import sys

def signal_handler(sig, frame):
    print("Бот завершает работу...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

bot = telebot.TeleBot(TOKEN)

user_states = {}

create_tables()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user:
        bot.send_message(message.chat.id, f'С возвращением, {user["name"]}!')
        show_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Привет! Давай зарегистрируемся.\nКак тебя зовут?')
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text
    user_id = message.from_user.id
    add_user(user_id, name)
    bot.send_message(message.chat.id, 'Теперь введи свой номер телефона (например, +996123456789):')
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    phone = message.text
    user_id = message.from_user.id
    update_user_phone(user_id, phone)
    bot.send_message(message.chat.id, '✅ Регистрация завершена! Добро пожаловать в бот.')
    show_main_menu(message.chat.id)

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📋 Вакансии'))

    if chat_id == ADMIN_ID:
        markup.add(types.KeyboardButton('➕ Добавить вакансию'))

    bot.send_message(chat_id, 'Выберите действие:', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id

    if user_id in user_states:
        if user_states[user_id] == 'waiting_for_vacancy_title':
            admin_add_title(message)
        elif user_states[user_id] == 'waiting_for_vacancy_description':
            admin_add_description(message)
        return

    if message.text == '📋 Вакансии':
        list_categories(message)
    elif message.text == '➕ Добавить вакансию' and message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, 'Введите название вакансии (или нажмите "Отмена"):', reply_markup=cancel_markup())
        user_states[user_id] = 'waiting_for_vacancy_title'
    elif message.text == '❌ Отмена':
        del user_states[user_id]
        show_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Не понял тебя. Выбери вариант из меню.')

def cancel_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('❌ Отмена'))
    return markup

def list_categories(message):
    categories = ['Курьер', 'Продавец', 'Водитель', 'Официант']
    markup = types.InlineKeyboardMarkup()

    for category in categories:
        button = types.InlineKeyboardButton(text=category, callback_data=f'category_{category}')
        markup.add(button)

    bot.send_message(message.chat.id, '📋 Выберите категорию вакансий:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '📋 Вакансии')
def handle_vacancies(message):
    list_categories(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def callback_category(call):
    category = call.data.split('_')[1]
    vacancies = get_vacancies_by_category(category)

    if vacancies:
        for vacancy_id, title, description, _ in vacancies:
            text = f"📝 <b>{title}</b>\n\n{description}"

            url_pattern = r'(https?://[^\s]+)'
            urls = re.findall(url_pattern, description)

            if urls:
                url = urls[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Подробнее", url=url))
                bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    text,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
    else:
        bot.send_message(call.message.chat.id, f'Вакансий для категории "{category}" нет.')

def admin_add_title(message):
    user_id = message.from_user.id

    if message.text == '❌ Отмена':
        del user_states[user_id]
        show_main_menu(message.chat.id)
        return

    title = message.text
    user_states[user_id] = 'waiting_for_vacancy_description'
    bot.send_message(message.chat.id, 'Введите описание вакансии (или нажмите "Отмена"):', reply_markup=cancel_markup())
    bot.register_next_step_handler(message, admin_add_description, title)

def admin_add_description(message, title):
    user_id = message.from_user.id

    if message.text == '❌ Отмена':
        del user_states[user_id]
        show_main_menu(message.chat.id)
        return

    description = message.text
    user_states[user_id] = 'waiting_for_vacancy_category'

    categories = ['Курьер', 'Продавец', 'Водитель', 'Официант']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(types.KeyboardButton(category))
    markup.add(types.KeyboardButton('❌ Отмена'))

    bot.send_message(message.chat.id, 'Выберите категорию вакансии:', reply_markup=markup)
    bot.register_next_step_handler(message, process_category_selection, title, description)

def process_category_selection(message, title, description):
    user_id = message.from_user.id

    if message.text == '❌ Отмена':
        del user_states[user_id]
        show_main_menu(message.chat.id)
        return

    category = message.text
    add_vacancy(title, description, category)
    bot.send_message(message.chat.id, '✅ Вакансия добавлена!')
    del user_states[user_id]
    show_main_menu(message.chat.id)


if __name__ == '__main__':
    bot.polling(none_stop=True)