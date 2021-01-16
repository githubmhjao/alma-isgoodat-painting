import os

from app import line_bot_api
from app.custom_models import AlmaRenders, AlmaNotify, CallDatabase

from linebot.models import TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, PostbackAction

def default_reply(event):
    name = line_bot_api.get_profile(event.source.user_id).display_name
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"Hello {name}!")
        )

def phase_start(event):
    CallDatabase.init_table()
    if CallDatabase.check_record(event.source.user_id):
        _ = CallDatabase.update_record(event.source.user_id, 'message_id', event.message.id)
    else:
        _ = CallDatabase.init_record(event.source.user_id, event.message.id)

    mode_dict = {'blend': '線性疊圖', 'composite': '濾鏡疊圖', 'composite_invert': '反式濾鏡疊圖'}

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=f"[1/4] 今晚，我想來點雙色打光！\n請選擇雙色打光模式：", 
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=PostbackAction(label=j, display_text=f'打光模式：{j}', data=f'mode={i}')) for i, j in mode_dict.items()]))
        )

def phase_intermediate(event):

    color_dict = {'red': '紅',
                  'orange': '橙', 
                  'yellow': '黃', 
                  'green': '綠', 
                  'blue': '藍',
                  'purple': '紫'}
    reply_dict = {'mode': '[2/4] 今晚，繼續來點雙色打光！\n請選擇色彩變化梯度：',
                  'gradient_factor': '[3/4] 今晚，還想來點雙色打光！\n請選擇第一道色彩：',
                  'first_tone': '[4/4] 今晚，最後來點雙色打光！\n請選擇第二道色彩：'}
    quick_button_dict = {'mode': [QuickReplyButton(action=PostbackAction(label=i, display_text=f'變化梯度：{i}', data=f'gradient_factor={i}')) for i in (5, 10, 50, 100)],
                         'gradient_factor': [QuickReplyButton(action=PostbackAction(label=j, display_text=f'第一道色彩：{j}', data=f'first_tone={i}')) for i, j in color_dict.items()],
                         'first_tone': [QuickReplyButton(action=PostbackAction(label=j, display_text=f'第二道色彩：{j}', data=f'second_tone={i}')) for i, j in color_dict.items()]}

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

    record = CallDatabase.update_record(user_id, current_phase, postback_data.split('=')[1])

    message_content = line_bot_api.get_message_content(record[1])

    print('Getting image...')
    im = AlmaRenders.get_image(message_content, event.reply_token)

    print('Running dual tone...')
    mode = record[2]
    gradient_factor = int(record[3])
    first_tone = record[4]
    second_tone = record[5]
    im_dual_tone = AlmaRenders.dual_tone_run(im, mode, gradient_factor, first_tone, second_tone)

    print('Saving image...')
    im_url = AlmaRenders.save_image(im_dual_tone, event.reply_token)

    auth_link = AlmaNotify.create_auth_link(user_id)

    reply_template = f"雙色打光模式：{mode}\n色彩變化梯度：{gradient_factor}\n第一道色彩：{first_tone}\n第二道色彩：{second_tone}\n"
    reply_template += '👉您的雙色打光將由 LINE Notify 送達。若尚未連動，請連動之後再次下單，謝謝！\n'
    reply_template += f'👉連動網址：\n{auth_link}'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_template)
    )

    record = CallDatabase.notify_get_token(user_id)
    if record:
        access_token = record[1]
        AlmaNotify.send_message(user_id, access_token, im_url)
