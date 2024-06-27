from pytube import YouTube, Search
import random
from pyrogram import filters
from pyrogram.types import Message
from src import app
import os
import re

from pymongo import MongoClient
from config import MONGO_DB_URI

DATABASE = MongoClient(MONGO_DB_URI)
db = DATABASE["MAIN"]["USERS"]

def add_user_to_db(user_id):
    if db.find_one({"user_id": user_id}):
        return
    db.insert_one({"user_id": user_id})

def is_valid_url(url):
    return re.match(r'^https?://(?:www\.)?youtu\.?be(?:\.com)?/', url, re.IGNORECASE) is not None

@app.on_message(filters.command("yt", ["!", "/", "."]))
async def yt(_, msg: Message):
    try:
        add_user_to_db(msg.from_user.id)

        split_text = msg.text.split(None, 1)
        if len(split_text) < 2:
            await msg.reply_text("Usage: `/yt (video link) or (video name)`")
            return

        query = split_text[1]
        if is_valid_url(query):
            yt = YouTube(query)
        else:
            search_results = Search(query)
            video = search_results.results[0]
            yt = YouTube(video.watch_url)
        
        stream = yt.streams.get_highest_resolution()
        cutie = f"video_{random.randint(1000, 9999)}"
        stream.download(filename=cutie)
        pop = f"""
Here is your video.
Requested by {msg.from_user.mention}
Query: `{query}`
Downloaded by {app.me.mention}"""
        await msg.reply_video(video=cutie, caption=pop)
        os.remove(cutie)
    except Exception as e:
        await msg.reply_text(f"Failed to download the video: {e}")

