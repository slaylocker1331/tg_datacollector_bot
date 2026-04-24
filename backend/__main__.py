#!/usr/bin/env python3
"""
Backend - главный файл для запуска всех сервисов
"""

import subprocess
import sys
import os
import signal
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

processes = []
running = True


def signal_handler(sig, frame):
    """Graceful shutdown"""
    global running
    running = False
    logger.info("\n⏹️  Остановка backend...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            try:
                p.kill()
            except:
                pass
    logger.info("✅ Backend остановлен")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

logger.info("=" * 60)
logger.info("🚀 Запуск полного backend")
logger.info("=" * 60)

# Changing to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Запуск веб-сервера
logger.info("🌐 Запуск веб-сервера на http://localhost:5000...")
try:
    server = subprocess.Popen([sys.executable, 'api/server.py'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    processes.append(server)
    time.sleep(1)
    
    # Проверяем, что процесс не упал сразу
    if server.poll() is not None:
        _, err = server.communicate()
        logger.error(f"❌ Ошибка запуска сервера: {err.decode('utf-8', errors='ignore')}")
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Ошибка запуска сервера: {e}")
    sys.exit(1)

# Запуск телеграм-бота
logger.info("🤖 Запуск телеграм-бота...")
try:
    bot = subprocess.Popen([sys.executable, 'bot/telegram_bot.py'],
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
    processes.append(bot)
    time.sleep(1)
    
    # Проверяем, что процесс не упал сразу
    if bot.poll() is not None:
        _, err = bot.communicate()
        logger.error(f"❌ Ошибка запуска бота: {err.decode('utf-8', errors='ignore')}")
        server.terminate()
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Ошибка запуска бота: {e}")
    server.terminate()
    sys.exit(1)

logger.info("")
logger.info("=" * 60)
logger.info("✅ Backend успешно запущен!")
logger.info("=" * 60)
logger.info("📊 Веб-интерфейс: http://localhost:5000")
logger.info("🤖 Телеграм-бот активен")
logger.info("")
logger.info("Для остановки нажмите Ctrl+C")
logger.info("=" * 60)
logger.info("")

# Ждём завершения
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    signal_handler(None, None)
