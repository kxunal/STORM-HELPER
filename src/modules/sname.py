from pyrogram import Client, filters
from src import app

@app.on_message(filters.command("sname", prefixes="/") & filters.reply)
async def show_name(client, message):
    replied_msg = message.reply_to_message
    if replied_msg.from_user:
        user_name = replied_msg.from_user.first_name
        unicode_name = user_name.encode('utf-16', 'surrogatepass').decode('utf-16')
        await message.reply_text(f"{unicode_name}")
    else:
        await message.reply_text("Please reply to a user's message to use this command.")
