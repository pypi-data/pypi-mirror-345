import requests
from typing import Callable, Dict

class LeityBot:
    def __init__(self, token: str):
        self.token = token
        self.handlers = []
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def message_handler(self, commands: list = None, text: str = None):
        def decorator(func: Callable):
            self.handlers.append((commands, text, func))
            return func
        return decorator

    def send_message(self, chat_id: int, text: str, reply_markup=None):
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        requests.post(self.base_url + 'sendMessage', json=data)

    def run(self):
        offset = 0
        while True:
            updates = requests.get(
                self.base_url + f'getUpdates?offset={offset}&timeout=30'
            ).json()
            
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

        for commands, text, handler in self.handlers:
            if commands and msg.text.startswith('/'):
                if any(msg.text[1:].split()[0] == cmd for cmd in commands):
                    handler(msg)
                    return
            elif text and text == msg.text:
                handler(msg)
                return