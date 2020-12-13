import numpy as np

def to_array(input_im):
    
    return np.array(input_im)
    
def simple_gray(input_array):
    
    return np.mean(np.array(input_array), axis=2)
    
def lkre_color_curve(input_array, alpha, beta=50):
    """
    param alpha: original grayscale
    param beta : adjusted grayscale
    """
    
    def leaky_relu(input_value, alpha, beta):
        if input_value < alpha:
            return input_value * beta / alpha
        else:
            return (input_value - alpha) * (255 - beta) / (255 - alpha) + beta
        
    vec_relu = np.vectorize(leaky_relu)
    
    return vec_relu(input_array, alpha, beta).astype(np.uint8)
    
def dual_tone(input_array, rgb_right, rgb_left):
    
    assert len(input_array.shape) == 2
    
    input_x, input_y = input_array.shape
    alpha_channel = np.ones((input_x, input_y, 1)) * 255
    
    # Use np.logspace instead of np.linspace
    rgb_right_channel = np.tile(np.logspace(0, 1, input_y), (input_x, 1))[:, :, np.newaxis] * rgb_right
    rgb_left_channel  = np.tile(np.logspace(1, 0, input_y), (input_x, 1))[:, :, np.newaxis] * rgb_left
    rgb_dual_channel = rgb_right_channel + rgb_left_channel
    
    input_array_dual = input_array[:, :, np.newaxis] / 255 * rgb_dual_channel
    input_array_dual = np.concatenate((input_array_dual, alpha_channel), axis=2).astype('int')
    
    return np.minimum(input_array_dual, 255).astype(np.uint8)
