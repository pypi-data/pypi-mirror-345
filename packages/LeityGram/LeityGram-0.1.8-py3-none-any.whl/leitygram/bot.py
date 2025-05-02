import aiohttp
import asyncio
import logging
from typing import Callable, Any, Dict, List, Optional, Union
from .types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LeityBot:
    def __init__(self, token: str, parse_mode: Optional[str] = None):
        self.token = token
        self.parse_mode = parse_mode
        self.handlers = []
        self.callback_handlers = []
        self.session = None
        self._me = None
        self.user_data = {}  # Хранение данных пользователя
        self.commands = {
            '/start': 'Начало работы с ботом',
            '/help': 'Помощь и список команд',
            '/test': 'Тестовая команда',
            '/keyboard': 'Показать клавиатуру',
            '/inline': 'Показать inline-кнопки'
        }

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
                logger.info(f"Bot info loaded: {self._me}")
        return self._me

    async def get_updates(self, offset: Optional[int] = None):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {'timeout': 30, 'allowed_updates': ['message', 'callback_query']}
        if offset:
            params['offset'] = offset
            
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

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
        if func:
            self.callback_handlers.append(func)
        else:
            def decorator(f):
                self.callback_handlers.append(f)
                return f
            return decorator

    # ===== Методы API =====
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
            logger.error(f"Error sending message: {e}")

    async def answer_callback_query(self, callback_query_id: str, **kwargs):
        params = {
            'callback_query_id': callback_query_id,
            **kwargs
        }

        url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # ===== Обработка обновлений =====
    async def process_updates(self):
        offset = None
        try:
            while True:
                updates = await self.get_updates(offset)
                if not updates.get('ok'):
                    logger.error(f"Error getting updates: {updates}")
                    await asyncio.sleep(5)
                    continue
                    
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        await self.process_message(update['message'])
                    elif 'callback_query' in update:
                        await self.process_callback(update['callback_query'])
        except Exception as e:
            logger.error(f"Error in process_updates: {e}")
        finally:
            await self.close_session()

async def process_message(self, message_data: Dict[str, Any]):
    message = Message(message_data)
    message._bot = self
    
    logger.info(f"New message from {message.chat.id}: {message.text}")

    # Сохраняем данные пользователя
    user_id = message.chat.id
    if user_id not in self.user_data:
        self.user_data[user_id] = {'message_count': 0}
    self.user_data[user_id]['message_count'] += 1

    if message.text and message.text.startswith('/'):
        # Извлекаем чистую команду (без параметров и имени бота)
        command_parts = message.text.split()[0].split('@')
        clean_command = command_parts[0].lower()

        for handler in self.handlers:
            try:
                if handler['commands']:
                    # Проверяем команды (учитываем / в начале)
                    if any(clean_command == f'/{cmd}'.lower() for cmd in handler['commands']):
                        await handler['func'](message)
                        return
            except Exception as e:
                logger.error(f"Error in handler: {e}")

    # Проверяем обработчики контента
    for handler in self.handlers:
        try:
            if handler['content_types'] and not handler['commands']:
                if message.content_type in handler['content_types']:
                    await handler['func'](message)
                    return
        except Exception as e:
            logger.error(f"Error in handler: {e}")

    # Если ни один обработчик не сработал
    if message.text and message.text.startswith('/'):
        await message.reply("Неизвестная команда. Введите /help для списка команд.")

    async def process_callback(self, callback_data: Dict[str, Any]):
        callback = CallbackQuery(callback_data)
        callback._bot = self
        
        logger.info(f"New callback from {callback.from_user['id']}: {callback.data}")

        for handler in self.callback_handlers:
            try:
                await handler(callback)
            except Exception as e:
                logger.error(f"Error in callback handler: {e}")

    async def run_polling(self):
        """Асинхронный запуск бота"""
        await self.create_session()
        try:
            me = await self.get_me()
            logger.info(f"Starting bot @{me['result']['username']}")
            await self.process_updates()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            await self.close_session()

    def run_polling_sync(self):
        """Синхронный запуск бота"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_polling())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            loop.close()