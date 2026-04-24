import sqlite3
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем parent directory в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.functions import get_all_users, get_db_connection
from config import SERVER_HOST, SERVER_PORT, DATABASE_PATH


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            logger.info(f"GET запрос: {path}")
            
            if path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'index.html')
                with open(frontend_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            
            elif path.startswith('/css/') or path.startswith('/js/'):
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                file_path = os.path.join(base_path, 'frontend', path.lstrip('/'))
                
                # Защита от path traversal
                if not os.path.abspath(file_path).startswith(os.path.abspath(base_path)):
                    raise ValueError("Недопустимый путь")
                
                if os.path.exists(file_path):
                    self.send_response(200)
                    if path.endswith('.css'):
                        self.send_header('Content-type', 'text/css; charset=utf-8')
                    elif path.endswith('.js'):
                        self.send_header('Content-type', 'application/javascript; charset=utf-8')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, "Файл не найден")
            
            elif path == '/api/users':
                try:
                    users = get_all_users()
                    response = {
                        'status': 'success',
                        'count': len(users),
                        'data': users
                    }
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    logger.info(f"API /users: {len(users)} пользователей")
                except Exception as e:
                    logger.error(f"Ошибка в /api/users: {e}", exc_info=True)
                    self.send_error(500, "Ошибка БД")
            
            else:
                self.send_error(404, "Маршрут не найден")
        except Exception as e:
            logger.error(f"Критическая ошибка в do_GET: {e}", exc_info=True)
            try:
                self.send_error(500, "Внутренняя ошибка сервера")
            except:
                pass
    
    def log_message(self, format, *args):
        # Скрываем стандартные логи для чистоты
        pass


def start_server(host=SERVER_HOST, port=SERVER_PORT):
    """Запускает веб-сервер"""
    try:
        server = HTTPServer((host, port), RequestHandler)
        logger.info(f"🌐 Веб-сервер запущен на http://localhost:{port}")
        logger.info("Нажмите Ctrl+C для остановки")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("✅ Сервер остановлен (Ctrl+C)")
            server.server_close()
    except OSError as e:
        logger.error(f"❌ Ошибка запуска сервера (порт {port} может быть занят): {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка сервера: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    start_server()
