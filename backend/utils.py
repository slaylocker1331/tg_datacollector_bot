"""
Вспомогательные функции для retry и обработки сетевых ошибок
"""
import time
import logging
from functools import wraps
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable)


def retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Декоратор для автоматических повторов при ошибках
    
    Args:
        max_attempts: максимальное число попыток
        delay: начальная задержка в секундах
        backoff: множитель задержки при каждой попытке (экспоненциальный backoff)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"❌ {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"⚠️  {func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    
    return decorator


def wait_for_connection(max_attempts: int = 5, delay: float = 3.0):
    """
    Ждёт подключения к сервису с экспоненциальным backoff
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"❌ Connection failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"⚠️  Connection attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= 1.5
                except Exception as e:
                    logger.error(f"❌ Unexpected error: {e}")
                    raise
            
            return None
        
        return wrapper
    
    return decorator
