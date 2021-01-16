import os
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from PIL import ImageEnhance

def get_image(message_content, file_name):
    file_path = f"/tmp/{file_name}.png"

    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
            
    im = Image.open(file_path)    
    return im

def sigmoid(x, alpha):
    return 1 /(1 + np.exp(-x * alpha))

def create_gradient_layer(layer_im, gradient_factor, first_tone, second_tone):
    layer_gradient = Image.new('RGB', layer_im.size)
    draw = ImageDraw.Draw(layer_gradient)

    for i in range(layer_im.size[0]):
        value = sigmoid(i - layer_im.size[0] / 2, gradient_factor / layer_im.size[0])
        fill_color = np.array(first_tone) * value + np.array(second_tone) * (1 - value)
        draw.line([(i, 0), (i, layer_im.size[1]-1)], fill=tuple(fill_color.astype('int')))

    return layer_gradient

def dual_tone_run(im, mode, gradient_factor, first_tone, second_tone):

    color_dict = {
        'red':    {'blend': (100, 10, 0),  'composite': (100, 10, 0),  'composite_invert': (255, 0, 0)},
        'orange': {'blend': (100, 50, 0),  'composite': (100, 50, 0),  'composite_invert': (255, 120, 0)},
        'yellow': {'blend': (100, 100, 0), 'composite': (100, 100, 0), 'composite_invert': (255, 255, 0)},
        'green':  {'blend': (10, 100, 0),  'composite': (10, 100, 0),  'composite_invert': (0, 255, 0)},
        'blue':   {'blend': (0, 10, 100),  'composite': (0, 10, 100),  'composite_invert': (0, 0, 255)},
        'purple': {'blend': (50, 0, 100),  'composite': (50, 0, 100),  'composite_invert': (120, 0, 255)} 
    }

    layer_im = im.convert('RGBA')

    first_tone = color_dict[first_tone][mode]
    second_tone = color_dict[second_tone][mode]
    layer_gradient = create_gradient_layer(layer_im, gradient_factor, first_tone, second_tone).convert('RGBA')
    
    if mode == 'blend':
        dual_tone = Image.blend(layer_im, layer_gradient, 0.5)
    elif mode == 'composite':
        dual_tone = Image.composite(layer_im, layer_gradient, layer_im.convert('L'))
    elif mode == 'composite_invert':
        dual_tone = Image.composite(layer_im, layer_gradient, ImageOps.invert(layer_im.convert('L')).convert('L'))
    return ImageEnhance.Color(dual_tone).enhance(2)

def save_image(im, token):
    file_path = f'/tmp/{token}_DualTone.png'
    im.save(file_path)    
    return f'https://{os.getenv("YOUR_HEROKU_APP_NAME")}.herokuapp.com/result/{token}'
