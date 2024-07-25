"""Система управления библиотекой"""
import operator
from functools import reduce
from json import dump, load
from json.decoder import JSONDecodeError
from uuid import uuid4


class Book():
    """Класс книги.
    Поля:
    - id (уникальный идентификатор, генерируется автоматически);
    - title (название книги);
    - author (автор книги);
    - year (год издания);
    - status (статус книги: в наличии/выдана)."""
    BOOK_STATUSES = {
        "0": "Выдана",
        "1": "В наличии"
    }

    BAD_BOOK_STATUS = "Недопустимый статус книги: "

    def __init__(
            self, title, author, year, id=str(uuid4().int), status="В наличии"
    ):
        """Создание экземляра книги."""
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        if status in self.BOOK_STATUSES.values():
            self.status = status
        else:
            raise ValueError(self.BAD_BOOK_STATUS, status)

    def set_status(self, status):
        """Установка статуса."""
        self.status = self.BOOK_STATUSES[status]

    def __str__(self):
        return (
            f"{self.id} - {self.title} - {self.author} - "
            f"{self.year} - {self.status}"
        )


class Library():
    """Класс библиотеки.
    Единственное поле - список книг."""
    BAD_FILE_MESSAGE = "Некорректный формат файла: "
    REPEATED_ID = "повторяющийся ID: "

    def __init__(self):
        self.books = []

    def add_book(self, book):
        """Добавление книги."""
        self.books.append(book)

    def delete(self, book):
        """Удаление книги."""
        self.books.remove(book)

    def list(self):
        """Получение списка книг."""
        return self.books

    def load_data(self, fp):
        """Загрузка книг из файла.
        Аргументом функция принимает файловый поток."""
        try:
            data = load(fp)["books"]
            ids_set = {}
            for book in data:
                if book["id"] in ids_set:
                    raise ValueError(
                        self.BAD_FILE_MESSAGE, self.REPEATED_ID, id
                    )
                self.add_book(
                    Book(
                        book["title"],
                        book["author"],
                        book["year"],
                        book["id"],
                        book["status"]
                    )
                )
        except (JSONDecodeError, KeyError) as exc:
            exit(self.BAD_FILE_MESSAGE, exc)
        except ValueError as exc:
            exit(exc)

    def save(self, fp):
        """Сохранение списка книг в файл.
        Аргументом функция принимает файловый поток."""
        dump(
            self, fp, default=lambda x: x.__dict__, ensure_ascii=False
        )

    def search(self, **kwargs):
        """Поиск книги.
        Возможен поиск либо по id (остальные аргументы проигнорируются),
        либо по автору, названию и году."""
        if 'id' in kwargs:
            for book in self.books:
                if book.id == kwargs['id']:
                    return book
        found = []
        for book in self.books:
            if reduce(
                operator.and_,
                [
                    getattr(book, field) == value
                    for (field, value) in kwargs.items()
                    if value
                ]
            ):
                found.append(book)
        return found


