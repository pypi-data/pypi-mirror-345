import requests

FORM_PIX_URL = 'http://localhost:3000'
API_KEY = None

def login(url, key):
    global FORM_PIX_URL, API_KEY
    FORM_PIX_URL = url
    API_KEY = key

def send_command(command, params, req_options):
    try:
        url = f"{FORM_PIX_URL}/api/{command}?{params}"
        response = requests.request(method=req_options['method'], url=url, headers=req_options['headers'])
        data = response.json()
        print(data)
    except Exception as err:
        print('Connection closed due to errors:', err)

def get_req_options():
    return {
        'method': 'POST',
        'headers': {
            'API': API_KEY,
            'Content-Type': 'application/json'
        }
    }

def fill(color, start, length):
    params = f"color={color}&start={start}&length={length}"
    send_command('fill', params, get_req_options())

def gradient(start_color, end_color, start, length):
    params = f"startColor={start_color}&endColor={end_color}&start={start}&length={length}"
    send_command('gradient', params, get_req_options())

def set_pixel(location, color):
    params = f"location={location}&color={color}"
    send_command('setPixel', params, get_req_options())

def set_pixels(pixels):
    params = f"pixels={pixels}"
    send_command('setPixels', params, get_req_options())

def say(text, color, bgcolor):
    params = f"text={text}&textColor={color}&backgroundColor={bgcolor}"
    send_command('say', params, get_req_options())

def get_sounds(sound_type):
    get_options = {
        'method': 'GET',
        'headers': {
            'API': API_KEY,
            'Content-Type': 'application/json'
        }
    }
    params = f"type={sound_type}"
    send_command('say', params, get_options)  # Assuming `say` was mistakenly reused

def play_sound(sfx, bgm):
    params = f"sfx={sfx}&bgm={bgm}"
    send_command('playSound', params, get_req_options())

# Example usage
# login('http://localhost:3000', 'your-api-key')
# fill('#ff0000', 0, 10)
# say('Hello', 'white', 'black')
