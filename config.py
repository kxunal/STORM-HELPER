from os import getenv
from dotenv import load_dotenv

load_dotenv()

#Necessary Variables 
API_ID = int(getenv("API_ID", ))
API_HASH = getenv("API_HASH", )
BOT_TOKEN = getenv("BOT_TOKEN") #Put your bot token here
LOG_ID = int(getenv("LOG_ID"))
SUDOERS = list(map(int, getenv("SUDOERS", "").split()))
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
