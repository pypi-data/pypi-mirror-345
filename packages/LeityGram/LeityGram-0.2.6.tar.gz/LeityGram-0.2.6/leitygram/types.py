from typing import Dict, List, Optional, Union, Any

class Message:
    def __init__(self, data: Dict):
        self.chat = self.Chat(data.get('chat', {}))
        self.text = data.get('text')
        self.message_id = data.get('message_id')
        self.from_user = self.User(data['from']) if 'from' in data else None
        self.content_type = self._detect_content_type(data)
        self._bot = None
        
    class Chat:
        def __init__(self, data: Dict):
            self.id = data['id']
            self.type = data.get('type')
            self.title = data.get('title')
            self.username = data.get('username')
            
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
    def __init__(self, data: Dict):
        self.id = data['id']
        self.data = data.get('data')
        self.message = Message(data['message']) if 'message' in data else None
        self.from_user = User(data['from']) if 'from' in data else None
        self._bot = None
        
    async def answer(self, text: Optional[str] = None, show_alert: bool = False, **kwargs):
        await self._bot.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            **kwargs
        )

class User:
    def __init__(self, data: Dict):
        self.id = data['id']
        self.username = data.get('username')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.language_code = data.get('language_code')

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