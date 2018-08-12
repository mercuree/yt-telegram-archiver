from __future__ import unicode_literals
import youtube_dl


def my_hook(d):
    print()
    print(d['status'])
    print()
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'mp4',
    'postprocessors': [
        {'key': 'FFmpegMetadata'}
    ],
    'progress_hooks': [my_hook],
    'restrictfilenames': True,
    'writethumbnail': True,
    'outtmpl': '%(title)s-%(id)s.%(ext)s'
}


def get_video_info(url):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False, process=False)


def download_from_youtube(info):

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.process_ie_result(info)

        filename = ydl.prepare_filename(info)
        return filename


