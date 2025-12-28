"""
Интеграционные тесты для MCP сервера
"""

import asyncio
import unittest
from unittest.mock import patch

from tools.data import DataTools


class TestMCPServerIntegration(unittest.TestCase):
    """Интеграционные тесты для MCP сервера"""

    def setUp(self):
        """Настройка тестов"""
        self.data_tools = DataTools()

    def test_data_tools_initialization(self):
        """Тест инициализации DataTools"""
        self.assertIsNotNone(self.data_tools)
        self.assertIsNotNone(self.data_tools.transactions_tool)
        self.assertIsNotNone(self.data_tools.transaction_detail_tool)

    def test_list_tools(self):
        """Тест получения списка инструментов"""
        tools = self.data_tools.list_tools()

        self.assertGreater(len(tools), 0)

        tool_names = [tool.name for tool in tools]
        self.assertIn("data_get_transactions", tool_names)
        self.assertIn("data_get_transaction_detail", tool_names)
        self.assertIn("data_get_categories", tool_names)
        self.assertIn("data_get_accounts", tool_names)

    def test_transaction_detail_tool_registration(self):
        """Тест регистрации инструмента детализации транзакций"""
        tools = self.data_tools.list_tools()
        detail_tools = [t for t in tools if t.name == "data_get_transaction_detail"]

        self.assertEqual(len(detail_tools), 1)

        detail_tool = detail_tools[0]
        self.assertEqual(
            detail_tool.description, "Получить детальную информацию о транзакции по ID"
        )
        self.assertIn("transaction_id", detail_tool.inputSchema["properties"])
        self.assertIn("transaction_id", detail_tool.inputSchema["required"])

    @patch("src.client.ZenMoneyClient")
    def test_handle_call_routing(self, mock_client_class):
        """Тест маршрутизации вызовов инструментов"""
        mock_client = mock_client_class.return_value

        async def run_test():
            # Тест вызова несуществующего инструмента
            result = await self.data_tools.handle_call(
                "non_existent_tool", {}, "fake-token"
            )
            self.assertIn("Неизвестный инструмент", result.content[0].text)

        asyncio.run(run_test())

    def test_tool_input_schemas(self):
        """Тест схем входных параметров инструментов"""
        tools = self.data_tools.list_tools()

        for tool in tools:
            # Каждый инструмент должен иметь схему
            self.assertIsNotNone(tool.inputSchema)
            self.assertIn("type", tool.inputSchema)
            self.assertEqual(tool.inputSchema["type"], "object")

            # Проверяем специфичные схемы
            if tool.name == "data_get_transaction_detail":
                self.assertIn("transaction_id", tool.inputSchema["required"])
            elif tool.name == "data_get_transactions":
                props = tool.inputSchema["properties"]
                self.assertIn("show_ids", props)
                self.assertIn("limit", props)


if __name__ == "__main__":
    unittest.main()
