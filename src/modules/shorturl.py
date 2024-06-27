from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from src import app



async def shorten_url(url):
    api_url = "https://tinyurl.com/api-create.php?url=" + url
    response = requests.get(api_url)
    return response.text

@app.on_message(filters.command("shorturl"))
async def short_url(_, message):
    url = message.text.split(" ", 1)[1]
    short_url = await shorten_url(url)
    visit_button = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴠɪsɪᴛ", url=short_url)]])
    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇᴅ ᴜʀʟ : \n\n`{short_url}`", reply_markup=visit_button)
