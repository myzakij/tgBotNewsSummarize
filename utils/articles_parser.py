from bs4 import BeautifulSoup
import requests
import logging


def parse_names(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Если запрос не удался, выбросит исключение
        soup = BeautifulSoup(response.text, "html.parser")
        news_dict = {}
        article_list = []

        # Поиск названий новостей и ссылок на статьи
        articles = soup.find_all('a', class_='list-item__title color-font-hover-only', href=True)

        # Поиск ссылки на следующую страницу
        next_url_div = soup.find('div', class_='list-items-loaded')
        n = next_url_div.get('data-next-url') if next_url_div else None
        next_page = f'https://ria.ru{n}' if n else None

        for i, article in enumerate(articles, start=1):
            article_list.append((i, article.text.strip(), article['href']))

        news_dict['articles'] = article_list
        news_dict['next_page'] = next_page

        return news_dict
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе к сайту: {e}")
        return None



#print(parse_names("https://ria.ru/services/science/more.html?id=1941738263&date=20240424T030000"))