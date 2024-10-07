import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie  # Importing from your scraper module

TOKEN = "7408716433:AAGFkyLuniEG2Z7Ip5vvpCLhfTUU-w5Tlxw"
URL = "https://obilo-repo.vercel.app"
bot = Bot(TOKEN)

# Dictionary to track user search status
user_searching = {}

def welcome(update, context) -> None:
    """ Welcome message when user starts the bot. """
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to AI Movies.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")

def find_movie(update, context):
    """ Process movie search based on user input. """
    user_id = update.message.from_user.id

    # Check if the user is already processing a search
    if user_searching.get(user_id, False):
        update.message.reply_text("Please wait, your previous search is still being processed...")
        return

    # Mark the user as searching
    user_searching[user_id] = True
    update.message.reply_text("Processing...")
    
    query = update.message.text
    movies_list = search_movies(query)  # Call the movie scraper function
    
    # Mark the user as no longer searching
    user_searching[user_id] = False
    
    if movies_list:
        # Create buttons for each movie found
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        update.message.reply_text('Search Results:', reply_markup=reply_markup)
    else:
        # No results found
        update.message.reply_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

def movie_result(update, context) -> None:
    """ Show movie details and download links. """
    query = update.callback_query
    s = get_movie(query.data)  # Get the selected movie details
    
    # If the movie has an image, download it and send it as a photo
    if s.get("img"):
        response = requests.get(s["img"])
        img = BytesIO(response.content)
        query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    
    # Prepare the download links
    link = ""
    links = s["links"]
    for i in links:
        link += f"🎬 {i}\n{links[i]}\n\n"
    
    caption = f"⚡ Fast Download Links:\n\n{link}"
    
    # Send the links in parts if the caption is too long for Telegram's limit
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)

def setup():
    """ Setup the bot's command and message handlers. """
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    """ Webhook listener for processing updates. """
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    """ Set webhook for the Telegram bot. """
    s = bot.setWebhook(f'{URL}/{TOKEN}')
    if s:
        return "Webhook setup ok

    else:
        return "Webhook setup failed"
