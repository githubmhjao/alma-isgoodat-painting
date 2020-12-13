from app import app, handler

from flask import request, send_from_directory, abort
from linebot.exceptions import InvalidSignatureError

@app.route("/")
def index():
    return send_from_directory('/app/', filename='Hello.png')

@app.route("/result/<token>")
def get_image_url(token):
    return send_from_directory('/tmp/', filename=f'{token}_DualTone.png')

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
