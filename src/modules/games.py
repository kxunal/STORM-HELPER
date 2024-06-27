import datetime, pymongo
from pymongo import MongoClient
import random
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src import app as Guardian 
from pyrogram import filters
import asyncio

PLAY_IMG = (
	"https://telegra.ph/file/bfc45e04e2b94d1895485.jpg",
        "https://telegra.ph/file/06a1d907a290b0f179085.jpg",
	"https://telegra.ph/file/09eb42ef833bf21e398c3.jpg",
	"https://telegra.ph/file/8c63e91be3db540292dd0.jpg",
	"https://telegra.ph/file/0332660a0db7fd9d8310e.jpg",
	"https://telegra.ph/file/fcf64ca1fcc7409562c2b.jpg"
)

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

# ------ db codes -------
import datetime
from config import MONGO_DB_URI
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_DB_URI)
db = mongo.Anonymous
gamesdb = db.games

async def create_account(user_id,user_name):
  dic = {
  'user_id' : user_id,
    "username" : user_name,
    'coins' : 50000,
  }
  return gamesdb.insert_one(dic)

async def is_player(user_id):
  return bool(await gamesdb.find_one({"user_id" : user_id}))
  
async def user_wallet(user_id):
    player = await gamesdb.find_one({"user_id" : user_id})
    if not player:
        return 0
    return player['coins']
   
async def find_and_update(user_id,username):
    user= await gamesdb.find_one({"user_id" : user_id})
    if not user:
        return
    old_username = user["username"].lower()
    if old_username != username.lower():
        return await gamesdb.update_one({'user_id' : user_id},{'$set' : {'username' : username}})
                                 
# ------ db codes ------

async def get_user_won(emoji,value):
    if emoji in ['🎯','🎳']:
        if value >= 4:
            u_won = True
        else:
            u_won = False
    elif emoji in ['🏀','⚽'] :
        if value >= 3:
            u_won = True
        else:
            u_won = False
    return u_won
                             
                             
async def can_play(tame,tru):
  current_time = datetime.datetime.now()
  time_since_last_collection = current_time - datetime.datetime.fromtimestamp(tame)
  x = tru - time_since_last_collection.total_seconds()
  if str(x).startswith('-'):
      return 0
  return x
  

BET_DICT = {}
DART_DICT = {}
BOWL_DICT = {}
BASKET_DICT = {}


@Guardian.on_message(filters.command("bet"))
async def _bet(client,message):
  chat_id = message.chat.id
  user = message.from_user
  if not await is_player(user.id):
     await create_account(user.id,message.from_user.username)
  if user.id not in BET_DICT.keys():
      BET_DICT[user.id] = None     
  if BET_DICT[user.id]:
      x= await can_play(BET_DICT[user.id],12)
      print(x)
      if int(x) != 0:
        return await message.reply_photo(photo=random.choice(PLAY_IMG), caption=f'**ʏᴏᴜ ᴄᴀɴ ʙᴇᴛ ᴀɢᴀɪɴ ɪɴ ʟɪᴋᴇ** {get_readable_time(x)}.')     
  possible = ['h','heads','tails','t','head','tail']
  if len(message.command) < 3:
      return await message.reply_text("**✑ ᴜsᴀɢᴇ : /bet [ᴀᴍᴏᴜɴᴛ] [ʜᴇᴀᴅs/ᴛᴀɪʟs]**")
  to_bet = message.command[1]
  cmd = message.command[2].lower()
  coins = await user_wallet(user.id)
  if to_bet == '*':
      to_bet = coins
  elif not to_bet.isdigit():
       return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴛʜɪɴᴋs ᴛʜᴀᴛ ɪᴛ's ᴀ ᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ?**")
  to_bet = int(to_bet)
  if to_bet == 0:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴡᴀɴɴᴀ ʙᴇᴛ 𝟶 ᴄᴏɪɴs ? ʟᴏʟ!**") 
  elif to_bet > coins:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴍᴜᴄʜ ᴄᴏɪɴs ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ** ✑ `{0:,}` **ᴄᴏɪɴs**".format(coins)) 
  rnd = random.choice(['heads','tails'])
  if cmd not in possible:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ sʜᴏᴜʟᴅ ᴛʀʏ ʜᴇᴀᴅs ᴏʀ ᴇɪᴛʜᴇʀ ᴛᴀɪʟs.**")
  if cmd in ['h','head','heads']:
      if rnd == 'heads':
          user_won = True         
      else:
          user_won = False
  if cmd in ['t','tail','tails']:
      if rnd == 'tails':
          user_won = True
      else:
          user_won = False
  BET_DICT[user.id] = datetime.datetime.now().timestamp()
  if not user_won:
      new_wallet = coins - to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**🛑 ᴛʜᴇ ᴄᴏɪɴ ʟᴀɴᴅᴇᴅ ᴏɴ** {0}!\n• **ʏᴏᴜ ʟᴏsᴛ** `{1:,}` **ᴄᴏɪɴs**\n• **ᴛᴏᴛᴀʟ ʙᴀʟᴀɴᴄᴇ** : `{2:,}` **ᴄᴏɪɴs**".format(rnd,to_bet,new_wallet))
  else:
      new_wallet = coins + to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**✅ ᴛʜᴇ ᴄᴏɪɴ ʟᴀɴᴅᴇᴅ ᴏɴ** {0}!\n**ʏᴏᴜ ᴡᴏɴ** `{1:,}` ᴄᴏɪɴs\n**ᴛᴏᴛᴀʟ ʙᴀʟᴀɴᴄᴇ** : `{2:,}` **ᴄᴏɪɴs**".format(rnd,to_bet,new_wallet)) 
     

