import asyncio
import re
import requests
from io import BytesIO

import telepot
from telepot.aio.delegate import per_chat_id, create_open
from telepot.aio.loop import MessageLoop
import pytesseract
from PIL import Image

# Replace "TOKEN" with your Telegram Bot API token
TOKEN = 'TOKEN'

class ScanTextBot(telepot.aio.helper.ChatHandler):
    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':
            if msg['text'] == '/start':
                await self.sender.sendMessage('Hi there! I\'m a bot that can extract text from photos. '
                                              'Send me a photo and I\'ll do my best to extract the text for you. '
                                              'You can also send the /gettext command to start.')
                return

            if msg['text'].startswith('/gettext'):
                await self.sender.sendMessage('Please send a photo containing the text you want to extract.')
                self._get_text = True
                return

        if content_type == 'photo' and hasattr(self, '_get_text'):
            # Get the file_id of the photo
            file_id = msg['photo'][-1]['file_id']

            # Get the file from Telegram
            file = await self.bot.getFile(file_id)
            file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file["file_path"]}'

            # Download the photo
            response = requests.get(file_url)
            image = Image.open(BytesIO(response.content))

            # Use pytesseract to extract text from the photo
            text = pytesseract.image_to_string(image, lang='eng')

            # Replace special characters with their Unicode representation
            text = text.replace('∫', '\u222b')
            text = text.replace('∑', '\u2211')
            text = text.replace('Π', '\u03a0')
            text = text.replace('Σ', '\u03a3')
            text = text.replace('×', '\u00d7')
            text = text.replace('÷', '\u00f7')

            # Send the extracted text back to the user
            await self.sender.sendMessage(text, parse_mode='Markdown')
            self._get_text = False

bot = telepot.aio.DelegatorBot(TOKEN, [
    per_chat_id(),
    create_open(ScanTextBot, timeout=10),
])

async def on_startup(dispatcher):
    await dispatcher.start()

async def on_shutdown(dispatcher):
    await dispatcher.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(bot.message_loop(on_startup=on_startup, on_shutdown=on_shutdown))
loop.run_forever()
