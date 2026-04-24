import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл из корня проекта
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Получаем токен из переменной окружения
telegram_token = os.getenv('TELEGRAM_TOKEN')

if not telegram_token:
    raise ValueError(
        "❌ TELEGRAM_TOKEN не установлен!\n"
        "Создайте файл .env и добавьте: TELEGRAM_TOKEN=ваш_токен"
    )

# Дополнительные конфигурации
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'users.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
