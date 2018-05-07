import hashlib
import hmac
import json
import logging

from .api_request_sender import ApiRequestSender
from .bot_configuration import BotConfiguration
from .consts import VIBER_BOT_API_URL, VIBER_BOT_USER_AGENT
from .message_sender import MessageSender
from .messages.message import Message
from .viber_requests import create_request


class Api(object):

	def __init__(self, bot_configuration):
		"""Api __init__ method.

		:type bot_configuration: viberbot.api.bot_configuration.BotConfiguration
		:raises: AssertionError
		"""
		assert isinstance(bot_configuration, BotConfiguration), \
			(
				"'bot_configuration' should be a type "
				"of 'viberbot.api.bot_configuration.BotConfiguration', "
				"not '{}'".format(type(bot_configuration))
			)

		self._logger = logging.getLogger('viber.bot.api')
		self._bot_configuration = bot_configuration
		self._request_sender = ApiRequestSender(
			self._logger, VIBER_BOT_API_URL,
			bot_configuration, VIBER_BOT_USER_AGENT)
		self._message_sender = MessageSender(
			self._logger, self._request_sender, bot_configuration)

	@property
	def name(self):
		"""Returns bot name.

		:rtype: str
		"""
		return self._bot_configuration.name

	@property
	def avatar(self):
		"""Returns link to bot's avatar.

		:rtype: str
		"""
		return self._bot_configuration.avatar

	def set_webhook(self, url, webhook_events=None, is_inline=False):
		"""Returns a list of registred event types.

		:param url: web server url
		:type url: str
		:param webhook_events: optional subscribed events list
		:type webhook_events: list[str]
		:type is_inline: bool
		:raises: TypeError, Exception
		:rtype: list
		"""
		self._logger.debug(u"setting webhook to url: {0}".format(url))
		return self._request_sender.set_webhook(
			url, webhook_events, is_inline)

	def unset_webhook(self):
		"""Unsets registred event types.

		:rtype: None
		"""
		self._logger.debug("unsetting webhook")
		return self._request_sender.set_webhook('')

	def get_online(self, ids):
		"""Returns online status for given Viber user ids.

		:type ids: list[str]
		:raises: AssertionError, TypeError, Exception
		:rtype: list[dict]
		"""
		return self._request_sender.get_online_status(ids)

	def get_user_details(self, user_id):
		"""Returns user's account details for given user id.

		:type user_id: str
		:raises: TypeError
		:rtype: dict
		"""
		return self._request_sender.get_user_details(user_id)

	def get_account_info(self):
		"""Fetches account's details from Viber API.

		:returns: account's details
		:rtype: dict
		"""
		self._logger.debug("requesting account info")
		account_info = self._request_sender.get_account_info()
		self._logger.debug(u"received account info: {0}".format(account_info))
		return account_info

	def verify_signature(self, request_data, signature):
		"""Verifies request data signature with given hex signature.

		Uses HMAC algorithm.

		:type request_data: dict
		:type signature: str
		:rtype: bool
		"""
		return signature == self._calculate_message_signature(request_data)

	def parse_request(self, request_data):
		"""Decodes request JSON to Python objects.

		:type request_data: str
		:raises: json.JSONDecodeError
		:rtype: dict
		"""
		self._logger.debug("parsing request")
		request_dict = json.loads(request_data)
		request = create_request(request_dict)
		self._logger.debug(u"parsed request={0}".format(request))
		return request

	def send_messages(self, to, messages, chat_id=None):
		"""Returns list of message tokens of the messages sent.

		:param to: Viber user id
		:type to: str
		:param messages: list of Message objects to be sent
		:type messages: list[viberbot.api.messages.Message]
		:param chat_id: Indicates that this is
			a message sent in inline conversation.
		:type chat_id: str
		:raises: TypeError
		:return: list of tokens of the sent messages
		:rtype: list
		"""
		self._logger.debug(
			"going to send messages: {0}, to: {1}".format(
				messages, to)
		)

		messages = self._validate_message_list(messages)

		return [
			self._message_sender.send_message(
				to, self._bot_configuration.name,
				self._bot_configuration.avatar, message,
				chat_id,
			) for message in messages
		]

	def post_messages_to_public_account(self, sender, messages):
		"""Returns list of message tokens of the messages sent.

		:param sender: viber user id
		:type sender: str
		:param messages: Message object list
		:type messages: list[viberbot.api.messages.Message]
		:raises: TypeError
		:rtype: list
		"""
		if not isinstance(sender, str):
			raise TypeError(
				"'sender' should be a type of 'str', not '{}'".format(
					type(sender))
			)

		messages = self._validate_message_list(messages)

		return [
			self._message_sender.post_to_public_account(
				sender, self._bot_configuration.name,
				self._bot_configuration.avatar, message,
			) for message in messages
		]

	def _calculate_message_signature(self, message):
		"""Calculates message's HMAC signature.

		:type message: dict
		:rtype: str
		"""
		return hmac.new(
			bytes(self._bot_configuration.auth_token.encode('ascii')),
			msg=message,
			digestmod=hashlib.sha256
		).hexdigest()

	def _validate_message_list(self, messages):
		"""Validates messages param.

		Messages could be either a single message instance or message list.
		If param is single message, returns it as a list of message.

		:type messages: list
		:raises: TypeError
		:returns: validated message list
		:rtype: list
		"""
		if not isinstance(messages, (Message, list)):
			raise TypeError(
				"'messages' should be either "
				"a type of 'viberbot.api.messages.message.Message' "
				"or 'list', not '{}'".format(type(messages))
			)

		if isinstance(messages, Message):
			messages = [messages]

		return messages
