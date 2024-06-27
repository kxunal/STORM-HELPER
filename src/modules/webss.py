import aiohttp
import src as SakuraLogger

async def post(url: str, **kwargs):
    async with aiohttp.ClientSession().post(url, **kwargs) as respo:
        try:
            data = await respo.json()
        except Exception as es:
            data = await respo.text()
            SakuraLogger.LOGGER.info(es)
    return data


from base64 import b64decode
from inspect import getfullargspec
from io import BytesIO
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src import app

async def take_screenshot(url: str, full: bool = False):
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True
    data = await post(
        "https://webscreenshot.vercel.app/api",
        data=payload,
    )
    if "image" not in data:
        return None
    b = data["image"].replace("data:image/jpeg;base64,", "")
    file = BytesIO(b64decode(b))
    file.name = "webss.jpg"
    return file


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command(["webss", "wss"], prefixes=["/", ".", "!"]))
async def take_ss(Sakura, message: Message):
    if len(message.command) < 2:
        return await eor(message, text="ɢɪᴠᴇ ᴀ ᴜʀʟ ᴛᴏ ғᴇᴛᴄʜ sᴄʀᴇᴇɴsʜᴏᴛ.")

    if len(message.command) == 2:
        url = message.text.split(None, 1)[1]
        full = False
    elif len(message.command) == 3:
        url = message.text.split(None, 2)[1]
        full = message.text.split(None, 2)[2].lower().strip() in [
            "yes",
            "y",
            "1",
            "true",
        ]
    else:
        return await eor(message, text="ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ.")
    m = await eor(message, text="ᴄᴀᴘᴛᴜʀɪɴɢ sᴄʀᴇᴇɴsʜᴏᴛ...")
    try:
        photo = await take_screenshot(url, full)
        if not photo:
            return await m.edit("ғᴀɪʟᴇᴅ ᴛᴏ ᴛᴀᴋᴇ sᴄʀᴇᴇɴsʜᴏᴛ.")
        m = await m.edit("ᴜᴘʟᴏᴀᴅɪɴɢ...")
        visit_button_text = "Visit"
        await message.reply_document(photo, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=visit_button_text, url=url)]]))
        await m.delete()
    except Exception as e:
        await m.edit(str(e))
