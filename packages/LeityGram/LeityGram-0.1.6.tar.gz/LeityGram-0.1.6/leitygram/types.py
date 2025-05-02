from typing import Dict, List, Optional

class Message:
    def __init__(self, data: Dict):
        self.chat = self.Chat(data['chat'])
        self.text = data.get('text')
        self.message_id = data['message_id']
        self.content_type = self._detect_content_type(data)
        
    class Chat:
        def __init__(self, data: Dict):
            self.id = data['id']
            self.type = data.get('type')
            
    def _detect_content_type(self, data: Dict) -> str:
        if 'text' in data:
            return 'text'
        elif 'photo' in data:
            return 'photo'
        # Добавьте другие типы контента по необходимости
        return 'unknown'
    
    async def reply(self, text: str, **kwargs):
        await self._bot.send_message(self.chat.id, text, **kwargs)

class ReplyKeyboardMarkup:
    def __init__(self, resize_keyboard: bool = True):
        self.keyboard = []
        self.resize_keyboard = resize_keyboard
        
    def add(self, *buttons: str):
        self.keyboard.append([button for button in buttons])
        
    def to_json(self):
        return {
            'keyboard': self.keyboard,
            'resize_keyboard': self.resize_keyboard
        }

class InlineKeyboardMarkup:
    def __init__(self):
        self.inline_keyboard = []
        
    def add(self, text: str, callback_data: str):
        self.inline_keyboard.append([{
            'text': text,
            'callback_data': callback_data
        }])
        
    def to_json(self):
        return {'inline_keyboard': self.inline_keyboard}

class CallbackQuery:
    def __init__(self, data: Dict):
        self.id = data['id']
        self.data = data.get('data')
        self.message = Message(data['message']) if 'message' in data else None
        self.from_user = data['from']
        
    async def answer(self, text: Optional[str] = None, show_alert: bool = False):
        await self._bot.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert
        )