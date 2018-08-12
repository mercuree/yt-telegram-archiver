import os


def get_required_env(name):
    val = os.environ.get(name)
    # check if required param is missing
    if not val:
        raise Exception("%s env is missing" % name)
    return val


APP_NAME = get_required_env('APP_NAME')

PROD_ENV = os.environ.get('PROD_ENV')

# use mongolab addon by default (it's free)
MONGOLAB_URI = os.environ.get('MONGODB_URI')

# Database credentials for custom mongodb
DB_USER = os.environ.get('MONGODB_USER')
DB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
DB_SOCKET_PATH = os.environ.get('MONGODB_SOCKET_PATH')

# Telegram bot token (generated via @botfather)
TELEGRAM_BOT_TOKEN = get_required_env('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_ID = get_required_env('TELEGRAM_API_ID')
TELEGRAM_API_HASH = get_required_env('TELEGRAM_API_HASH')

TELEGRAM_USERNAME = get_required_env('TELEGRAM_USERNAME')

TELEGRAM_ARCHIVE_CHANNEL_USERNAME = get_required_env('TELEGRAM_ARCHIVE_CHANNEL_USERNAME')

PUBSUBHUB_SECRET_PART = os.environ.get('PUBSUBHUB_SECRET') or '22600671384'

FLASK_SECRET = get_required_env('FLASK_SECRET')

TEST_VIDEO_URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'
