# 🎯 Backend - Телеграм бот + Веб API

Полнофункциональный backend с телеграм-ботом и веб-сервером.

## 📁 Структура

```
backend/
├── __main__.py              # Главный файл для запуска
├── config.py                # Конфигурация (токены)
├── requirements.txt         # Зависимости
│
├── api/                     # Веб-сервер
│   ├── __init__.py
│   └── server.py            # HTTP сервер + API
│
├── bot/                     # Телеграм-бот
│   ├── __init__.py
│   └── telegram_bot.py      # Обработчики команд
│
└── db/                      # База данных
    ├── __init__.py
    └── functions.py         # SQL функции
```

## 🚀 Запуск

### Способ 1: Прямой запуск (рекомендуется)
```bash
python3 backend/__main__.py
```

### Способ 2: Модуль Python
```bash
python3 -m backend
```

## 📦 Установка зависимостей

```bash
pip install --user python-telegram-bot
```

Или если `--user` не работает:
```bash
pip install --break-system-packages python-telegram-bot
```

## 🔧 Конфигурация

Отредактируйте `backend/config.py`:
```python
telegram_token = "ВАШ_ТОКЕН_ЗДЕСЬ"
```

## 📊 API Endpoints

- `GET /` — HTML интерфейс
- `GET /api/users` — JSON данные пользователей
- `GET /css/*` — CSS файлы
- `GET /js/*` — JavaScript файлы

## 🤖 Команды Бота

- `/start` — начать регистрацию
- Отправить контакт — сохранить номер телефона

## 🗄️ База данных

Данные хранятся в `users.db` с таблицей:
- `id` — ID в БД
- `telegram_id` — ID пользователя Telegram
- `name` — Имя пользователя
- `phone` — Номер телефона
- `created_at` — Дата регистрации

## ✨ Особенности

✅ Единый backend со всеми сервисами  
✅ Модульная архитектура  
✅ Разделение на API, Bot, DB  
✅ Легко расширяется  
✅ Без внешних зависимостей (кроме python-telegram-bot)  

## 📝 Логирование

Запуск происходит в терминале с красивым форматированием:
- 🌐 Статус веб-сервера
- 🤖 Статус телеграм-бота
- ✅ Статус готовности

## 🛑 Остановка

Нажмите `Ctrl+C` в терминале — graceful shutdown обоих сервисов.
