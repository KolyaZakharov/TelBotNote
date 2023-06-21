import logging
import os

import requests
import telebot
from dotenv import load_dotenv
from telebot.types import Message

load_dotenv()  # Загрузка переменных окружения из файла .env

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Конфигурационные параметры
bot_token = os.getenv("BOT_TOKEN")
api_base_url = (
    "http://127.0.0.1:8000/api/notes/"
)
# Инициализация бота
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=["start"])
def start_message(message: Message) -> None:
    """Обработчик команды /start."""
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для работы с заметками. Используй команды:\n"
        "/list - получить список заметок\n"
        "/create <title> <content> - создать новую заметку\n"
        "/update <note_id> <title> <content> - обновить существующую заметку\n"
        "/delete <note_id> - удалить заметку\n"
        "/view <note_id> - просмотреть заметку",
    )


@bot.message_handler(commands=["create"])
def create_note_handler(message: Message) -> None:
    """Обработчик команды /create."""
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "Недостаточно аргументов. Используйте: /create <title> <content>",
        )
        return
    title = args[0]
    content = " ".join(args[1:])

    try:
        # Отправляем POST запрос к API для создания заметки
        response = requests.post(
            api_base_url, json={"title": title, "content": content}
        )
        response.raise_for_status()
        bot.send_message(message.chat.id, "Заметка успешно создана")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, "Ошибка при создании заметки")
        logging.error(f"Ошибка при создании заметки: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка")
        logging.error(f"Необработанное исключение при создании заметки: {e}")


@bot.message_handler(commands=["list"])
def list_notes_handler(message: Message) -> None:
    """Обработчик команды /list."""
    try:
        # Отправляем GET запрос к  API для получения списка заметок
        response = requests.get(api_base_url)
        response.raise_for_status()
        notes = response.json()
        if notes:
            message_text = "\n".join(
                [f'{note["id"]}: {note["title"]}' for note in notes]
            )
        else:
            message_text = "Список заметок пуст"
        bot.send_message(message.chat.id, message_text)
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, "Ошибка при получении списка заметок")
        logging.error(f"Ошибка при получении списка заметок: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка")
        logging.error(f"Необработанное исключение при получении списка заметок: {e}")


@bot.message_handler(commands=["view"])
def view_note_handler(message: Message) -> None:
    """Обработчик команды /view."""
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.send_message(
            message.chat.id, "Недостаточно аргументов. Используйте: /view <note_id>"
        )
        return

    note_id = args[0]

    try:
        # Проверка, является ли введенное значение числом
        if not note_id.isdigit():
            bot.send_message(
                message.chat.id, "Пожалуйста, введите числовой идентификатор заметки."
            )
            return

        # Отправляем GET запрос к  API для получения информации о заметке по ее идентификатору
        response = requests.get(f"{api_base_url}{note_id}/")
        response.raise_for_status()
        note = response.json()
        message_text = f'Заметка {note["id"]}:\n\n{note["title"]}\n\n{note["content"]}'
        bot.send_message(message.chat.id, message_text)
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            bot.send_message(
                message.chat.id, "Заметки с указанным идентификатором не существует."
            )
        else:
            bot.send_message(
                message.chat.id,
                "Ошибка при получении информации о заметке. Пожалуйста, проверьте правильность ввода команды.",
            )
        logging.error(f"Ошибка при получении информации о заметке: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка")
        logging.error(
            f"Необработанное исключение при получении информации о заметке: {e}"
        )
    else:
        # Блок else будет выполнен, если исключений не возникло
        logging.info("Запрос на просмотр заметки успешно обработан.")
    finally:
        # Блок finally будет выполнен в любом случае, даже если возникло исключение
        logging.info("Запрос на просмотр заметки завершен.")


@bot.message_handler(commands=["update"])
def update_note_handler(message: Message) -> None:
    """Обработчик команды /update."""
    args = message.text.split()[1:]
    if len(args) < 3:
        bot.send_message(
            message.chat.id,
            "Недостаточно аргументов. Используйте: /update <note_id> <title> <content>",
        )
        return
    note_id = args[0]
    title = args[1]
    content = " ".join(args[2:])

    try:
        # Отправляем PUT запрос к  API для обновления заметки по ее идентификатору
        response = requests.put(
            f"{api_base_url}{note_id}/", json={"title": title, "content": content}
        )
        response.raise_for_status()
        bot.send_message(message.chat.id, "Заметка успешно обновлена")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, "Ошибка при обновлении заметки")
        logging.error(f"Ошибка при обновлении заметки: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка")
        logging.error(f"Необработанное исключение при обновлении заметки: {e}")


@bot.message_handler(commands=["delete"])
def delete_note_handler(message: Message) -> None:
    """Обработчик команды /delete."""
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.send_message(
            message.chat.id, "Недостаточно аргументов. Используйте: /delete <note_id>"
        )
        return
    note_id = args[0]

    try:
        # Проверка, является ли введенное значение числом
        if not note_id.isdigit():
            bot.send_message(
                message.chat.id, "Пожалуйста, введите числовой идентификатор заметки."
            )
            return

        # Отправляем DELETE запрос к  API для удаления заметки по ее идентификатору
        response = requests.delete(f"{api_base_url}{note_id}/")
        response.raise_for_status()
        bot.send_message(message.chat.id, "Заметка успешно удалена")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, "Заметки с таким ID не существует")
        logging.error(f"Ошибка при удалении заметки: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка")
        logging.error(f"Необработанное исключение при удалении заметки: {e}")

    logging.info("Запрос на удаление заметки завершен.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
