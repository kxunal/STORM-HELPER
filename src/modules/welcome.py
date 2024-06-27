from pyrogram import filters
from pyrogram.types import Message
from src import app
from src.database.welcome_db import *
from src.modules.editmode import group_admins
from PIL import Image, ImageDraw, ImageChops, ImageFont

async def circle(pfp, size=(215, 215)):
    pfp = pfp.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.Resampling.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

async def pfp(pfp, chat, id):
    if len(chat) > 21:
        chat = chat[0:18] + ".."
    temp = Image.open("./src/pics/bg.jpg")
    pfp = Image.open(pfp).convert("RGBA")
    pfp = await circle(pfp, (363, 363))
    
    font_path = "./src/fonts/font.ttf"
    m_font = ImageFont.truetype(font_path, 35)
    i_font = ImageFont.truetype(font_path, 20)
    
    nice = temp.copy()
    nice.paste(pfp, (58, 131), pfp)
    draw = ImageDraw.Draw(nice)
    draw.text((565, 350), text=f"{chat.upper()}", font=m_font, fill=(275, 275, 275))
    draw.text((180, 525), text=str(id), font=i_font, fill=(275, 275, 275))
    nice.save(f"./src/pics/nice{id}.png")
    return f"./src/pics/nice{id}.png"

@app.on_message(filters.command("welcome"))
async def welcomefunc(app, message) -> None:
    group_admin = await group_admins(message.chat.id)
    if message.from_user.id not in group_admin:
        return await message.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ.")
    
    if len(message.command) == 1:
        return await message.reply("ᴜꜱᴀɢᴇ: /welcome on/off")
    status = message.command[1]
    if status == "on":
        check_status = WELCOME_DB.find_one({"group_id": message.chat.id})
        if not check_status:
            add_welcome_enable(message.chat.id)
            return await message.reply("ꜱᴜʀᴇ ɪ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴡᴇʟᴄᴏᴍᴇ ɴᴇᴡ ᴍᴇᴍʙᴇʀꜱ.")
        else:
            await message.reply("ɪᴛ'ꜱ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.")
    elif status == "off":
        check_status = WELCOME_DB.find_one({"group_id": message.chat.id})
        if not check_status:
            return await message.reply("ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴅɪꜱᴀʙʟᴇᴅ.")
        else:
            remove_welcome_enable(message.chat.id)
            return await message.reply("ᴏʜᴋ ɪ ᴡɪʟʟ ʙᴇ Qᴜɪᴛᴇ ᴡʜᴇɴ ᴀɴʏᴏɴᴇ'ꜱ ᴊᴏɪɴ.")
    else:
        return await message.reply("ɪɴᴠᴀʟɪᴅ ꜱʏɴᴛᴀx!\nᴛʀʏ /ᴡᴇʟᴄᴏᴍᴇ ᴏɴ/ᴏꜰꜰ")

@app.on_message(filters.new_chat_members, group=6)
async def okbaby(client, message):
    group_admin = await group_admins(message.chat.id)
    for user in message.new_chat_members:
        if user.id == client.me.id:  # Check if the bot itself is joining
            return  # Skip
        check = WELCOME_DB.find_one({"group_id": message.chat.id})
        if not check:
            return
        photo = await client.download_media(user.photo.big_file_id)
        accha = await pfp(photo, message.chat.title, user.id)
        await app.send_photo(message.chat.id, photo=accha, caption=f"""Iᴅ : `{user.id}`\nNᴀᴍᴇ : {user.mention}\nUsᴇʀɴᴀᴍᴇ : @{user.username}""")


