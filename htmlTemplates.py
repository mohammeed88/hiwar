from PIL import Image
import base64
from pathlib import Path

# Function to encode an image to base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Define base directory
BASE_DIR = Path(__file__).resolve().parent

# Load user and bot icons
bot_icon_path = BASE_DIR / "icon_bot.png"
bot_icon_base64 = encode_image(bot_icon_path)

# CSS styles
css = '''
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f9;
    color: #333;
}
.chat-container {
    max-width: 600px;
    margin: 50px auto;
    padding: 20px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    padding-bottom: 100px; /* Add padding to make space for input box */
}
.header-container {
    display: flex;
    align-items: center;
    padding: 10px;
    margin-bottom: 20px;
    background-color: #0a74da;
    color: #fff;
    border-radius: 10px;
}
.header-container .avatar {
    margin-right: 10px;
}
.header-container .avatar img {
    max-width: 50px;
    max-height: 50px;
    border-radius: 50%;
}
.header-container .message {
    font-size: 1.2em;
    font-weight: bold;
}
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
}
.chat-message.user {
    background-color: #2b313e;
}
.chat-message.bot {
    background-color: #475063;
}
.chat-message .avatar {
    width: 50px;
}
.chat-message .avatar img {
    max-width: 50px;
    max-height: 50px;
    border-radius: 50%;
    object-fit: cover;
}
.chat-message .message {
    padding: 0 1.5rem;
    color: #fff;
    width: calc(100% - 50px);
}
</style>
'''

# HTML templates
user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://t4.ftcdn.net/jpg/02/29/75/83/240_F_229758328_7x8jwCwjtBMmC6rgFzLFhZoEpLobB6L8.jpg">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="data:image/png;base64,{bot_icon_base64}">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''.replace('{bot_icon_base64}', bot_icon_base64)

header_template = '''
<div class="header-container">
    <div class="avatar">
        <img src="data:image/png;base64,{bot_icon_base64}">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''.replace('{bot_icon_base64}', bot_icon_base64)
