from app import handler
from app.custom_models import AlmaTalks

from linebot.models import MessageEvent, TextMessage, ImageMessage, PostbackEvent

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    AlmaTalks.default_reply(event)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    AlmaTalks.phase_start(event)

@handler.add(PostbackEvent)
def handle_postback(event):
    if not event.postback.data.startswith('second_tone='):
        AlmaTalks.phase_intermediate(event)
    else:
        AlmaTalks.phase_finish(event)