@Guardian.on_message(filters.command("dart"))
async def _bet(client,message):
  chat_id = message.chat.id
  user = message.from_user
  if not await is_player(user.id):
     await create_account(user.id,message.from_user.username)
  if user.id not in DART_DICT.keys():
      DART_DICT[user.id] = None     
  if DART_DICT[user.id]:
      x= await can_play(DART_DICT[user.id],20)
      if int(x) != 0:
        return await message.reply_photo(photo=random.choice(PLAY_IMG), caption=f'**ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴅᴀʀᴛ ᴀɢᴀɪɴ ɪɴ ʟɪᴋᴇ** `{get_readable_time(x)}`.')
  if len(message.command) < 2:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ᴏᴋ! ʙᴜᴛ ʜᴏᴡ ᴍᴜᴄʜ ʏᴏᴜ ᴀʀᴇ ɢᴏɴɴᴀ ʙᴇᴛ.**")
  to_bet = message.command[1]
  coins = await user_wallet(user.id)
  if to_bet == '*':
      to_bet = coins
  elif not to_bet.isdigit():
       return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴛʜɪɴᴋs ᴛʜᴀᴛ ɪᴛ's ᴀ ᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ?**")
  to_bet = int(to_bet)
  if to_bet == 0:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴡᴀɴɴᴀ ʙᴇᴛ 𝟶 ᴄᴏɪɴs ? ʟᴏʟ!**") 
  elif to_bet > coins:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="**ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴍᴜᴄʜ ᴄᴏɪɴs ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ** ✑ `{0:,}` **ᴄᴏɪɴs**".format(coins))
  m = await client.send_dice(chat_id,'🎯')
  msg = await message.reply('....')
  u_won = await get_user_won(m.dice.emoji,m.dice.value)
  DART_DICT[user.id] = datetime.datetime.now().timestamp()
  if not u_won:
      new_wallet = coins - to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("**🛑 sᴀᴅ ᴛᴏ sᴀʏ! ʙᴜᴛ ʏᴏᴜ ʟᴏsᴛ** `{0:,}` **ᴄᴏɪɴs**\n• **ᴄᴜʀᴇᴇɴᴛ ʙᴀʟᴀɴᴄᴇ** ✑ `{1:,}` **ᴄᴏɪɴs**".format(to_bet,new_wallet))
  else:
      new_wallet = coins + to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("**✅ ᴡᴏᴡ! ʏᴏᴜ ᴡᴏɴ** `{0:,}` **ᴄᴏɪɴs**\n• **ᴄᴜʀᴇᴇɴᴛ ʙᴀʟᴀɴᴄᴇ** ✑ `{1:,}`**ᴄᴏɪɴs.**".format(to_bet,new_wallet))
     
      
