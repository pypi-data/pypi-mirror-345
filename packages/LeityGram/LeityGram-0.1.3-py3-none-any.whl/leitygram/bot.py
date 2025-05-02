import aiohttp
import asyncio
from typing import Callable, Any, Dict, List, Optional, Union
from .types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery

class LeityBot:
    def __init__(self, token: str, parse_mode: Optional[str] = None):
        self.token = token
        self.parse_mode = parse_mode
        self.handlers = []
        self.callback_handlers = []
        self.session = None
        self._me = None

    # ===== Базовые функции =====
    async def create_session(self):
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_me(self):
        """Получает информацию о боте"""
        if not self._me:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            async with self.session.get(url) as resp:
                self._me = await resp.json()
        return self._me

    # ===== Обработчики =====
    def message_handler(self, commands=None, content_types=None):
        def decorator(func):
            self.handlers.append({
                'func': func,
                'commands': commands,
                'content_types': content_types or ['text']
            })
            return func
        return decorator

    def callback_query_handler(self, func=None):
        """Обработчик inline кнопок"""
        if func:
            self.callback_handlers.append(func)
        else:
            def decorator(f):
                self.callback_handlers.append(f)
                return f
            return decorator

    # ===== Методы API =====
    async def send_message(self, 
                         chat_id: Union[int, str],
                         text: str,
                         reply_markup=None,
                         reply_to_message_id=None):
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': self.parse_mode
        }
        if reply_markup:
            params['reply_markup'] = reply_markup.to_json()
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def answer_callback_query(self,
                                  callback_query_id: str,
                                  text: Optional[str] = None,
                                  show_alert: bool = False):
        params = {
            'callback_query_id': callback_query_id,
            'show_alert': show_alert
        }
        if text:
            params['text'] = text

        url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # ===== Ядро обработки =====
    async def process_updates(self):
        offset = None
        try:
            while True:
                updates = await self.get_updates(offset)
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        await self.process_message(update['message'])
                    elif 'callback_query' in update:
                        await self.process_callback(update['callback_query'])
        except asyncio.CancelledError:
            pass

    async def process_message(self, message_data: Dict[str, Any]):
        message = Message(message_data)
        message._bot = self
        
        for handler in self.handlers:
            if handler['commands'] and message.text:
                if any(message.text.startswith(f'/{cmd}') for cmd in handler['commands']):
                    await handler['func'](message)
            elif handler['content_types']:
                if message.content_type in handler['content_types']:
                    await handler['func'](message)

    async def process_callback(self, callback_data: Dict[str, Any]):
        callback = CallbackQuery(callback_data)
        callback._bot = self
        
        for handler in self.callback_handlers:
            await handler(callback)

    # ===== Запуск =====
    async def run_polling(self):
        await self.create_session()
        try:
            await self.get_me()  # Проверяем токен
            await self.process_updates()
        finally:
            await self.close_session()

    def run_polling_sync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_polling())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()