if __name__ == '__main__':
    """Консольное приложение для управления библиотекой."""

    MESSAGES = {
        "AUTHOR_INPUT": "Автор: >",
        "BAD_COMMAND":
            "Неверная команда, воспользуйтесь командой <ПОМОЩЬ> для справки",
        "BAD_STATUS": "Неверный статус",
        "BOOK_ADDED": "Добавлена книга: ",
        "BOOK_NOT_FOUND": "Книга с данным идентификатором не найдена",
        "BOOK_DELETED": "Удалена книга:",
        "FILE_INPUT": "Путь к файлу: >",
        "FOUND": "Результаты поиска:",
        "HELP":
            "Доступные команды:\n"
            "ВЫХОД - выход из программы\n"
            "ДОБАВИТЬ - добваление книги\n"
            "УДАЛИТЬ - удаление книги из библиотеки\n"
            "КАТАЛОГ - выводит список книг библиотеки\n"
            "ПОИСК - поиск книги в библиотеке\n"
            "ПОМОЩЬ - вывод этого сообщения\n"
            "СТАТУС - изменение статуса книги\n"
            "CОХРАНИТЬ - сохранить в файл",
        "ID_INPUT": "ID книги: >",
        "INTERRUPTED": "Пустой ввод, роцедура прервана",
        "OPEN_ERROR":
            "Не удалось открыть файл, "
            "проверьте путь и перезапустите программу",
        "OPEN_SUCCESS": "успешно открыт, данные загружены.",
        "NOT_FOUND": "Таких книг не найдено",
        "PATH_REQUEST":
            "Введите путь к файлу с каталогом книг "
            "(если файл не существует, он будет создан):",
        "QUIT": "Спасибо за пользование библиотекой!",
        "SAVE_ERROR": "Не удалось сохранить в файл",
        "SAVE_SUCCESS": "Данные успешно сохранены.",
        "STATUS_SET": "Статус изменен:",
        "STATUS_INPUT": "Статус: 0 - выдана / 1 - в наличии): >",
        "TITLE_INPUT": "Название: >",
        "YEAR_INPUT": "Год: >"
    }

    def add(library):
        """Добавление книги в библиотеку через консоль."""
        title = input(MESSAGES["TITLE_INPUT"]).strip()
        author = input(MESSAGES["AUTHOR_INPUT"]).strip()
        year = input(MESSAGES["YEAR_INPUT"]).strip()
        book = Book(title=title, author=author, year=year)
        library.add_book(book=book)
        print(MESSAGES["BOOK_ADDED"], book)

    def delete(library):
        """Удаление книги из библиотеки через консоль."""
        id = input(MESSAGES["ID_INPUT"]).strip()
        if id:
            book = library.search(id=id)
            if book:
                library.delete(book=book)
                print(MESSAGES["BOOK_DELETED"], book)
            else:
                print(MESSAGES["BOOK_NOT_FOUND"])
        else:
            print(MESSAGES["INTERRUPTED"])

    def help_():
        """Вывод списка доступных команд на консоль."""
        print(MESSAGES["HELP"])

    def list_(library):
        """Вывод книг библиотеки на консоль."""
        for book in library.list():
            print(book)

    def status(library):
        """Изменение статуса книги в библиотеке через консоль."""
        id = input(MESSAGES["ID_INPUT"]).strip()
        if id:
            book = library.search(id=id)
            if book:
                status = input(MESSAGES["STATUS_INPUT"]).strip()
                if status in Book.BOOK_STATUSES:
                    book.set_status(status)
                    print(MESSAGES["STATUS_SET"], book)
                else:
                    print(MESSAGES["BAD_STATUS"])
            else:
                print(MESSAGES["BOOK_NOT_FOUND"])
        else:
            print(MESSAGES["INTERRUPTED"])

    def quit_():
        """Выход из приложения."""
        exit(MESSAGES["QUIT"])

    def save(library):
        """Сохранение библиотеки в файл."""
        filename = input(MESSAGES["FILE_INPUT"]).strip()
        if filename:
            try:
                with open(filename, 'w') as fp:
                    library.save(fp)
                print(MESSAGES["SAVE_SUCCESS"])
            except OSError:
                print(MESSAGES["SAVE_ERROR"])

    def search(library):
        """Поиск книги по названию, автору, году."""
        (title, author, year) = (
            input(MESSAGES["TITLE_INPUT"]).strip(),
            input(MESSAGES["AUTHOR_INPUT"]).strip(),
            input(MESSAGES["YEAR_INPUT"]).strip(),
        )
        if title or author or year:
            found = library.search(title=title, author=author, year=year)
            if found:
                print(MESSAGES["FOUND"])
                for book in found:
                    print(book)
            else:
                print(MESSAGES["NOT_FOUND"])
        else:
            print(MESSAGES["INTERRUPTED"])

    def unknown_command():
        """Вывод на консоль сообщения о неизвестной команде."""
        print(MESSAGES["BAD_COMMAND"])

    # команды управления библиотекой
    LIBRARY_COMMANDS = {
        "добавить": add,
        "удалить": delete,
        "каталог": list_,
        "статус": status,
        "сохранить": save,
        "поиск": search
    }

    # прочие команды
    OTHER_COMMANDS = {
        "выход": quit_,
        "помощь": help_
    }

    # загружаем файл при необходимости, создаем библиотеку
    print(MESSAGES["PATH_REQUEST"])
    filepath = input(">").strip()
    library = Library()
    if filepath:
        try:
            with open(filepath) as fp:
                library.load_data(fp)
            print(filepath, MESSAGES["OPEN_SUCCESS"])
        except OSError:
            print(MESSAGES["OPEN_ERROR"])
    else:
        print("Создана новая библиотека.")

    # принимаем команды
    while (True):
        command = input(">").strip().lower()
        if command in LIBRARY_COMMANDS:
            LIBRARY_COMMANDS[command](library)
        else:
            OTHER_COMMANDS.get(command, unknown_command)()
