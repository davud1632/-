import logging
import requests
import pdfplumber
from io import BytesIO
import telebot

# Замените на ваш токен
API_TOKEN = '7408236858:AAFPRYC0W3c14YRW9co9mXs8-spsRRi_jv4'
bot = telebot.TeleBot(API_TOKEN)

PDF_URL = 'https://aitanapa.ru/download/%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5/?wpdmdl=970&refresh=673b6bdf508e11731947487'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_schedule_from_pdf():
    """Извлекает расписание из PDF-файла по URL. Возвращает текст расписания или сообщение об ошибке."""
    try:
        response = requests.get(PDF_URL, stream=True)  # stream=True для экономии памяти
        response.raise_for_status()  # Проверка кода ответа

        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = ""
            for page in pdf.pages:
                #Обработка кодировки
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2) #увеличиваем толерантность для лучшего распознования
                if page_text:
                    text += page_text + "\n"

            return text.strip() # Удаление лишних пробелов

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке PDF: {e}")
        return f"Ошибка при загрузке PDF: {e}"
    except pdfplumber.exceptions.EmptyFileError:
        logger.error(f"PDF-файл пуст.")
        return "PDF-файл пуст."
    except Exception as e:  # Улавливаем другие возможные ошибки
        logger.exception(f"Непредвиденная ошибка: {e}")  # logging.exception записывает traceback
        return f"Произошла непредвиденная ошибка."



@bot.message_handler(commands=['schedule_pdf'])
def send_schedule_pdf(message):
    """Обрабатывает команду /schedule_pdf, отправляет расписание."""
    schedule_text = get_schedule_from_pdf()
    bot.reply_to(message, schedule_text, parse_mode="HTML")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обрабатывает команды /start и /help."""
    bot.reply_to(message, "Привет! Используй команду /schedule_pdf, чтобы получить расписание.")


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.exception(f"Ошибка в основном цикле бота: {e}")