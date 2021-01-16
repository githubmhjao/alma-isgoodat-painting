import os, urllib, json

from app.custom_models import CallDatabase

client_id = os.environ['NOTIFY_CLIENT_ID']
client_secret = os.environ['NOTIFY_CLIENT_SECRET']
redirect_uri = f"https://{os.environ['YOUR_HEROKU_APP_NAME']}.herokuapp.com/callback/notify"

def create_auth_link(user_id, client_id=client_id, redirect_uri=redirect_uri):
    data = {'response_type': 'code', 'client_id': client_id, 'redirect_uri': redirect_uri, 'scope': 'notify', 'state': user_id}
    query_str = urllib.parse.urlencode(data)

    return f'https://notify-bot.line.me/oauth/authorize?{query_str}'

def get_token(code, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri):
    url = 'https://notify-bot.line.me/oauth/token'
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    page = urllib.request.urlopen(req).read()
    
    return json.loads(page.decode('utf-8'))['access_token']

def handle_subscribe(code, user_id):
    access_token = get_token(code)
    _ = CallDatabase.notify_subscribe(user_id, access_token, True)

    return True

def send_message(user_id, access_token, im_url):

    url = 'https://notify-api.line.me/api/notify'
    headers = {"Authorization": "Bearer "+ access_token}
    data = {'message': '✌您點的雙色打光已送達！', 'imageThumbnail': im_url, 'imageFullsize': im_url}
    data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        page = urllib.request.urlopen(req).read()
        print('Notify Success!')

    except:
        _ = CallDatabase.notify_subscribe(user_id, access_token, False)
        print('Notify Fail. User Unsubscribe.')    
