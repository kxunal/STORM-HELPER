from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyfiglet import figlet_format
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

@app.on_message(filters.command("figlet"))
async def figlet_command(_, message):
    add_user_database(message.from_user.id)  # Add user to the database
    text = " ".join(message.command[1:])
    figlet_text = figlet_format(text)
    response = f"Here is your figlet of '{text}':\n```\n{figlet_text}\n```"
    close_button = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="figletclose")]])
    await message.reply_text(response, reply_markup=close_button)

@app.on_callback_query(filters.regex("figletclose"))
async def close_callback(_, query: CallbackQuery):
    await query.message.delete()
