import aiohttp
import asyncio
from typing import Callable, Any, Dict, List, Optional
from .types import Message

class LeityBot:
    def __init__(self, token: str):
        self.token = token
        self.handlers = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def create_session(self):
        """Создает aiohttp сессию"""
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        """Закрывает aiohttp сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def message_handler(self, 
                       commands: Optional[List[str]] = None, 
                       content_types: Optional[List[str]] = None):
        """Декоратор для регистрации обработчиков сообщений"""
        def decorator(func: Callable):
            self.handlers.append({
                'func': func,
                'commands': commands,
                'content_types': content_types
            })
            return func
        return decorator
        
    async def send_message(self, chat_id: int, text: str):
        """Отправляет сообщение в Telegram"""
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()
            
    async def get_updates(self, offset: Optional[int] = None):
        """Получает обновления от Telegram API"""
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        async with self.session.get(url, params=params) as resp:
            return await resp.json()
            
    async def process_updates(self):
        """Основной цикл обработки обновлений"""
        offset = None
        try:
            while True:
                updates = await self.get_updates(offset)
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        await self.process_message(update['message'])
        except asyncio.CancelledError:
            pass
                    
    async def process_message(self, message_data: Dict[str, Any]):
        """Обрабатывает входящее сообщение"""
        message = Message(message_data)
        message._bot = self  # Добавляем ссылку на бота
        
        for handler in self.handlers:
            if handler['commands'] and message.text:
                if any(message.text.startswith(f'/{cmd}') for cmd in handler['commands']):
                    await handler['func'](message)
            elif handler['content_types']:
                await handler['func'](message)
                
    async def run_polling(self):
        """Запускает бота в режиме polling"""
        await self.create_session()
        try:
            await self.process_updates()
        finally:
            await self.close_session()
            
    def run_polling_sync(self):
        """Синхронный запуск бота (для удобства)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_polling())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()