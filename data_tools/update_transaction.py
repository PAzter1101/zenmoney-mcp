"""
Инструмент для обновления транзакций
"""

from typing import Any, Dict

from mcp.types import CallToolResult, TextContent

from src.client import ZenMoneyClient

from .base import BaseDataTool


class UpdateTransactionTool(BaseDataTool):
    """Инструмент для обновления транзакции"""

    name = "data_set_transaction"
    description = "Обновление данных транзакции (категория, комментарий и др.)"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "ID транзакции для обновления",
                },
                "category": {
                    "type": "string", 
                    "description": "ID категории для назначения транзакции",
                },
                "comment": {
                    "type": "string",
                    "description": "Комментарий к транзакции",
                },
                "payee": {
                    "type": "string",
                    "description": "Получатель/плательщик",
                },
            },
            "required": ["transaction_id"],
        }

    async def execute(
        self, client: ZenMoneyClient, args: Dict[str, Any]
    ) -> CallToolResult:
        """Выполнение обновления транзакции"""
        transaction_id = args["transaction_id"]
        
        # Подготавливаем обновления
        updates = {}
        if "category" in args:
            updates["tag"] = [args["category"]] if args["category"] else []
        if "comment" in args:
            updates["comment"] = args["comment"]
        if "payee" in args:
            updates["payee"] = args["payee"]
            
        if not updates:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", 
                        text="❌ Не указаны поля для обновления"
                    )
                ]
            )

        try:
            success = await client.update_transaction(transaction_id, updates)
            
            if success:
                result = f"✅ Транзакция {transaction_id} успешно обновлена\n\n"
                result += "Обновленные поля:\n"
                for field, value in updates.items():
                    result += f"  {field}: {value}\n"
                    
                return CallToolResult(
                    content=[TextContent(type="text", text=result)]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", 
                            text=f"❌ Транзакция {transaction_id} не найдена"
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", 
                        text=f"❌ Ошибка обновления транзакции: {str(e)}"
                    )
                ]
            )
