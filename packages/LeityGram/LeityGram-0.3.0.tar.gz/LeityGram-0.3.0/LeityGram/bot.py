import requests
import json
from typing import Callable, Dict, List
from .types import Message

class LeityBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.message_handlers = []
        self.command_handlers = {}
        self.text_handlers = {}

    def message_handler(self, commands: List[str] = None, text: str = None):
        def decorator(func: Callable):
            if commands:
                for cmd in commands:
                    self.command_handlers[cmd] = func
            if text:
                self.text_handlers[text] = func
            self.message_handlers.append(func)
            return func
        return decorator

    def reply(self, message: Message, text: str, reply_markup=None):
        data = {
            'chat_id': message.chat.id,
            'text': text,
            'reply_to_message_id': message.message_id
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup.to_dict())
        self._request('sendMessage', data)

    def _request(self, method: str, data: dict):
        url = f"{self.base_url}/{method}"
        response = requests.post(url, data=data)
        return response.json()

    def run(self, polling: bool = True):
        offset = 0
        while polling:
            updates = self._request('getUpdates', {'offset': offset, 'timeout': 30})
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                if 'message' in update:
                    self._process_message(update['message'])

    def _process_message(self, message_data: dict):
        msg = Message(
            message_id=message_data['message_id'],
            from_user=User(
                id=message_data['from']['id'],
                first_name=message_data['from']['first_name'],
                username=message_data['from'].get('username')
            ),
            chat=Chat(
                id=message_data['chat']['id'],
                type=message_data['chat']['type']
            ),
            text=message_data.get('text', '')
        )

        # Обработка команд
        if msg.text.startswith('/'):
            cmd = msg.text.split()[0][1:].lower()
            if cmd in self.command_handlers:
                self.command_handlers[cmd](msg)
                return

        # Обработка текста
        if msg.text in self.text_handlers:
            self.text_handlers[msg.text](msg)
            return

        # Общие обработчики
        for handler in self.message_handlers:
            handler(msg)