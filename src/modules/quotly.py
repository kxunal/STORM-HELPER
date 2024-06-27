import io
from io import BytesIO
from src import app
from pyrogram import filters
from pyrogram.types import Message
from httpx import AsyncClient, Timeout

class SakuraException(Exception):
    pass

http = AsyncClient(
    http2=True,
    verify=False,
    timeout=Timeout(40)
)

async def message_sender_id(ctx: Message):
    if ctx.forward_date:
        return ctx.forward_from.id if ctx.forward_from else 1
    elif ctx.from_user:
        return ctx.from_user.id
    elif ctx.sender_chat:
        return ctx.sender_chat.id
    else:
        return 1

async def message_sender_name(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return ctx.forward_sender_name
        elif ctx.forward_from:
            return f"{ctx.forward_from.first_name} {ctx.forward_from.last_name or ''}"
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.title
        else:
            return ""
    elif ctx.from_user:
        return f"{ctx.from_user.first_name} {ctx.from_user.last_name or ''}"
    elif ctx.sender_chat:
        return ctx.sender_chat.title
    else:
        return ""

async def get_photo_info(photo):
    if photo:
        return {
            "small_file_id": photo.small_file_id,
            "small_photo_unique_id": photo.small_photo_unique_id,
            "big_file_id": photo.big_file_id,
            "big_photo_unique_id": photo.big_photo_unique_id,
        }
    else:
        return ""

async def message_sender_photo(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_from_chat and ctx.forward_from_chat.photo:
            return await get_photo_info(ctx.forward_from_chat.photo)
        elif ctx.forward_from and ctx.forward_from.photo:
            return await get_photo_info(ctx.forward_from.photo)
        else:
            return ""
    elif ctx.from_user and ctx.from_user.photo:
        return await get_photo_info(ctx.from_user.photo)
    elif ctx.sender_chat and ctx.sender_chat.photo:
        return await get_photo_info(ctx.sender_chat.photo)
    else:
        return ""

async def message_sender_emoji(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_from:
            return ctx.forward_from.emoji_status.custom_emoji_id if ctx.forward_from.emoji_status else ""
    elif ctx.from_user:
        return ctx.from_user.emoji_status.custom_emoji_id if ctx.from_user and ctx.from_user.emoji_status else ""
    return ""

async def message_sender_username(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_from_chat and ctx.forward_from_chat.username:
            return ctx.forward_from_chat.username
        elif ctx.forward_from and ctx.forward_from.username:
            return ctx.forward_from.username
        else:
            return ""
    elif ctx.from_user and ctx.from_user.username:
        return ctx.from_user.username
    elif ctx.sender_chat and ctx.sender_chat.username:
        return ctx.sender_chat.username
    else:
        return ""

async def pyrogram_to_quotly_payload(message, is_reply):
    payload = {
        "entities": [],
        "chatId": await message_sender_id(message),
        "text": await get_text_or_caption(message),
        "avatar": True,
        "from": {
            "id": await message_sender_id(message),
            "name": await message_sender_name(message),
            "username": await message_sender_username(message),
            "type": message.chat.type.name.lower(),
            "photo": await message_sender_photo(message),
            "emoji": await message_sender_emoji(message)
        },
        "replyMessage": {}
    }
    if message.reply_to_message and is_reply:
        payload["replyMessage"] = {
            "name": await message_sender_name(message.reply_to_message),
            "text": await get_text_or_caption(message.reply_to_message),
            "chatId": await message_sender_id(message.reply_to_message),
        }
    return payload

async def pyrogram_to_quotly(messages, is_reply):
    if not isinstance(messages, list):
        messages = [messages]
    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [await pyrogram_to_quotly_payload(message, is_reply) for message in messages]
    }
    response = await http.post("https://bot.lyo.su/quote/generate.png", json=payload)
    if not response.is_error:
        return response.read()
    else:
        raise SakuraException(response.json())

async def get_text_or_caption(ctx: Message):
    return ctx.text or ctx.caption or ""

async def is_arg_int(txt):
    try:
        count = int(txt)
        return True, count
    except ValueError:
        return False, 0

async def get_messages_within_range(ctx, check_arg):
    try:
        return [
            i for i in await app.get_messages(
                chat_id=ctx.chat.id,
                message_ids=range(ctx.reply_to_message.id, ctx.reply_to_message.id + (check_arg[1] + 5)),
                replies=-1,
            ) if not i.empty and not i.media
        ]
    except Exception:
        return []

async def handle_message_reply(ctx, is_reply):
    try:
        messages = await get_messages_within_range(ctx, is_arg_int(ctx.command[1]))
    except Exception:
        return await ctx.reply_text("🤷🏻‍♂️")
    try:
        make_quotly = await pyrogram_to_quotly(messages, is_reply=is_reply)
        bio_sticker = BytesIO(make_quotly)
        bio_sticker.name = "guardianquote.webp"
        return await ctx.reply_sticker(bio_sticker)
    except Exception:
        return await ctx.reply("🤷🏻‍♂️")

async def handle_single_message_reply(ctx, is_reply):
    try:
        messages_one = await app.get_messages(
            chat_id=ctx.chat.id, message_ids=ctx.reply_to_message.id, replies=-1
        )
        messages = [messages_one]
    except Exception:
        return await ctx.reply("🤷🏻‍♂️")
    try:
        make_quotly = await pyrogram_to_quotly(messages, is_reply=is_reply)
        bio_sticker = io.BytesIO(make_quotly)
        bio_sticker.name = "guardianquote.webp"
        return await ctx.reply_sticker(bio_sticker)
    except Exception as e:
        return await ctx.reply(f"Error occurred: {e}")

@app.on_message(filters.command(["q"], prefixes=["/", "!", "."]) & filters.reply)
async def msg_quotly_cmd(self: app, ctx: Message):
    is_reply = ctx.command[0].endswith("r")
    if len(ctx.text.split()) > 1:
        if arg_int := await is_arg_int(ctx.command[1])[0]:
            if not (2 <= arg_int <= 10):
                return await ctx.reply("Invalid range")
            return await handle_message_reply(ctx, is_reply)
    return await handle_single_message_reply(ctx, is_reply)
