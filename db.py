import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pymongo
from pymongo.errors import DuplicateKeyError


class MongoDB:
    def __init__(self, collection):
        self.collection = collection
        logs_folder = Path('../logs')
        logs_folder.mkdir() if not logs_folder.exists() else None

        logging.basicConfig(filename=f'../logs/parser.log',
                            level=logging.DEBUG,
                            format='[%(asctime)s] %(levelname)s - %(message)s',
                            datefmt='%H:%M:%S',
                            encoding='utf-8')

    def insert_one_value(self, user_id, name, date, text):
        """Insert reminder into DB

        :param user_id: user unique id
        :param name: username
        :param date: date of remind
        :param text: text of remind
        :return: bool, status code, response text/updated or inserted value
        """
        try:
            value = {'_id': str(uuid.uuid4()),
                     'user_id': user_id,
                     'name': f'{name}',
                     'date': date,
                     'text': text}

            self.collection.insert_one(value)
            return True, 200, value
        except pymongo.errors.DuplicateKeyError:
            try:
                value = {'_id': str(uuid.uuid4()),
                         'user_id': user_id,
                         'name': f'{name}',
                         'date': date,
                         'text': text}

                self.collection.replace_one(value)
                return True, 200, value
            except Exception as ex:
                return False, 404, f'{repr(ex)}'
        except Exception as ex:
            return False, 404, f'{repr(ex)}'

    def delete_all_values(self):
        """Delete all values in the collection

        :return: success text message or error text message
        """
        try:
            self.collection.delete_many({})
            logging.info('All values removed')
            return 'All values removed', 200
        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return repr(ex), 404

    def get_all_values_json(self):
        """Get all values from the collection

        :return: all posts in the dict representation
        """
        try:
            all_posts = dict()
            data = self.collection.find()
            for remind in data:
                all_posts[remind['_id']] = remind
            if all_posts:
                logging.info(f'Successfully retrieved all values')
                return all_posts, 200
            else:
                logging.error(f'No value')
                return 'There is no such meaning', 404
        except Exception as ex:
            logging.error(f'{repr(ex)}')
            return repr(ex), 404

    def send_remind(self):
        """Send text remind from DB

        :return: user id, user name, text
        """
        if self.collection.count_documents({}) != 0:
            query = {}
            for values in self.collection.find(query, {'_id': 1, 'date': 1, 'text': 1, 'user_id': 1, 'name': 1}):
                now_date = datetime.now() + timedelta(hours=3)
                now_date = now_date.strftime('%H:%M - %d.%m.%Y')

                date = values.get('date')
                _id = values.get('_id')
                name = values.get('name')
                if date == now_date:
                    text = values.get('text')
                    user_id = values.get('user_id')
                    self.collection.delete_one({'_id': _id})
                    return user_id, name, text
