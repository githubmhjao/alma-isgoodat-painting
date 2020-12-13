from app import line_bot_api
from app.custom_models import CallDatabase, AlmaRenders, AlmaUtils

from linebot.models import TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, PostbackAction

def default_reply(user_id, text, token):
    name = line_bot_api.get_profile(user_id).display_name
    line_bot_api.reply_message(
        token,
        TextSendMessage(text=f"{name} said {text}")
        )

def phase_start(event):
    CallDatabase.init_table()
    if CallDatabase.check_record(event.source.user_id):
        _ = CallDatabase.update_record(event.source.user_id, 'message_id', event.message.id)
    else:
        _ = CallDatabase.init_record(event.source.user_id, event.message.id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=f"[1/5] Start DUAL TONE!\nPlease set original grayscale value:", 
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=PostbackAction(label=i * 50, data=f'original_grayscale={i * 50}')) for i in range(1, 5)]))
        )

def phase_intermediate(event):

    color_dict = {'#Red': '100:30:25',
                  '#Orange': '80:25:0', 
                  '#Yellow': '80:50:0', 
                  '#Green': '25:100:30', 
                  '#Blue': '30:25:100',
                  '#Purple': '50:0:80'}
    reply_dict = {'original_grayscale': '[2/5] Continue DUAL TONE!\nPlease set adjusted grayscale value:',
                  'adjusted_grayscale': '[3/5] Continue DUAL TONE!\nPlease select the 1st TONE:',
                  'first_tone': '[4/5] Just about to finish!\nPlease select the 2nd TONE:'}
    quick_button_dict = {'original_grayscale': [QuickReplyButton(action=PostbackAction(label=i * 50, data=f'adjusted_grayscale={i * 50}')) for i in range(1, 5)],
                         'adjusted_grayscale': [QuickReplyButton(action=PostbackAction(label=i, data=f'first_tone={j}')) for i, j in color_dict.items()],
                         'first_tone': [QuickReplyButton(action=PostbackAction(label=i, data=f'second_tone={j}')) for i, j in color_dict.items()]}

    user_id = event.source.user_id
    postback_data = event.postback.data
    current_phase = postback_data.split('=')[0]

    CallDatabase.update_record(user_id, current_phase, postback_data.split('=')[1])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=reply_dict[current_phase],
            quick_reply=QuickReply(
                items=quick_button_dict[current_phase]))
        )

def phase_finish(event):
    user_id = event.source.user_id
    postback_data = event.postback.data
    current_phase = postback_data.split('=')[0]

    CallDatabase.update_record(user_id, current_phase, postback_data.split('=')[1])
    record = CallDatabase.check_record(user_id)

    name = line_bot_api.get_profile(record[0]).display_name
    message_content = line_bot_api.get_message_content(record[1])
    im = AlmaUtils.get_image(message_content, event.reply_token)

    print('Running to_array...')
    im_array = AlmaRenders.to_array(im)
    print('Running simple gray...')
    im_array = AlmaRenders.simple_gray(im_array)
    print('Running leaky relu color curve...')
    im_array = AlmaRenders.lkre_color_curve(im_array, int(record[2]), int(record[3]))

    first_tone = [int(i) for i in record[4].split(':')]
    second_tone = [int(i) for i in record[5].split(':')]
    print('Running dual_tone...')
    im_array = AlmaRenders.dual_tone(im_array, first_tone, second_tone)
    image_url = AlmaUtils.save_image(im_array, event.reply_token)

    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    )
