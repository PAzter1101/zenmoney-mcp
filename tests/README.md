# Тесты для ZenMoney MCP Server

Структура тестов:
- `unit/` - юнит-тесты для отдельных компонентов
- `integration/` - интеграционные тесты

## Запуск тестов

```bash
# Все тесты
python -m pytest tests/

# Только юнит-тесты
python -m pytest tests/unit/

# Только интеграционные тесты
python -m pytest tests/integration/
```
