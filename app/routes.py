# 利用 route 處理路由
from app import app, handler
from app.custom_models import AlmaNotify

from flask import request, send_from_directory, abort
from linebot.exceptions import InvalidSignatureError

@app.route("/")
def index():
    return send_from_directory('/app/', filename='hello.png')

@app.route("/result/<token>")
def get_image_url(token):
    return send_from_directory('/tmp/', filename=f'{token}_DualTone.png')

@app.route("/callback/notify", methods=['GET'])
def callback_notify():
    
    assert request.headers['referer'] == 'https://notify-bot.line.me/'
    code = request.args.get('code')
    state = request.args.get('state')
    
    success = AlmaNotify.handle_subscribe(code, state)

    return '恭喜完成 LINE Notify 連動！請關閉此視窗。'

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
