"""
Инструменты аутентификации для MCP сервера
"""

from mcp.types import Tool, TextContent, CallToolResult
from typing import Dict, Any, List

class AuthTools:
    """Класс инструментов аутентификации"""
    
    def __init__(self):
        self.access_token = None
    
    def list_tools(self) -> List[Tool]:
        """Список доступных инструментов аутентификации"""
        return [
            Tool(
                name="auth_set_token",
                description="Установить Bearer токен для доступа к API ДзенМани",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "description": "Bearer токен для API ДзенМани"
                        }
                    },
                    "required": ["token"]
                }
            ),
            Tool(
                name="auth_get_status",
                description="Проверить статус аутентификации",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def handle_call(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Обработка вызовов инструментов аутентификации"""
        
        if name == "auth_set_token":
            token = arguments.get("token")
            if not token:
                return CallToolResult(
                    content=[TextContent(type="text", text="❌ Токен не указан")]
                )
            
            self.access_token = token
            return CallToolResult(
                content=[TextContent(type="text", text="✅ Токен установлен успешно")]
            )
        
        elif name == "auth_get_status":
            if self.access_token:
                masked_token = f"{self.access_token[:8]}...{self.access_token[-4:]}"
                return CallToolResult(
                    content=[TextContent(type="text", text=f"✅ Аутентифицирован: {masked_token}")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="❌ Токен не установлен")]
                )
        
        else:
            raise ValueError(f"Неизвестный инструмент аутентификации: {name}")
    
    def get_token(self) -> str:
        """Получение токена для использования в других модулях"""
        return self.access_token
