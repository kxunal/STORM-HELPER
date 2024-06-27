import asyncio
from pyrogram import Client, filters
from datetime import datetime
from src import app

@app.on_message(filters.command("ping"))
async def ping(bot, message):
    start_time = datetime.now()
    x = await message.reply_text("ᴘɪɴɢɪɴɢ...")
    await asyncio.sleep(1.5)
    await x.delete()
    end_time = datetime.now()
    latency = (end_time - start_time).microseconds / 1000
    await message.reply_text(f"ᴘɪɴɢ ᴘᴏɴɢ ʟᴀᴛᴇɴᴄʏ{latency}ᴍs")
