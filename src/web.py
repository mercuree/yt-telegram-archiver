# coding=utf-8


from flask import Flask, request, url_for, redirect
import logging
from src import telegramClient
from src import config
import threading
import requests
import feedparser
from datetime import datetime
from time import mktime

from wtforms import form
import wtforms.fields
from src import db
import flask_admin
from flask_admin import Admin, expose
from flask_admin.contrib.pymongo import ModelView
from flask_simplelogin import SimpleLogin, login_required, is_logged_in
from src import subscriptiontask

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

app.secret_key = config.FLASK_SECRET

SimpleLogin(app)


class MyAdminIndexView(flask_admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not is_logged_in('admin'):
            return redirect(url_for('simplelogin.login', next=request.url))
        return super(MyAdminIndexView, self).index()


class ChannelsForm(form.Form):
    channel_id = wtforms.fields.StringField('channel_id')
    uploader_name = wtforms.fields.StringField('uploader_name')


class ChannelsView(ModelView):
    column_list = ('channel_id', 'uploader_name', 'created')
    column_labels = {'channel_id': 'Channel ID', 'uploader_name': 'Channel name'}
    form = ChannelsForm

    def on_model_change(self, form, model, is_created):
        if is_created:
            subscriptiontask.subscribe_channel(model["channel_id"])
            model['created'] = datetime.utcnow()

    def is_accessible(self):
        return is_logged_in('admin')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('simplelogin.login', next=request.url))


admin = Admin(app, name=config.APP_NAME, template_mode='bootstrap3', index_view=MyAdminIndexView(),
              base_template='my_master.html')
admin.add_view(ChannelsView(db.db['channels']))


def download_and_send(url):
    threading.Thread(target=telegramClient.main, args=(url,)).start()


@app.route('/', methods=['GET'])
def go_to_admin():
    return redirect(url_for('admin.index'))


@app.route('/backupVideoFromUrl', methods=['GET', 'POST'])
@login_required
def backup_video_from_url():

    if request.method == 'GET':
        return '<!doctype html><html><body>' \
               '<form action="/backupVideoFromUrl" method="POST">' \
               '<input type="text" name="url" /> <input type="submit" value="Send"/>' \
               '</form>' \
               '</body></html>'

    url = request.form.get('url')
    if url:
        download_and_send(url)
        return 'In proccess'
    else:
        return 'url not set'


@app.route('/tasks/subscribepubsubhub', methods=['GET'])
def pubsubhubbub_subscribe():
    youtube_channel_id = request.args.get('channel_id')
    if not youtube_channel_id:
        logging.log(logging.WARNING, 'youtube channel id is missing')
        return 'not ok. youtube channel id is missing'

    data = {
        'hub.callback': 'https://{}.herokuapp.com/pubsubhub{}'.format(
            config.APP_NAME.lower(), config.PUBSUBHUB_SECRET_PART),
        'hub.mode': 'subscribe',
        'hub.topic': 'https://www.youtube.com/xml/feeds/videos.xml?channel_id=%s' % youtube_channel_id
    }
    resp = requests.post(
        url='https://pubsubhubbub.appspot.com/subscribe',
        data=data
    )

    if resp.status_code == 202:
        logging.log(logging.INFO, "Channel %s subscribed successfully" % youtube_channel_id)
        return 'ok'
    else:
        logging.log(logging.WARNING, "Channel %s subscribe FAILED" % youtube_channel_id)
        return 'not ok'


@app.route('/pubsubhub' + config.PUBSUBHUB_SECRET_PART, methods=['GET', 'POST'])
def pubsubhubbub_callback():

    # pubsubhub subscription verification procedure
    # http://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#verifysub
    if request.args.get('hub.challenge'):
        return request.args.get('hub.challenge')

    data = request.get_data()
    logging.log(logging.INFO, data)
    feed = feedparser.parse(data)

    for entry in feed['entries']:
        # if entry.yt_channelid not in allowed_channels:
        #     logging.log(logging.WARNING, "This channel not allowed: %s" % entry.author.uri)
        #     break

        tnow = datetime.utcnow()
        dt = datetime.fromtimestamp(mktime(entry.published_parsed))
        if (tnow - dt).total_seconds() / 3600 > 1:
            logging.log(logging.INFO, 'Too old entry %s' % entry.published)
            break

        else:
            logging.log(logging.INFO, 'Adding new youtube video %s' % entry.yt_videoid)
            download_and_send(entry.link)

        break

    return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)