import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Union

from bot_config import BASE_DIR
from config import load_config

config = load_config(fr'{BASE_DIR}/config/config.ini')


class SQLiteDB:
    def __init__(self):
        self.con = sqlite3.connect(r'users.db', check_same_thread=False)
        self.cursor = self.con.cursor()
        self._create_table_users()

    def _create_table_users(self):
        """Create table reminds

        :return:
        """
        with self.con:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users"
                                "(id TEXT UNIQUE,"
                                "user_id INTEGER,"
                                "name TEXT,"
                                "date TEXT,"
                                "text TEXT)")

    def _check_duplicates(self, value: tuple):
        """Checks for duplicate users

        :param value:
        :return:
        """
        with self.con:
            all_data = self.cursor.execute("SELECT user_id, name, date, text FROM users")
            for remind in all_data.fetchall():
                if remind == value[1:]:
                    return True

    def _get_formatted_json(self, users: Union[list, tuple]):
        """Returns formatted users

        :return: formatted users
        """
        all_posts = dict()
        for user in users:
            _id = user[0]
            user_id = user[1]
            name = user[2]
            date = user[3]
            text = user[-1]
            all_posts[_id] = {
                'user_id': user_id,
                'name': name,
                'date': date,
                'text': text
            }
        return all_posts

    def insert_one_value(self, user_id: int, name: str, date: str, text: str, _id=None) -> Union[bool, int, tuple]:
        """Insert reminder into DB

        :param _id: Unique_id
        :param user_id: user unique id
        :param name: username
        :param date: date of remind
        :param text: text of remind
        :return: bool, status code, response text/updated or inserted value
        """
        try:
            if not _id:
                value = (str(uuid.uuid4()), user_id, name, date, text)
            else:
                value = (_id, user_id, name, date, text)
            if not self._check_duplicates(value):
                with self.con:
                    self.cursor.execute(
                        "INSERT INTO users (id, user_id, name, date, text) VALUES (?, ?, ?, ?, ?)", value
                    )
                    return True, 200, value
            else:
                return False, 404, value

        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return False, 404, f'{repr(ex)}'

    def get_all_values_json(self):
        """Get all values from the collection

        :return:
        """
        try:
            with self.con:
                all_data = self.cursor.execute("SELECT * FROM users")
                all_posts = self._get_formatted_json(all_data.fetchall())
                return all_posts, 200
        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return repr(ex), 404

    def _delete_values(self, all_id: tuple):
        """Delete value by id

        :return:
        """
        with self.con:
            for _id in all_id:
                self.cursor.execute('DELETE FROM users WHERE id = ?', (_id,))

    def send_remind(self):
        """Send text remind from DB

        :return: user id, user name, text/None
        """
        with self.con:
            time_direction = config.tg_bot.TIME_DIRECTION
            now = datetime.now() + timedelta(hours=time_direction)
            now_date = now.strftime('%H:%M - %d.%m.%Y')
            result = self.cursor.execute("SELECT * FROM users WHERE date = ?", (now_date,))

            all_data = result.fetchall()
            if all_data:
                all_id = tuple(
                    [_id[0] for _id in all_data]
                )
                self._delete_values(all_id)
                for value in all_data:
                    user_id = value[1]
                    name = value[2]
                    text = value[-1]
                    yield user_id, name, text
            else:
                return

    def delete_all_values(self):
        """Delete all values in the collection

        :return: success text message or error text message
        """
        with self.con:
            try:
                self.cursor.execute('DELETE FROM users')
                return 'All values removed', 200
            except Exception as ex:
                logging.error(f'{repr(ex)}')
                return repr(ex), 404
