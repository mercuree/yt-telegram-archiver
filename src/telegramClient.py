
from telethon import TelegramClient, events

from src.youtube_downloader import download_from_youtube, get_video_info
from src import config
from src import db
from src import myhelpers
import logging
import os

import asyncio
import concurrent.futures

# Use your own values here
api_id = config.TELEGRAM_API_ID
api_hash = config.TELEGRAM_API_HASH
bot_token = config.TELEGRAM_BOT_TOKEN

loop = asyncio.get_event_loop()

executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=1
)

# For instance, show only warnings and above
#logging.getLogger('telethon').setLevel(level=logging.DEBUG)


class TelegramDownloaderAndSender(object):
    def __init__(self, url):
        self.url = url
        self.client = None
        self.video_info = None
        self.upload_progress = 'Загрузка еще не началась'

    def start(self):
        self.video_info = self.get_info()
        if self.video_info:
            loop.run_until_complete(
                self.process()
            )

    async def process(self):
        self.client = TelegramClient('YoutubeBackuper', api_id, api_hash)
        self.client.add_event_handler(self.handler, event=events.NewMessage)
        await self.send_backup_video()

    async def send_backup_video(self):
        vi = self.video_info
        client = self.client
        callback = self.callback

        await client.start(bot_token=bot_token)

        start_msg = f'**url**: {vi["webpage_url"]}\n' \
                    f'**Title**: {vi["title"]}\n' \
                    f'**Description**: \n{vi["description"]}\n' \
                    f'**Duration**: {vi["duration"]}\n' \
                    f'**uploader**: {vi["uploader"]}\n'
        await client.send_message(config.TELEGRAM_USERNAME, start_msg)

        # run task inside another thread, so we can emulate async behaviour
        # https://pymotw.com/3/asyncio/executors.html
        completed, pending = await asyncio.wait([loop.run_in_executor(executor, self.task, vi)])
        filename, thumbnail_path = [t.result() for t in completed][0]

        channel_to_send = config.PROD_ENV and config.TELEGRAM_ARCHIVE_CHANNEL_USERNAME or config.TELEGRAM_USERNAME
        await client.send_file(
            channel_to_send,
            file=filename,
            progress_callback=callback,
            allow_cache=False,
            thumb=thumbnail_path,
            caption=f'{vi["title"]}\nКанал: {vi["uploader"]}\n'
                    f'Дата: {vi["upload_date"]}\n{vi["webpage_url"]}',
            attributes=[
                myhelpers.get_video_document_attribute(filename)
            ],
            force_document=True  # disable hachoir check, may break video sending as video
        )
        # clear files
        os.remove(thumbnail_path)
        os.remove(filename)
        if config.PROD_ENV:
            db.insert_new_video(vi['id'], vi['webpage_url'], vi['uploader'], vi['title'])
        await client.send_message(config.TELEGRAM_USERNAME, 'Finished.')

        await client.disconnect()

    @staticmethod
    def task(video_info):
        # this task works inside separated thread

        filename = download_from_youtube(video_info)
        thumbnail_path = filename.replace('.mp4', '.jpg')

        # create thumbnail with 100px
        myhelpers.prepare_thumbnail_image(thumbnail_path)
        logging.debug('thumbnail path: %s' % thumbnail_path)
        return filename, thumbnail_path

    def get_info(self):
        url = self.url
        video_info = get_video_info(url)
        if url != config.TEST_VIDEO_URL and db.is_video_already_exists(video_info.get('id')):
            logging.warn('Video with id %s already exists' % video_info.get('id'))
            return False

        if video_info.get('is_live') is True:
            logging.warn('Video %s is live streaming. Skip' % video_info.get('id'))
            return False

        return video_info

    def callback(self, a, b):
        self.upload_progress = '%skb of %skb' % (a / 1024, b / 1024)

        logging.info(self.upload_progress)

    async def handler(self, event):
        # dummy function
        if event.message.sender.is_self is False:
            await self.client.send_message(config.TELEGRAM_USERNAME, self.upload_progress)
            print(event)
        else:
            logging.warning('Another session is running')


def main(url=config.TEST_VIDEO_URL):
    tdas = TelegramDownloaderAndSender(url)
    tdas.start()


if __name__ == '__main__':
    main()
