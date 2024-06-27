from pyrogram import Client, filters
import psutil
import datetime
from src import app
from pymongo import MongoClient
from config import MONGO_DB_URI

DATABASE = MongoClient(MONGO_DB_URI)
db = DATABASE["MAIN"]["USERS"]
collection = db["members"]

def add_user_database(user_id: int):
    check_user = collection.find_one({"user_id": user_id})
    if not check_user:
        return collection.insert_one({"user_id": user_id})

def get_uptime():
    uptime_seconds = psutil.boot_time()
    uptime_datetime = datetime.datetime.fromtimestamp(uptime_seconds)
    uptime_delta = datetime.datetime.now() - uptime_datetime
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds

@app.on_message(filters.command("alive", prefixes="/"))
async def alive_command(client, message):
    add_user_database(message.from_user.id)  # Add user to the database
    hours, minutes, seconds = get_uptime()
    uptime_message = f"I'ᴍ ᴀᴡᴀᴋᴇ sɪɴᴄᴇ {hours} ʜᴏᴜʀs, {minutes}  ᴍɪɴᴜᴛᴇs, {seconds} sᴇᴄᴏɴᴅs"
    await message.reply_text(uptime_message)
