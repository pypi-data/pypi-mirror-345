from typing import Dict, List, Optional, Union, Any

class Message:
    def __init__(self, data: Dict, bot_instance=None):
        self.chat = self.Chat(data['chat']) if 'chat' in data else None
        self.text = data.get('text')
        self.message_id = data.get('message_id')
        self.from_user = User(data['from']) if 'from' in data else None
        self.content_type = self._detect_content_type(data)
        self._bot = bot_instance  # Устанавливаем ссылку на бота при создании

    async def edit_text(self, text: str, **kwargs):
        """Редактирует текст сообщения"""
        if not self._bot:
            raise ValueError("Bot instance not set")
            
        params = {
            'chat_id': self.chat.id,
            'message_id': self.message_id,
            'text': text,
            'parse_mode': self._bot.parse_mode,
            **kwargs
        }
        
        if 'reply_markup' in kwargs and hasattr(kwargs['reply_markup'], 'to_json'):
            params['reply_markup'] = kwargs['reply_markup'].to_json()

        url = f"https://api.telegram.org/bot{self._bot.token}/editMessageText"
        async with self._bot.session.post(url, json=params) as resp:
            return await resp.json()
        
    class Chat:
        def __init__(self, data: Dict):
            self.id = data['id']
            self.type = data.get('type')
            self.title = data.get('title')
            self.username = data.get('username')
            
    def _detect_content_type(self, data: Dict) -> str:
        # Пример реализации определения типа контента
        if 'text' in data:
            return 'text'
        elif 'photo' in data:
            return 'photo'
        elif 'video' in data:
            return 'video'
        # Добавьте другие типы контента по необходимости
        return 'unknown'

    async def reply(self, text: str, **kwargs):
        """Отправляет ответ на сообщение"""
        if not self._bot:
            raise ValueError("Bot instance not set")
        return await self._bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_to_message_id=self.message_id,
            **kwargs
        )
        
    async def edit_text(self, text: str, **kwargs):
        """Редактирует текст сообщения"""
        if not self._bot:
            raise ValueError("Bot instance not set")
        return await self._bot.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            **kwargs
        )
        
class User:
    def __init__(self, data: Dict):
        if isinstance(data, dict):
            self.id = data.get('id')
            self.username = data.get('username')
            self.first_name = data.get('first_name')
            self.last_name = data.get('last_name')
            self.language_code = data.get('language_code')
        else:
            # Если передается уже объект User
            self.id = getattr(data, 'id', None)
            self.username = getattr(data, 'username', None)
            self.first_name = getattr(data, 'first_name', None)
            self.last_name = getattr(data, 'last_name', None)
            self.language_code = getattr(data, 'language_code', None)
    
    def __getitem__(self, key):
        # Для обратной совместимости с кодом, который использует user как словарь
        return getattr(self, key, None)
    
    def get(self, key, default=None):
        # Аналог dict.get()
        return getattr(self, key, default)
            
    def _detect_content_type(self, data: Dict) -> str:
        if 'text' in data:
            return 'text'
        elif 'photo' in data:
            return 'photo'
        elif 'document' in data:
            return 'document'
        elif 'audio' in data:
            return 'audio'
        elif 'video' in data:
            return 'video'
        elif 'voice' in data:
            return 'voice'
        elif 'sticker' in data:
            return 'sticker'
        return 'unknown'
    
    async def reply(self, text: str, **kwargs):
        await self._bot.send_message(self.chat.id, text, **kwargs)
        
    async def delete(self):
        await self._bot.delete_message(self.chat.id, self.message_id)

class CallbackQuery:
    def __init__(self, data: Dict, bot_instance=None):
        self.id = data['id']
        self.data = data.get('data')
        self.message = Message(data['message'], bot_instance) if 'message' in data else None
        self.from_user = User(data['from']) if 'from' in data else None
        self._bot = bot_instance  # Устанавливаем ссылку на бота
        
        # Передаем ссылку на бота в сообщение
        if self.message:
            self.message._bot = self._bot
        
    async def answer(self, text: Optional[str] = None, show_alert: bool = False, **kwargs):
        await self._bot.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            **kwargs
        )

class ReplyKeyboardMarkup:
    def __init__(self, resize_keyboard: bool = True, one_time_keyboard: bool = False):
        self.keyboard = []
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        
    def add(self, *buttons: str, row_width: int = 1):
        if row_width == 1:
            self.keyboard.append([button for button in buttons])
        else:
            for i in range(0, len(buttons), row_width):
                self.keyboard.append(list(buttons[i:i+row_width]))
                
    def row(self, *buttons: str):
        self.keyboard.append([button for button in buttons])
        
    def to_json(self):
        return {
            'keyboard': self.keyboard,
            'resize_keyboard': self.resize_keyboard,
            'one_time_keyboard': self.one_time_keyboard
        }

class ReplyKeyboardRemove:
    def __init__(self, selective: bool = False):
        self.selective = selective
        
    def to_json(self):
        return {
            'remove_keyboard': True,
            'selective': self.selective
        }

class InlineKeyboardMarkup:
    def __init__(self):
        self.inline_keyboard = []
        
    def add(self, text: str, callback_data: Optional[str] = None, 
            url: Optional[str] = None, row_width: int = 1):
        button = {'text': text}
        if callback_data:
            button['callback_data'] = callback_data
        if url:
            button['url'] = url
            
        if row_width == 1:
            self.inline_keyboard.append([button])
        else:
            if not self.inline_keyboard or len(self.inline_keyboard[-1]) >= row_width:
                self.inline_keyboard.append([])
            self.inline_keyboard[-1].append(button)
            
    def row(self, *buttons: Dict[str, str]):
        self.inline_keyboard.append([button for button in buttons])
        
    def to_json(self):
        return {'inline_keyboard': self.inline_keyboard}

class InlineKeyboardButton:
    def __init__(self, text: str, callback_data: Optional[str] = None, url: Optional[str] = None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        
    def to_dict(self):
        button = {'text': self.text}
        if self.callback_data:
            button['callback_data'] = self.callback_data
        if self.url:
            button['url'] = self.url
        return button