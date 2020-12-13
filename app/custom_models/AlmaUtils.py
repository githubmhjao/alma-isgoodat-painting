import os
from PIL import Image

def get_image(message_content, file_name="hello"):
    file_path = f"/tmp/{file_name}.png"

    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
            
    im = Image.open(file_path)    
    return im

def save_image(input_array, token):
    im = Image.fromarray(input_array)
    file_path = f'/tmp/{token}_DualTone.png'
    im.save(file_path)    
    return f'https://{os.getenv("HEROKU_APP_NAME")}.herokuapp.com/result/{token}'
