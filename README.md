## Recommendation before use

# Join the bot [here](https://t.me/kaiaplaybot/app?startapp=ref-sfpx96ju54fv41n)

# 🔥🔥 Use PYTHON 3.10 - 3.11.5 🔥🔥

## Features  
| Feature                                                     | Supported  |
|---------------------------------------------------------------|:----------------:|
| Multithreading                                                |        ✅        |
| Proxy binding to session                                      |        ✅        |
| Auto claim                                                    |        ✅        |
| Auto checkin                                                  |        ✅        |
| Auto spin                                                     |        ✅        |
| Support for tdata / pyrogram .session / telethon .session     |        ✅        |


## [Settings](https://github.com/vanhbakaa/Kaia-bot/blob/main/.env-example)
| Settings | Description |
|----------------------------|:-------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**      | Platform data from which to run the Telegram session (default - android)                                      |
| **AUTO_UPGRADE**           | Automatically upgrade (mining speed and mutiplier) (default: True)                                            |           
| **REF_LINK**               | Put your ref link here (default: my ref link)                                                                 |
| **AUTO_SPIN**              | Auto Spin wheel (default: False) recommend turn off for new user                                              |
| **USE_PROXY_FROM_FILE**    | Whether to use a proxy from the bot/config/proxies.txt file (True / False)                                    |


## Quick Start 📚

To install libraries and run bot - open run.bat on Windows

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10 - 3.11.5**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/vanhbakaa/Kaia-bot/) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/vanhbakaa/Kaia-bot.git
cd Kaia-bot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/Kaia-bot >>> python3 main.py --action (1/2)
# Or
~/Kaia-bot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/Kaia-bot >>> python main.py --action (1/2)
# Or
~/Kaia-bot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```
### Contacts

For support or questions, you can contact me [![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/airdrop_tool_vanh)
