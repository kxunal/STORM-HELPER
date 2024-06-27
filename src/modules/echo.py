from pyrogram import filters
from html import escape, unescape
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
        
@app.on_message(filters.command("echo"))
async def echo(app, message):
    add_user_database(message.from_user.id)  # Add user to the database
    if message.reply_to_message:
        text = message.text.split(None, 1)[1]
        await app.send_message(chat_id=message.chat.id, text=text, reply_to_message_id=message.reply_to_message.id)
    else:
        try:
            text = message.text.split(maxsplit=1)[1]
            if text.strip() == "":
                await message.reply_text("ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ ᴇᴄʜᴏ.")
            else:
                await message.reply_text(unescape(text))
        except IndexError:
            await message.reply_text("ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ ᴇᴄʜᴏ")
