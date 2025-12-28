"""
Конфигурация для тестов
"""

import os
import sys

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
