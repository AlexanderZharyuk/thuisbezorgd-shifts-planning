# Thuisbezorgd shifts planning
Telegram bot for getting Thuisbezorgd shifts on current and next week.

## Getting Started

Before use this bot you need follow next steps:

- Install virtual environment in project folder by next command:
```shell
python3 -m venv venv
```
- Create `.env`-file where you put your credentials like this:
```shell
TELEGRAM_BOT_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN>
MODERATORS_TELEGRAM_ID=<YOUR-MODERATOR-TELEGRAM-ID>
TELEGRAM_ADMIN_ID=<YOUR-TELEGRAM-ID>
DATABASE_NAME=<YOUR-DATABASE-NAME> # For example: shifts.sqlite3 
RATE_PER_HOUR=<YOUR-RATE-PER-HOUR>
TAX_PERCENT=<YOUR-SALARY-TAX-PERCENT>
```
- Activate your venv by command:
```shell
. venv/bin/activate # For Linux
venv\Scripts\Activate.bat # For Windows
```

And install requirements:
```shell
pip install -r requirements.txt
```

## Deploy bot

For use this bot on your computer / VPS you need to run follow command:
```shell
python3 main.py
```

But it's not a good production idea. My suggestion to create [unit](https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files) in your systemd and enable it.

For example my unit `thuisbezorgd-bot.service`:
```text
[Unit]
Description=Thuisbezorg Shifts Bot


[Service]
WorkingDirectory=/opt/thuisbezorgd-shifts-planning/
Type=simple
ExecStart=/opt/thuisbezorgd-shifts-planning/venv/bin/python3 -b bot/main.py
Restart=always


[Install]
WantedBy=multi-user.target
```

After this steps your bot will work also after server restart. Hope you enjoy!

## Features

This bot created for people who want to know when I have shifts, that is my family and friend :)

Also I want to check my income and don't calculate it everytime, so this bot can
show only for me weekly incomes (previous and next week) and also I can manipulate and change my shifts timings through the bot.

If you want - you can check my next shifts here: [@ThuisbezorgdShiftsBot](https://t.me/ThuisbezorgdShiftsBot)

P.S:
Will add English version soon.

## Author
* Alexandr Jariuc

