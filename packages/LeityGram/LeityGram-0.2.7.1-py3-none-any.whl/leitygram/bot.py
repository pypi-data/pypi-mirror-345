import aiohttp
import asyncio
import logging
from typing import Callable, Any, Dict, List, Optional, Union
from .types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove

class LeityBot:
    def __init__(self, token: str, parse_mode: Optional[str] = None):
        self.token = token
        self.parse_mode = parse_mode
        self.handlers = []
        self.callback_handlers = []
        self.session = None
        self._me = None
        self.user_data = {}  # Хранилище пользовательских данных
        self.user_states = {}  # Хранилище состояний пользователей
        self.commands = {}  # Пустой словарь команд (добавляется разработчиком)

    async def create_session(self):
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_me(self):
        if not self._me:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            async with self.session.get(url) as resp:
                self._me = await resp.json()
                logging.info(f"Bot info loaded: {self._me}")
        return self._me

    async def get_updates(self, offset: Optional[int] = None):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {'timeout': 30, 'allowed_updates': ['message', 'callback_query']}
        if offset:
            params['offset'] = offset
            
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

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
        if func:
            self.callback_handlers.append(func)
        else:
            def decorator(f):
                self.callback_handlers.append(f)
                return f
            return decorator

    # Методы для работы с API Telegram
    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        
        if 'reply_markup' in kwargs and hasattr(kwargs['reply_markup'], 'to_json'):
            params['reply_markup'] = kwargs['reply_markup'].to_json()

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            async with self.session.post(url, json=params) as resp:
                return await resp.json()
        except Exception as e:
            logging.error(f"Error sending message: {e}")

    async def answer_callback_query(self, callback_query_id: str, **kwargs):
        params = {
            'callback_query_id': callback_query_id,
            **kwargs
        }

        url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def delete_message(self, chat_id: Union[int, str], message_id: int):
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage"
        params = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_photo(self, chat_id: Union[int, str], photo: str, caption: Optional[str] = None, **kwargs):
        params = {
            'chat_id': chat_id,
            'photo': photo,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_document(self, chat_id: Union[int, str], document: str, caption: Optional[str] = None, **kwargs):
        params = {
            'chat_id': chat_id,
            'document': document,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def edit_message_text(self, chat_id: Union[int, str], message_id: int, text: str, **kwargs):
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        url = f"https://api.telegram.org/bot{self.token}/editMessageText"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def edit_message_reply_markup(self, chat_id: Union[int, str], message_id: int, reply_markup=None):
        params = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        if reply_markup and hasattr(reply_markup, 'to_json'):
            params['reply_markup'] = reply_markup.to_json()
        url = f"https://api.telegram.org/bot{self.token}/editMessageReplyMarkup"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # Методы для работы с состояниями
    async def set_state(self, user_id: int, state: Optional[str]):
        """Установить состояние для пользователя"""
        if state is None:
            self.user_states.pop(user_id, None)
        else:
            self.user_states[user_id] = state

    async def get_state(self, user_id: int) -> Optional[str]:
        """Получить текущее состояние пользователя"""
        return self.user_states.get(user_id)

    # Методы для работы с пользовательскими данными
    async def update_user_data(self, user_id: int, data: Dict[str, Any]):
        """Обновить данные пользователя"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id].update(data)

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Получить данные пользователя"""
        return self.user_data.get(user_id, {})

    async def process_message(self, message_data: Dict[str, Any]):
        message = Message(message_data)
        message._bot = self
        
        logging.info(f"New message from {message.chat.id}: {message.text}")

        if message.text and message.text.startswith('/'):
            command = message.text.split()[0].lower()
            command = command.split('@')[0]
            
            for handler in self.handlers:
                try:
                    if handler.get('commands'):
                        if any(command == f'/{cmd}'.lower() for cmd in handler['commands']):
                            await handler['func'](message)
                            return
                except Exception as e:
                    logging.error(f"Error in handler: {e}")

        for handler in self.handlers:
            try:
                if handler.get('content_types') and not handler.get('commands'):
                    if message.content_type in handler['content_types']:
                        await handler['func'](message)
                        return
            except Exception as e:
                logging.error(f"Error in content handler: {e}")

    async def process_callback(self, callback_data: Dict[str, Any]):
        callback = CallbackQuery(callback_data)
        callback._bot = self
        
        logging.info(f"New callback from {callback.from_user['id']}: {callback.data}")

        for handler in self.callback_handlers:
            try:
                await handler(callback)
            except Exception as e:
                logging.error(f"Error in callback handler: {e}")

    async def process_updates(self):
        offset = None
        try:
            while True:
                updates = await self.get_updates(offset)
                if not updates.get('ok'):
                    await asyncio.sleep(5)
                    continue
                    
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        await self.process_message(update['message'])
                    elif 'callback_query' in update:
                        await self.process_callback(update['callback_query'])
        except Exception as e:
            logging.error(f"Error in process_updates: {e}")
        finally:
            await self.close_session()

    async def run_polling(self):
        """Асинхронный запуск бота"""
        await self.create_session()
        try:
            me = await self.get_me()
            logging.info(f"Starting bot @{me['result']['username']}")
            await self.process_updates()
        except Exception as e:
            logging.error(f"Fatal error: {e}")
        finally:
            await self.close_session()

    def run_polling_sync(self):
        """Синхронный запуск бота"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_polling())
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        finally:
            loop.close()