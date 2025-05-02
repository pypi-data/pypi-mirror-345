import aiohttp
import asyncio
import logging
from typing import Callable, Any, Dict, List, Optional, Union
from .types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove

class LeityBot:
    def __init__(self, token: str, parse_mode: Optional[str] = None, brawl_stars_token: Optional[str] = None):
        self.token = token
        self.parse_mode = parse_mode
        self.brawl_stars_token = brawl_stars_token  # Теперь это будет работать
        self.handlers = []
        self.callback_handlers = []
        self.session = None
        self._me = None
        self.user_data = {}
        self.user_states = {}
        self.commands = {} 

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

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': self.parse_mode,
        }
        
        # Обработка reply_markup
        if 'reply_markup' in kwargs:
            if hasattr(kwargs['reply_markup'], 'to_dict'):
                params['reply_markup'] = kwargs['reply_markup'].to_dict()
            elif hasattr(kwargs['reply_markup'], 'to_json'):
                params['reply_markup'] = kwargs['reply_markup'].to_json()
            else:
                params['reply_markup'] = kwargs['reply_markup']
        
        # Добавляем остальные параметры
        params.update({k: v for k, v in kwargs.items() if k != 'reply_markup'})
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

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
        }
        
        if 'reply_markup' in kwargs:
            if hasattr(kwargs['reply_markup'], 'to_dict'):
                params['reply_markup'] = kwargs['reply_markup'].to_dict()
            else:
                params['reply_markup'] = kwargs['reply_markup']
        
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

    async def forward_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], message_id: int, disable_notification: bool = False):
        url = f"https://api.telegram.org/bot{self.token}/forwardMessage"
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def copy_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], message_id: int, caption: Optional[str] = None, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/copyMessage"
        params = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # Методы для работы с медиа
    async def send_audio(self, chat_id: Union[int, str], audio: str, caption: Optional[str] = None, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendAudio"
        params = {
            'chat_id': chat_id,
            'audio': audio,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_video(self, chat_id: Union[int, str], video: str, caption: Optional[str] = None, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendVideo"
        params = {
            'chat_id': chat_id,
            'video': video,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_animation(self, chat_id: Union[int, str], animation: str, caption: Optional[str] = None, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendAnimation"
        params = {
            'chat_id': chat_id,
            'animation': animation,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_voice(self, chat_id: Union[int, str], voice: str, caption: Optional[str] = None, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendVoice"
        params = {
            'chat_id': chat_id,
            'voice': voice,
            'caption': caption,
            'parse_mode': self.parse_mode,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_video_note(self, chat_id: Union[int, str], video_note: str, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendVideoNote"
        params = {
            'chat_id': chat_id,
            'video_note': video_note,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_media_group(self, chat_id: Union[int, str], media: List[Dict], **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendMediaGroup"
        params = {
            'chat_id': chat_id,
            'media': media,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_location(self, chat_id: Union[int, str], latitude: float, longitude: float, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendLocation"
        params = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_venue(self, chat_id: Union[int, str], latitude: float, longitude: float, title: str, address: str, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendVenue"
        params = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'title': title,
            'address': address,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_contact(self, chat_id: Union[int, str], phone_number: str, first_name: str, **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendContact"
        params = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_poll(self, chat_id: Union[int, str], question: str, options: List[str], **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendPoll"
        params = {
            'chat_id': chat_id,
            'question': question,
            'options': options,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def send_dice(self, chat_id: Union[int, str], **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendDice"
        params = {
            'chat_id': chat_id,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # Методы для работы с чатами
    async def get_chat(self, chat_id: Union[int, str]):
        url = f"https://api.telegram.org/bot{self.token}/getChat"
        params = {'chat_id': chat_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def get_chat_administrators(self, chat_id: Union[int, str]):
        url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators"
        params = {'chat_id': chat_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def get_chat_members_count(self, chat_id: Union[int, str]):
        url = f"https://api.telegram.org/bot{self.token}/getChatMembersCount"
        params = {'chat_id': chat_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def get_chat_member(self, chat_id: Union[int, str], user_id: int):
        url = f"https://api.telegram.org/bot{self.token}/getChatMember"
        params = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def set_chat_title(self, chat_id: Union[int, str], title: str):
        url = f"https://api.telegram.org/bot{self.token}/setChatTitle"
        params = {
            'chat_id': chat_id,
            'title': title
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def set_chat_description(self, chat_id: Union[int, str], description: str):
        url = f"https://api.telegram.org/bot{self.token}/setChatDescription"
        params = {
            'chat_id': chat_id,
            'description': description
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def pin_chat_message(self, chat_id: Union[int, str], message_id: int, disable_notification: bool = False):
        url = f"https://api.telegram.org/bot{self.token}/pinChatMessage"
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'disable_notification': disable_notification
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def unpin_chat_message(self, chat_id: Union[int, str], message_id: Optional[int] = None):
        url = f"https://api.telegram.org/bot{self.token}/unpinChatMessage"
        params = {'chat_id': chat_id}
        if message_id:
            params['message_id'] = message_id
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def unpin_all_chat_messages(self, chat_id: Union[int, str]):
        url = f"https://api.telegram.org/bot{self.token}/unpinAllChatMessages"
        params = {'chat_id': chat_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def leave_chat(self, chat_id: Union[int, str]):
        url = f"https://api.telegram.org/bot{self.token}/leaveChat"
        params = {'chat_id': chat_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # Методы для работы с файлами
    async def get_file(self, file_id: str):
        url = f"https://api.telegram.org/bot{self.token}/getFile"
        params = {'file_id': file_id}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def download_file(self, file_path: str):
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        async with self.session.get(url) as resp:
            return await resp.read()

    # Методы для работы с настройками бота
    async def set_my_commands(self, commands: List[Dict]):
        url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
        params = {'commands': commands}
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def get_my_commands(self):
        url = f"https://api.telegram.org/bot{self.token}/getMyCommands"
        async with self.session.post(url) as resp:
            return await resp.json()

    async def delete_my_commands(self):
        url = f"https://api.telegram.org/bot{self.token}/deleteMyCommands"
        async with self.session.post(url) as resp:
            return await resp.json()

    # Методы для работы с вебхуками
    async def set_webhook(self, url: str, certificate: Optional[str] = None, **kwargs):
        params = {
            'url': url,
            **kwargs
        }
        if certificate:
            with open(certificate, 'rb') as cert_file:
                files = {'certificate': cert_file}
                async with self.session.post(
                    f"https://api.telegram.org/bot{self.token}/setWebhook",
                    data=params,
                    files=files
                ) as resp:
                    return await resp.json()
        else:
            async with self.session.post(
                f"https://api.telegram.org/bot{self.token}/setWebhook",
                json=params
            ) as resp:
                return await resp.json()

    async def delete_webhook(self):
        url = f"https://api.telegram.org/bot{self.token}/deleteWebhook"
        async with self.session.post(url) as resp:
            return await resp.json()

    async def get_webhook_info(self):
        url = f"https://api.telegram.org/bot{self.token}/getWebhookInfo"
        async with self.session.post(url) as resp:
            return await resp.json()

    # Методы для работы с платежами (если нужно)
    async def send_invoice(self, chat_id: Union[int, str], title: str, description: str, 
                         payload: str, provider_token: str, currency: str, 
                         prices: List[Dict], **kwargs):
        url = f"https://api.telegram.org/bot{self.token}/sendInvoice"
        params = {
            'chat_id': chat_id,
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'currency': currency,
            'prices': prices,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # Дополнительные методы
    async def close(self):
        url = f"https://api.telegram.org/bot{self.token}/close"
        async with self.session.post(url) as resp:
            return await resp.json()

    async def log_out(self):
        url = f"https://api.telegram.org/bot{self.token}/logOut"
        async with self.session.post(url) as resp:
            return await resp.json()

    async def create_giveaway(
        self,
        chat_id: Union[int, str],
        prize_description: str,
        winner_count: int,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        **kwargs
    ):
        """
        Создает розыгрыш в чате.
        :param chat_id: ID чата
        :param prize_description: Описание приза
        :param winner_count: Количество победителей
        :param start_date: Дата начала (Unix timestamp)
        :param end_date: Дата окончания (Unix timestamp)
        :param kwargs: Доп. параметры (selective, only_new_members и т.д.)
        """
        url = f"https://api.telegram.org/bot{self.token}/createGiveaway"
        params = {
            "chat_id": chat_id,
            "prize_description": prize_description,
            "winner_count": winner_count,
            **({"start_date": start_date} if start_date else {}),
            **({"end_date": end_date} if end_date else {}),
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def stop_giveaway(
        self,
        chat_id: Union[int, str],
        message_id: int,
        winner_count: Optional[int] = None,
        **kwargs
    ):
        """
        Останавливает розыгрыш и выбирает победителей.
        :param chat_id: ID чата
        :param message_id: ID сообщения с розыгрышем
        :param winner_count: Количество победителей (если не указано, берется из розыгрыша)
        """
        url = f"https://api.telegram.org/bot{self.token}/stopGiveaway"
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            **({"winner_count": winner_count} if winner_count else {}),
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 2. Telegram Stars (Платежи звездами) ===
    async def send_stars(
        self,
        chat_id: Union[int, str],
        amount: int,
        **kwargs
    ):
        """
        Отправляет звезды пользователю.
        :param chat_id: ID чата
        :param amount: Количество звезд (минимум 1)
        :param kwargs: Доп. параметры (custom_payload, reply_markup и т.д.)
        """
        url = f"https://api.telegram.org/bot{self.token}/sendStars"
        params = {
            "chat_id": chat_id,
            "amount": amount,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def refund_star_payment(
        self,
        user_id: int,
        telegram_payment_charge_id: str,
        **kwargs
    ):
        """
        Возвращает звезды пользователю.
        :param user_id: ID пользователя
        :param telegram_payment_charge_id: ID платежа
        """
        url = f"https://api.telegram.org/bot{self.token}/refundStarPayment"
        params = {
            "user_id": user_id,
            "telegram_payment_charge_id": telegram_payment_charge_id,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 3. Bot Commands v2 (Команды бота с scope) ===
    async def set_my_commands_v2(
        self,
        commands: List[Dict],
        scope: Optional[Dict] = None,
        language_code: Optional[str] = None,
    ):
        """
        Устанавливает команды бота с учетом scope (чаты, группы, приватные чаты).
        :param commands: Список команд [{"command": "start", "description": "Start bot"}]
        :param scope: Область действия ({"type": "all_private_chats"})
        :param language_code: Код языка (например, "en", "ru")
        """
        url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
        params = {
            "commands": commands,
            **({"scope": scope} if scope else {}),
            **({"language_code": language_code} if language_code else {}),
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    async def delete_my_commands_v2(
        self,
        scope: Optional[Dict] = None,
        language_code: Optional[str] = None,
    ):
        """
        Удаляет команды бота для определенного scope.
        """
        url = f"https://api.telegram.org/bot{self.token}/deleteMyCommands"
        params = {
            **({"scope": scope} if scope else {}),
            **({"language_code": language_code} if language_code else {}),
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 4. Business Messages (Бизнес-аккаунты) ===
    async def send_business_message(
        self,
        business_connection_id: str,
        chat_id: Union[int, str],
        text: str,
        **kwargs
    ):
        """
        Отправляет сообщение в бизнес-чат.
        :param business_connection_id: ID бизнес-подключения
        :param chat_id: ID чата
        :param text: Текст сообщения
        """
        url = f"https://api.telegram.org/bot{self.token}/sendBusinessMessage"
        params = {
            "business_connection_id": business_connection_id,
            "chat_id": chat_id,
            "text": text,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 5. Reaction (Реакции на сообщения) ===
    async def set_message_reaction(
        self,
        chat_id: Union[int, str],
        message_id: int,
        reaction: Optional[List[Dict]] = None,
        is_big: bool = False,
        **kwargs
    ):
        """
        Устанавливает реакцию на сообщение.
        :param chat_id: ID чата
        :param message_id: ID сообщения
        :param reaction: Список реакций [{"type": "emoji", "emoji": "👍"}]
        :param is_big: Увеличить реакцию (True/False)
        """
        url = f"https://api.telegram.org/bot{self.token}/setMessageReaction"
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            **({"reaction": reaction} if reaction else {}),
            "is_big": is_big,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 6. Inline Queries (Обновленные inline-методы) ===
    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: List[Dict],
        cache_time: int = 300,
        **kwargs
    ):
        """
        Отправляет результаты inline-запроса.
        :param inline_query_id: ID inline-запроса
        :param results: Список результатов
        :param cache_time: Время кеширования (сек)
        """
        url = f"https://api.telegram.org/bot{self.token}/answerInlineQuery"
        params = {
            "inline_query_id": inline_query_id,
            "results": results,
            "cache_time": cache_time,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 7. Chat Boost (Бусты чатов) ===
    async def get_chat_boosts(
        self,
        chat_id: Union[int, str],
        **kwargs
    ):
        """
        Получает информацию о бустах чата.
        """
        url = f"https://api.telegram.org/bot{self.token}/getChatBoosts"
        params = {
            "chat_id": chat_id,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

    # === 8. Stories (Истории) ===
    async def send_story(
        self,
        chat_id: Union[int, str],
        content: Dict,
        **kwargs
    ):
        """
        Отправляет историю (только для бизнес-аккаунтов).
        """
        url = f"https://api.telegram.org/bot{self.token}/sendStory"
        params = {
            "chat_id": chat_id,
            "content": content,
            **kwargs
        }
        async with self.session.post(url, json=params) as resp:
            return await resp.json()

async def get_brawl_stars_player(self, player_tag: str) -> Dict:
    """
    Получает статистику игрока по тегу.
    :param player_tag: Тег игрока (например, #ABC123)
    :return: Данные игрока (name, trophies, club, brawlers и т.д.)
    """
    if not self.brawl_stars_token:
        raise ValueError("Brawl Stars token not set!")
    
    url = f"https://api.brawlstars.com/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {self.brawl_stars_token}"}
    
    async with self.session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception(f"Brawl Stars API error: {resp.status} | {await resp.text()}")

async def get_brawl_stars_club(self, club_tag: str) -> Dict:
    """
    Получает данные клуба по тегу.
    :param club_tag: Тег клуба (например, #ABC123)
    :return: Данные клуба (name, trophies, members и т.д.)
    """
    if not self.brawl_stars_token:
        raise ValueError("Brawl Stars token not set!")
    
    url = f"https://api.brawlstars.com/v1/clubs/{club_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {self.brawl_stars_token}"}
    
    async with self.session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception(f"Brawl Stars API error: {resp.status} | {await resp.text()}")

async def get_brawl_stars_events(self) -> Dict:
    """
    Получает текущие события (ротация карт, режимы и т.д.).
    :return: Список событий.
    """
    if not self.brawl_stars_token:
        raise ValueError("Brawl Stars token not set!")
    
    url = "https://api.brawlstars.com/v1/events/rotation"
    headers = {"Authorization": f"Bearer {self.brawl_stars_token}"}
    
    async with self.session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception(f"Brawl Stars API error: {resp.status} | {await resp.text()}")

async def get_brawl_stars_brawler(self, brawler_id: int) -> Dict:
    """
    Получает информацию о бравлере по ID.
    :param brawler_id: ID бравлера (например, 16000000 для Shelly)
    :return: Данные бравлера (атака, ульт, гаджеты и т.д.)
    """
    if not self.brawl_stars_token:
        raise ValueError("Brawl Stars token not set!")
    
    url = f"https://api.brawlstars.com/v1/brawlers/{brawler_id}"
    headers = {"Authorization": f"Bearer {self.brawl_stars_token}"}
    
    async with self.session.get(url, headers=headers) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception(f"Brawl Stars API error: {resp.status} | {await resp.text()}")

async def get_brawl_stars_leaderboard(self, leaderboard_type: str = "players", limit: int = 10) -> Dict:
    """
    Получает топ игроков или клубов.
    :param leaderboard_type: "players" или "clubs"
    :param limit: Количество записей (макс. 200)
    :return: Топ игроков/клубов.
    """
    if not self.brawl_stars_token:
        raise ValueError("Brawl Stars token not set!")
    
    url = f"https://api.brawlstars.com/v1/rankings/{leaderboard_type}"
    headers = {"Authorization": f"Bearer {self.brawl_stars_token}"}
    params = {"limit": limit}
    
    async with self.session.get(url, headers=headers, params=params) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception(f"Brawl Stars API error: {resp.status} | {await resp.text()}")
            
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

    async def process_updates(self):
        """Основной цикл обработки обновлений"""
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

    async def process_message(self, message_data: Dict[str, Any]):
        """Обработка входящих сообщений"""
        message = Message(message_data, self)
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
        """Обработка callback-запросов"""
        callback = CallbackQuery(callback_data, self)
        callback._bot = self
        
        logging.info(f"New callback from {callback.from_user['id']}: {callback.data}")

        for handler in self.callback_handlers:
            try:
                await handler(callback)
            except Exception as e:
                logging.error(f"Error in callback handler: {e}")

    async def run_polling(self):
        """Запуск бота в режиме polling"""
        await self.create_session()
        try:
            me = await self.get_me()
            logging.info(f"Starting bot @{me['result']['username']}")
            await self.process_updates()
        except Exception as e:
            logging.error(f"Fatal error: {e}")
        finally:
            await self.close_session()

async def run_polling_sync(self):
    """Синхронный запуск бота (адаптированный для асинхронного вызова)"""
    try:
        await self.run_polling()  # Просто вызываем асинхронный run_polling
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")