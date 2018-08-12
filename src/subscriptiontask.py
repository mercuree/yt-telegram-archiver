import requests
from src import config
import logging
import time
from src import db

if config.PROD_ENV:
    base_url = 'https://%s.herokuapp.com' % config.APP_NAME
else:
    base_url = 'http://127.0.0.1'


def subscribe_channel(channel_id):
    logging.info('task started for id %s' % channel_id)

    url = base_url + '/tasks/subscribepubsubhub'
    resp = requests.get(url, params={'channel_id': channel_id})

    logging.info('Subscribtion task for channel %s finished: %s' % (channel_id, resp.text))


def unsubscribe_channel(channel_id):
    url = base_url + '/tasks/subscribepubsubhub'
    resp = requests.get(url, params={'channel_id': channel_id, 'mode': 'unsubscribe'})

    logging.info('Channel %s was unsubscribed: %s' % (channel_id, resp.text))


def subscribe_task():
    channels = db.get_channels()
    for channel in channels:
        channel_id = channel['channel_id']
        subscribe_channel(channel_id)

        time.sleep(3)


if __name__ == '__main__':
    subscribe_task()
