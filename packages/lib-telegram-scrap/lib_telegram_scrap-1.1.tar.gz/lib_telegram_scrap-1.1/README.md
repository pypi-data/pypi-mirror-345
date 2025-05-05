# lib_telegram_scrap

`lib_telegram_scrap` это библиотека для сбора информации из чатов

## Установка из PyPI

```bash
pip install lib_telegram_scrap
```

## Использование репозитория GitHub

```bash
git clone https://github.com/YuranIgnatenko/lib_telegram_scrap.git
cd lib_telegram_scrap
pip install .
```

## Пример использования

```python
from lib_telegram_scrap.scrapper import Scraper
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

API_ID = config['Telegram']['api_id']
API_HASH = config['Telegram']['api_hash']
COUNT_LAST_MESSAGES = config['Channel']['count_last_messages']
URL_CHANNEL = config['Channel']['url']

async def main():
	scraper = Scraper(api_id=API_ID, api_hash=API_HASH)

	messages = await scraper.get_last_messages(URL_CHANNEL, COUNT_LAST_MESSAGES)
	
	# Process messages
	for message in messages:
		print(f"Message: {message.message}")
		print(f"Date: {message.date}")
		print("---")

	await scraper.close()

if __name__ == "__main__":
	asyncio.run(main())
```

> If first using, then enter console
```
phone number: +7xxxxxxxxx
received code from telegram: xxxxx
*your 2-password
```