@Guardian.on_message(filters.command("bowl"))
async def _bet(client,message):
  chat_id = message.chat.id
  user = message.from_user
  if not await is_player(user.id):
     await create_account(user.id,message.from_user.username) 
  if user.id not in BOWL_DICT.keys():
      BOWL_DICT[user.id] = None     
  if BOWL_DICT[user.id]:
      x= await can_play(BOWL_DICT[user.id],20)
      if int(x) != 0:
        return await message.reply_photo(photo=random.choice(PLAY_IMG), caption=f'ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ʙᴏᴡʟ ᴀɢᴀɪɴ ɪɴ ʟɪᴋᴇ `{get_readable_time(x)}`.')
  if len(message.command) < 2:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ᴏᴋ! ʙᴜᴛ ʜᴏᴡ ᴍᴜᴄʜ ʏᴏᴜ ᴀʀᴇ ɢᴏɴɴᴀ ʙᴇᴛ.")
  to_bet = message.command[1]
  coins = await user_wallet(user.id)
  if to_bet == '*':
      to_bet = coins
  elif not to_bet.isdigit():
       return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ʏᴏᴜ ᴛʜɪɴᴋs ᴛʜᴀᴛ ɪᴛ's ᴀ ᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ?")
  to_bet = int(to_bet)
  if to_bet == 0:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ʏᴏᴜ ᴡᴀɴɴᴀ ʙᴇᴛ 𝟶 ᴄᴏɪɴs ? ʟᴏʟ!") 
  elif to_bet > coins:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴍᴜᴄʜ ᴄᴏɪɴs ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ✑ `{0:,}` ᴄᴏɪɴs".format(coins))
  m = await client.send_dice(chat_id,'🎳')
  msg = await message.reply('....')
  u_won = await get_user_won(m.dice.emoji,m.dice.value)
  BOWL_DICT[user.id] = datetime.datetime.now().timestamp()
  if not u_won:
      new_wallet = coins - to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("🛑 sᴀᴅ ᴛᴏ sᴀʏ! ʙᴜᴛ ʏᴏᴜ ʟᴏsᴛ `{0:,}` ᴄᴏɪɴs\n• ᴄᴜʀᴇᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ✑ `{1:,}` ᴄᴏɪɴs".format(to_bet,new_wallet))
  else:
      new_wallet = coins + to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("✅ ᴡᴏᴡ! ʏᴏᴜ ᴡᴏɴ `{0:,}` ᴄᴏɪɴs\n• ᴄᴜʀᴇᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ✑ `{1:,}` ᴄᴏɪɴs.".format(to_bet,new_wallet))
  

@Guardian.on_message(filters.command("basket"))
async def _bet(client,message):
  chat_id = message.chat.id
  user = message.from_user
  if not await is_player(user.id):
     await create_account(user.id,message.from_user.username)  
  if user.id not in BASKET_DICT.keys():
      BASKET_DICT[user.id] = None     
  if BASKET_DICT[user.id]:
      x= await can_play(BASKET_DICT[user.id],20)
      if int(x) != 0:
        return await message.reply_photo(photo=random.choice(PLAY_IMG), caption=f'ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ʙᴀsᴋᴇᴛ ᴀɢᴀɪɴ ɪɴ ʟɪᴋᴇ `{get_readable_time(x)}`.')
  if len(message.command) < 2:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ᴏᴋ! ʙᴜᴛ ʜᴏᴡ ᴍᴜᴄʜ ʏᴏᴜ ᴀʀᴇ ɢᴏɴɴᴀ ʙᴇᴛ.")
  to_bet = message.command[1]
  coins = await user_wallet(user.id)
  if to_bet == '*':
      to_bet = coins
  elif not to_bet.isdigit():
       return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ʏᴏᴜ ᴛʜɪɴᴋs ᴛʜᴀᴛ ɪᴛ's ᴀ ᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ?")
  to_bet = int(to_bet)
  if to_bet == 0:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption="ʏᴏᴜ ᴡᴀɴɴᴀ ʙᴇᴛ 𝟶 ᴄᴏɪɴs ? ʟᴏʟ!") 
  elif to_bet > coins:
      return await message.reply_photo(photo=random.choice(PLAY_IMG), caption=_["minigames4"].format(coins))
  m = await client.send_dice(chat_id,'🏀')
  msg = await message.reply('....')
  u_won = await get_user_won(m.dice.emoji,m.dice.value)
  BASKET_DICT[user.id] = datetime.datetime.now().timestamp()
  if not u_won:
      new_wallet = coins - to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴍᴜᴄʜ ᴄᴏɪɴs ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ✑ `{0:,}` ᴄᴏɪɴs".format(to_bet,new_wallet))
  else:
      new_wallet = coins + to_bet
      await gamesdb.update_one({'user_id' : user.id}, {'$set' : {'coins' : new_wallet}})
      await asyncio.sleep(5)
      return await msg.edit_caption("✅ ᴡᴏᴡ! ʏᴏᴜ ᴡᴏɴ `{0:,}` ᴄᴏɪɴs\n• ᴄᴜʀᴇᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ✑ `{1:,}` ᴄᴏɪɴs.".format(to_bet,new_wallet))
