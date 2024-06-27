from pyrogram import filters
import requests
import time
import os
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

@app.on_message(filters.command("imagine", prefixes=["/", "!"]))
async def draw_prompt(app, message):
    add_user_database(message.from_user.id)  # Add user to the database
    
    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "beautiful sunset"
    
    if query.startswith("http"):
        response = requests.get(query)
        image_data = response.content
    else:
        response = requests.get("https://source.unsplash.com/random/?" + query)
        image_data = response.content
    
    if response.status_code == 200:
        try:
            if image_data:
                destination_dir = ''
                destination_path = os.path.join(destination_dir, 'generated_image.jpg')
                
                with open(destination_path, 'wb') as f:
                    f.write(image_data)
                
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=destination_path
                )
            else:
                await app.send_message(message.chat.id, "Failed to get image from the server.")
        except Exception as e:
            await app.send_message(message.chat.id, f"Error: {e}")
    else:
        await app.send_message(message.chat.id, f"Error: {response.status_code}")
