# Reminder bot

![GitHub last commit](https://img.shields.io/github/last-commit/evil-kekc/ReminderBot)
![GitHub repo size](https://img.shields.io/github/repo-size/evil-kekc/ReminderBot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/evil-kekc/ReminderBot)
![Stars](https://img.shields.io/github/stars/evil-kekc/ReminderBot?style=social)

---

# About The Project

Telegram bot to remind you of important events.

**How it works**: we create a reminder with a date and text using Telegram. The reminder data is stored in the database
and
when the specified date and time is reached, a reminder is sent to the user in a telegram

![til](images/UsageExample.gif)

---

# Quick start

1. Clone the [repo](https://github.com/evil-kekc/ReminderBot):

```
git clone https://github.com/evil-kekc/ReminderBot
```

2. Create and activate virtual environment

  ```sh
  python -m venv venv
  cd venv/Scripts
  activate.bat
  ```

3. Open [config.ini](config/config.ini) and paste the following options:

* **BOT_TOKEN** - Bot token received from [BotFather](https://t.me/BotFather)
* **HOST_URL** - Domain link (if you are using ngrok eg: https://e0d1-151-249-164-76.eu.ngrok.io)
* **MONGO_DB_URL** - Link to connect MongoDB
* **ADMIN_ID** - ID of the admin who will have access to the bug reports analysis
* **DB** - Database to be used in the project (SQLite_DB / MONGO_DB)
* **TIMEDELTA** - Time difference (in hours) with server

Example:

```
BOT_TOKEN = 123456789:QWERTYUIOPASDFGHJKLZXCVBNM
HOST_URL = https://example.com
MONGO_DB_URL = mongodb+srv://username:password@cluster.jmezdsn.mongodb.net/?retryWrites\\\=true&w\\\=majority
ADMIN_ID = 123456789
DB = SQLite_DB
TIMEDELTA = 3
```

4. Run [ngrok.exe](config/ngrok.exe) to start the server (making the HTTP port of our application available) and write
   command in ngrok terminal and then use the received link in [HOST_URL](config/config.ini):

```
ngrok http 8000
```

Example:

![til](images/NgrokExample.gif)



5. Run the application [main.py](app/main.py)

```
uvicorn app.main:app --reload
```

---

# Contact

Artem Troshkin

**Email:** 3371824@gmail.com

**Telegram:** [evil_kekc](https://t.me/evil_kekc)
