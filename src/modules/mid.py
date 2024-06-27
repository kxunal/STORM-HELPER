from pyrogram import filters
import urllib.parse
from src import app

@app.on_message(filters.command(["mid"], prefixes=["/", ".",  "!"]))
async def draw_prompt(app, message):
    codes = message.text.split(maxsplit=1)[1]
    cods = urllib.parse.quote(codes)
    get = f"https://cute-tan-gorilla-yoke.cyclic.app/imagine?text={cods}"
    await message.reply_photo(photo=get, caption=f"Prompt: {codes}")
