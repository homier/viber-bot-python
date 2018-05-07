import json
import logging
import traceback

import requests

from . import consts

from .bot_configuration import BotConfiguration


class ApiRequestSender(object):

	def __init__(self, logger, viber_bot_api_url,
				 bot_configuration, viber_bot_user_agent):
		"""ApiRequestSender __init__ method.

		:type logger: logging.Logger
		:param viber_bot_api_url: bot api url
		:type viber_bot_api_url: str
		:type bot_confugration: viberbot.api.bot_confugration.BotConfiguration
		:type viber_bot_user_agent: str
		:raises: AssertionError
		"""
		assert isinstance(logger, logging.Logger)
		assert isinstance(viber_bot_api_url, str)
		assert isinstance(bot_configuration, BotConfiguration)
		assert isinstance(viber_bot_user_agent, str)

		self._logger = logger
		self._viber_bot_api_url = viber_bot_api_url
		self._bot_configuration = bot_configuration
		self._user_agent = viber_bot_user_agent

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
		payload = dict(
			auth_token=self._bot_configuration.auth_token,
			is_inline=is_inline,
			url=url,
		)

		if webhook_events is not None:
			payload['event_types'] = self._validate_webhook_event_list(
				webhook_events)

		result = self.post_request(
			endpoint=consts.API_ENDPOINT_SET_WEBHOOK,
			payload=payload)

		if not result['status'] == 0:
			raise Exception(
				"failed with status: {0}, message: {1}".format(
					result['status'], result['status_message']))

		return result['event_types']

	def get_account_info(self):
		"""Fetches account's details from Viber API.

		:returns: account's details
		:rtype: dict
		"""
		payload=dict(auth_token=self._bot_configuration.auth_token)
		return self.post_request(
			endpoint=consts.API_ENDPOINT_GET_ACCOUNT_INFO,
			payload=payload)

	def post_request(self, endpoint, payload):
		"""Makes POST request to Viber API.

		:param endpoint: API endpoint (do not include base url path)
		:type endpoint: str
		:param payload: request payload
		:type payload: dict
		:raises: Exception, requests.RequestException
		:return: json decoded response from Viber API
		:rtype: dict
		"""
		try:
			payload = json.dumps(payload)
		except (json.JSONDecodeError, TypeError, ValueError):
			raise TypeError(
				"'payload' object has unserializable type: '{}'".format(
					type(payload))
			)

		try:
			headers = requests.utils.default_headers()
			headers.update({'User-Agent': self._user_agent})

			url = '{base}/{endpoint}'.format(
				base=self._viber_bot_api_url, endpoint=endpoint)

			response = requests.post(url, data=payload, headers=headers)
			response.raise_for_status()

			return response.json()
		except requests.RequestException as e:
			self._logger.error(
				"failed to post request to endpoint={0}, with payload={1}. "
				"error is: {2}".format(
					endpoint, payload, traceback.format_exc())
			)
			raise e
		except Exception as ex:
			self._logger.error(
				"unexpected Exception while trying to post request. "
				"error is: {0}".format(traceback.format_exc())
			)
			raise ex

	def get_online_status(self, ids=None):
		"""Returns online status for given Viber user ids.

		:type ids: list[str]
		:raises: AssertionError, TypeError, Exception
		:rtype: list
		"""
		assert ids is not None, "'ids' param could not equal to None"
		ids = self._validate_user_id_list(ids)

		payload = dict(
			auth_token=self._bot_configuration.auth_token,
			ids=ids,
		)

		result = self.post_request(
			endpoint=consts.API_ENDPOINT_GET_ONLINE,
			payload=payload)

		if not result['status'] == 0:
			raise Exception(
				"failed with status: {0}, message: {1}".format(
					result['status'], result['status_message'])
			)

		return result['users']

	def get_user_details(self, user_id):
		"""Returns user's account details for given user id.

		:type user_id: str
		:raises: TypeError
		:rtype: dict
		"""
		if not isinstance(user_id, str):
			raise TypeError(
				"'user_id' should be a type of 'str', not {}".format(
					type(user_id))
			)

		payload = dict(
			auth_token=self._bot_configuration.auth_token,
			id=user_id,
		)

		result = self.post_request(
			endpoint=consts.API_ENDPOINT_GET_USER_DETAILS,
			payload=payload)

		if not result['status'] == 0:
			raise Exception(
				"failed with status: {0}, message: {1}".format(
					result['status'], result['status_message'])
			)

		return result['user']

	def _validate_webhook_event_list(self, webhook_events):
		"""Validates webhook_event param.

		'webhook_events' could be either a signle event,
		or a list of the events.

		:type webhook_events: list
		:raises: TypeError
		:returns: validated webhook event list
		:rtype: list[str]
		"""

		if not isinstance(webhook_events, (str, list)):
			raise TypeError(
				"'webhook_events' should be either "
				"a type of 'str' or 'list', not '{}'".format(
					type(webhook_events))
			)

		if isinstance(webhook_events, str):
			webhook_events = [webhook_events]

		for event in webhook_events:
			if not isinstance(event, str):
				raise TypeError(
					"'event' ({}) should be a type of 'str', not '{}'".format(
						event, type(event)))

		return webhook_events

	def _validate_user_id_list(self, user_ids):
		"""Validates user_ids param.

		'user_ids' could be either a single item, or a list of the user_ids.

		:type user_ids: list[str]
		:raises: TypeError
		:returns: validated 'user_ids' list.
		:rtype: list[str]
		"""
		if not isinstance(user_ids, (str, list)):
			raise TypeError(
				"'user_ids' should be either "
				"a type of 'str' or 'list', not '{}'".format(
					type(user_ids))
			)

		if isinstance(user_ids, str):
			user_ids = [user_ids]

		for user_id in user_ids:
			if not isinstance(user_id, str):
				raise TypeError(
					"user_id ({}) should be a type of 'str', not '{}'".format(
						user_id, type(user_id))
				)

		return user_ids
