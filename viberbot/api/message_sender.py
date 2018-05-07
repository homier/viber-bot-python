import json
import logging

from . import consts

from .api_request_sender import ApiRequestSender
from .bot_configuration import BotConfiguration
from .messages.message import Message


class MessageSender(object):

	def __init__(self, logger, request_sender, bot_configuration):
		"""MessageSender's class __init__ method.

		:type logger: logging.Logger
		:type request_sender: viberbot.api.api_request_sender.ApiRequestSender
		:type bot_configuration:
			viberbot.api.bot_configuration.BotConfiguration
		:raises: AssertionError
		"""
		assert isinstance(logger, logging.Logger), \
			"'logger' should be a type of 'logging.Logger', not '{}'".format(
				type(logger))
		assert isinstance(request_sender, ApiRequestSender), \
			(
				"'request_sender' should be a type "
				"of 'viberbot.api.api_request_sender.ApiRequestSender', "
				"not '{}'".format(type(request_sender))
			)
		assert isinstance(bot_configuration, BotConfiguration), \
			(
				"'bot_configuration' should be a type "
				"of 'viberbot.api.bot_configuration.BotConfiguration', "
				"not '{}'".format(type(bot_configuration))
			)

		self._logger = logger
		self._request_sender = request_sender
		self._bot_configuration = bot_configuration

	def send_message(self, to, sender_name, sender_avatar,
					 message, chat_id=None):
		"""Sends message to Viber API.

		:param to: message receiver
		:type to: str
		:param sender_name: sender name
		:type sender_name: str
		:param sender_avatar: link to sender avatar image
		:type sender_avatar: str
		:param message: message for sending
		:type message: viberbot.api.messages.Message
		:raises: TypeError
		:rtype: dict
		"""
		message = self.validate_message(message)

		payload = self._prepare_payload(
			message=message,
			receiver=to,
			sender_name=sender_name,
			sender_avatar=sender_avatar,
			chat_id=chat_id,
		)

		self._logger.debug(u"going to send message: {0}".format(payload))

		return self.request(
			consts.API_EDNPOINT_SEND_MESSAGE, payload)

	def post_to_public_account(self, sender, sender_name,
							   sender_avatar, message):
		"""Posts message to public account.

		:param sender: sender id
		:type sender: str
		:param sender_name: sender name
		:type sender_name: str
		:param sender_avatar: link to sender's avatar image.
		:type sender_avatar: str
		:param message: message for sending
		:type message: viberbot.api.messages.message.Message
		:raises: TypeError
		:rtype: dict
		"""
		message = self.validate_message(message)

		payload = self._prepare_payload(
			message=message,
			sender=sender,
			sender_name=sender_name,
			sender_avatar=sender_avatar,
		)

		self._logger.debug(u"going to send message: {0}".format(payload))

		return self.request(
			consts.API_ENDPOINT_POST, payload)

	def request(self, endpoint, payload):
		"""Makes API POST request.

		:param endpoint: viber's api endpoint, not included base url
		:type endpoint: str
		:param payload: request payload
		:type payload: dict
		:raises: Exception
		:returns: message token
		:rtype: str
		"""
		result = self._request_sender.post_request(
			endpoint, payload)

		if not result['status'] == 0:
			raise Exception(
				"failed with status: {0}, message: {1}".format(
					result['status'], result['status_message'])
			)

		return result['message_token']

	def _prepare_payload(self, message, sender_name, sender_avatar,
						 sender=None, receiver=None, chat_id=None):
		payload = {
			'auth_token': self._bot_configuration.auth_token,
			'from': sender,
			'receiver': receiver,
			'sender': {
				'name': sender_name,
				'avatar': sender_avatar
			},
			"chat_id": chat_id,
		}
		payload.update(message.to_dict())

		return self._remove_empty_fields(payload)

	def _remove_empty_fields(self, message):
		"""Removes empty key value pairs from dict.

		:type message: dict
		:rtype: dict
		"""
		return {k: v for k, v in message.items() if v is not None}

	def validate_message(self, message):
		"""Validates and returns message.

		:type message: viberbot.api.messages.message.Message
		:raises: TypeError, Exception
		:returns: validated message object
		:rtype message: viberbot.api.messages.message.Message
		"""
		if not isinstance(message, Message):
			raise TypeError(
				"'message' should be a type of "
				"'viberbot.api.messages.Message', not '{}'".format(
					type(message))
			)

		if not message.validate():
			self._logger.error(
				"failed validating message: {0}".format(message))
			raise Exception("failed validating message: {0}".format(message))

		return message
