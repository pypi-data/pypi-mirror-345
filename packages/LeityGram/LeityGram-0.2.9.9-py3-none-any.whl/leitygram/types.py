from dataclasses import dataclass

@dataclass
class User:
    id: int
    first_name: str
    username: str = None

@dataclass
class Chat:
    id: int
    type: str

@dataclass
class Message:
    message_id: int
    from_user: User
    chat: Chat
    text: str