class Message:
    def __init__(self, data: Dict):
        self.chat = self.Chat(data['chat'])
        self.text = data.get('text')
        self.message_id = data['message_id']
        
    class Chat:
        def __init__(self, data: Dict):
            self.id = data['id']
            
    async def reply(self, text: str):
        await self._bot.send_message(self.chat.id, text)