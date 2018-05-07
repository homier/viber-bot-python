import pkg_resources


VIBER_BOT_VERSION = pkg_resources.get_distribution('viberbot').version

VIBER_BOT_API_URL = "https://chatapi.viber.com/pa"
VIBER_BOT_USER_AGENT = "ViberBot-Python/{}".format(VIBER_BOT_VERSION)


API_EDNPOINT_SEND_MESSAGE = 'send_message'
API_ENDPOINT_GET_ACCOUNT_INFO = 'get_account_info'
API_ENDPOINT_GET_ONLINE = 'get_online'
API_ENDPOINT_GET_USER_DETAILS = 'get_user_details'
API_ENDPOINT_POST = 'post'
API_ENDPOINT_SET_WEBHOOK = 'set_webhook'
