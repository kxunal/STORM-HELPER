from src import app
from src.database.chats_db import get_served_chats
from src.database.users_db import get_served_users
from pyrogram import filters
from pyrogram.types import Message

@app.on_message(filters.command("stats", ["!", "/", "."]))
async def unxstats(_, msg: Message):
    served_users = await get_served_users()
    users = (len(served_users))
    served_chats = len(await get_served_chats())
    chats = (served_chats)
    await msg.reply_text(f"""⛩ ᴄʜᴀᴛs: `{chats}`\n✨ ᴜsᴇʀs: `{users}`""")
