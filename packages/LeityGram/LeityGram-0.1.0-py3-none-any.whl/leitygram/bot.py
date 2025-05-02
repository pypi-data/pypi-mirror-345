import aiohttp
import asyncio
from typing import Callable, Any, Dict, List
from .types import Message  # Импорт из types.py

class LeityBot:
    def __init__(self, token: str):
        self.token = token
        self.handlers = []
        self.session = aiohttp.ClientSession()
        
    def message_handler(self, commands: List[str] = None, content_types: List[str] = None):
        def decorator(func: Callable):
            self.handlers.append({
                'func': func,
                'commands': commands,
                'content_types': content_types
            })
            return func
        return decorator
        
    async def send_message(self, chat_id: int, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()
            
    async def get_updates(self, offset: int = None):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        async with self.session.get(url, params=params) as resp:
            return await resp.json()
            
    async def process_updates(self):
        offset = None
        while True:
            updates = await self.get_updates(offset)
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                if 'message' in update:
                    await self.process_message(update['message'])
                    
    async def process_message(self, message_data: Dict):
        message = Message(message_data)  # Используем импортированный Message
        message._bot = self  # Добавляем ссылку на бота
        for handler in self.handlers:
            if handler['commands'] and message.text:
                if any(message.text.startswith(f'/{cmd}') for cmd in handler['commands']):
                    await handler['func'](message)
            elif handler['content_types']:
                await handler['func'](message)
                
    def run_polling(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_updates())