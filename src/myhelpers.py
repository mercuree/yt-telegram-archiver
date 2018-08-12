import hachoir
import hachoir.metadata
import hachoir.parser
from telethon.tl.types import DocumentAttributeVideo
from PIL import Image
import logging


def get_video_document_attribute(filename):
    # this part was partially copied from the telethon sources
    # added supports_streaming attribute, so we can watch video while it is downloading
    with hachoir.parser.createParser(filename) as parser:
        m = hachoir.metadata.extractMetadata(parser)
        doc = DocumentAttributeVideo(
            supports_streaming=True,
            w=m.get('width') if m.has('width') else 0,
            h=m.get('height') if m.has('height') else 0,
            duration=int(m.get('duration').seconds
                         if m.has('duration') else 0)
        )
    return doc


def prepare_thumbnail_image(filename):
    logging.info('Converting thumbnail...')
    image = Image.open(filename)
    image.thumbnail((100, image.height))
    image.save(filename)
    logging.info('Converting finished. image size is %sx%s' % (image.width, image.height))
