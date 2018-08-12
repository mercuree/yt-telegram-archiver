from pymongo import MongoClient
from urllib.parse import quote_plus
from src import config

if config.DB_USER and config.DB_PASSWORD and config.DB_SOCKET_PATH:
    uri = "mongodb://%s:%s@%s" % (
        quote_plus(config.DB_USER),
        quote_plus(config.DB_PASSWORD),
        config.DB_SOCKET_PATH
    )
    db_name = 'YoutubeBackuper'
elif config.MONGOLAB_URI:
    uri = config.MONGOLAB_URI
    db_name = uri.split('mongodb://')[1].split(':')[0]
else:
    raise Exception('No database credentials were found')

client = MongoClient(uri)

# db name
db = client[db_name]


def is_video_already_exists(video_id):
    doc = db.videos.find_one({
        'video_id': video_id
    })
    return bool(doc)


def insert_new_video(video_id, url, uploader, title):
    params = locals()
    db.videos.insert_one(params)


def get_channels():
    return db.channels.find({})
