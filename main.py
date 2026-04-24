#!/usr/bin/env python3
"""
Главный скрипт для запуска всей программы
"""

import subprocess
import sys

if __name__ == '__main__':
    print("=" * 60)
    print("🎯 Запуск приложения")
    print("=" * 60)
    
    # Запускаем backend
    result = subprocess.run([sys.executable, '-m', 'backend'], cwd='.')
    sys.exit(result.returncode)