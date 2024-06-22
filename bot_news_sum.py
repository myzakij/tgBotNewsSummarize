from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from model.summary import summarize_text
from utils.articles_parser import parse_names
from utils.text_parse import text_ria
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.builtin import CommandStart


API_TOKEN = 'YOUR API TOKEN'
START_URLS = {
    'science': 'https://ria.ru/services/science/more.html',
    'world': 'https://ria.ru/services/world/more.html',
    'culture': 'https://ria.ru/services/culture/more.html',
    'tourism': 'https://ria.ru/services/tourism/more.html'
}


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NavigationState(StatesGroup):
    navigating = State()


@dp.message_handler(CommandStart())
async def cmd_start_unrestricted(message: types.Message, state: FSMContext):
    await cmd_start(message)

# @dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Наука", callback_data="start_science"),
        InlineKeyboardButton("В мире", callback_data="start_world")
    )
    keyboard.add(
        InlineKeyboardButton("Культура", callback_data="start_culture"),
        InlineKeyboardButton("Туризм", callback_data="start_tourism")
    )
    await message.answer("<b>=====|Выберите тему|=====</b>", reply_markup=keyboard, parse_mode="HTML")

# Callback handlers for each theme
@dp.callback_query_handler(lambda c: c.data.startswith('start_'))
async def process_theme(callback_query: types.CallbackQuery):
    theme = callback_query.data.split('_')[-1]
    start_url = START_URLS.get(theme)
    if start_url:
        await NavigationState.navigating.set()
        await send_news(callback_query.message, start_url)
    else:
        await bot.answer_callback_query(callback_query.id, "Тема не найдена")

async def send_news(message, start_url):
    news = parse_names(start_url)
    articles = '\n'.join([f'{num}. {title}' for num, title, _ in news['articles']])
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    prev_button = types.InlineKeyboardButton('Предыдущая страница', callback_data='prev')
    next_button = types.InlineKeyboardButton('Следующая страница', callback_data='next')
    select_article_button = types.InlineKeyboardButton('Выбрать новость', callback_data='select_article')
    keyboard.add(prev_button, next_button, select_article_button)
    await message.answer(articles, reply_markup=keyboard)

# Обработчик обратных вызовов для кнопок "Предыдущая страница" и "Следующая страница"
@dp.callback_query_handler(lambda c: c.data == 'prev' or c.data == 'next', state=NavigationState.navigating)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        current_page_index = data.get('current_page_index', 0)
        pages = data.get('pages', [START_URLS['science']])

        # Обработка нажатия кнопки "Предыдущая страница"
        if callback_query.data == 'prev':
            if current_page_index > 0:
                current_page_index -= 1
                print(current_page_index)
                news = parse_names(pages[current_page_index])
                articles = '\n'.join([f'{num}. {title}' for num, title, _ in news['articles']])
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                prev_button = types.InlineKeyboardButton('Предыдущая страница', callback_data='prev')
                next_button = types.InlineKeyboardButton('Следующая страница', callback_data='next')
                select_article_button = types.InlineKeyboardButton('Выбрать новость', callback_data='select_article')
                keyboard.add(prev_button, next_button, select_article_button)
                await bot.edit_message_text(
                    text=articles,
                    chat_id=callback_query.from_user.id,
                    message_id=callback_query.message.message_id,
                    reply_markup=keyboard 
                )
                data['current_page_index'] = current_page_index
            else:
                await bot.answer_callback_query(callback_query.id, "Это первая страница.")

        # Обработка нажатия кнопки "Следующая страница"
        elif callback_query.data == 'next':
            news = parse_names(pages[current_page_index])
            if news:
                next_page = news['next_page']
                if next_page:
                    if next_page in pages:
                        current_page_index = pages.index(next_page)
                    else:
                        pages.append(next_page)
                        print(pages)#####
                        current_page_index += 1
                        print(current_page_index)
                    news = parse_names(pages[current_page_index])
                    articles = '\n'.join([f'{num}. {title}' for num, title, _ in news['articles']])
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    prev_button = types.InlineKeyboardButton('Предыдущая страница', callback_data='prev')
                    next_button = types.InlineKeyboardButton('Следующая страница', callback_data='next')
                    select_article_button = types.InlineKeyboardButton('Выбрать новость', callback_data='select_article')
                    keyboard.add(prev_button, next_button, select_article_button)
                    await bot.edit_message_text(
                        text=articles,
                        chat_id=callback_query.from_user.id,
                        message_id=callback_query.message.message_id,
                        reply_markup=keyboard
                    )
                    data['current_page_index'] = current_page_index
                    data['pages'] = pages
                else:
                    await bot.answer_callback_query(callback_query.id, "Следующая страница не найдена.")
            else:
                await bot.answer_callback_query(callback_query.id, "Произошла ошибка при загрузке новостей.")

@dp.callback_query_handler(lambda c: c.data == 'select_article', state=NavigationState.navigating)
async def select_article(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['current_page_index'] = data.get('current_page_index', 0)
        data['pages'] = data.get('pages', [START_URLS['science']])
    await NavigationState.navigating.set()
    await bot.send_message(callback_query.from_user.id, "Введите номер новости (от 1 до 20):")

@dp.message_handler(state=NavigationState.navigating)
async def process_article_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            article_number = int(message.text)
            if 1 <= article_number <= 20:
                current_page_index = data.get('current_page_index', 0)
                news = parse_names(data.get('pages')[current_page_index])
                selected_article = news['articles'][article_number - 1]
                article_url = selected_article[2]
                article_text = text_ria(article_url)
                summ_text = summarize_text(article_text)
                #СЮДАААААААААААААААААААААААААААААА
                
                # Получаем идентификатор чата, где было отправлено сообщение с текстом новости
                chat_id = message.chat.id

                # Добавляем кнопку "Вернуться назад" к сообщению с текстом новости
                keyboard = types.InlineKeyboardMarkup()
                back_button = types.InlineKeyboardButton('Вернуться назад', callback_data='back_to_list')
                keyboard.add(back_button)
                
                # Отправляем новое сообщение с обновленным текстом новости и кнопкой
                await bot.send_message(
                    chat_id=chat_id,
                    text=summ_text,
                    reply_markup=keyboard
                )
            else:
                await message.answer("Неверный номер новости. Введите число от 1 до 20.")
        except ValueError:
            await message.answer("Неверный формат ввода. Введите число от 1 до 20.")



@dp.callback_query_handler(lambda c: c.data == 'back_to_list', state=NavigationState.navigating)
async def back_to_list(callback_query: types.CallbackQuery, state: FSMContext):
    await NavigationState.navigating.set()
    await cmd_start(callback_query.message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
