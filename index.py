import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# It's recommended to use environment variables for sensitive information
TOKEN = os.getenv("TOKEN", "7408716433:AAGFkyLuniEG2Z7Ip5vvpCLhfTUU-w5Tlxw")
URL = "https://obilo-repo.vercel.app"
bot = Bot(TOKEN)

# Dictionary to track user search status
user_searching = {}

def welcome(update, context) -> None:
    user_first_name = update.message.from_user.first_name
    welcome_message = (f"Hello {user_first_name}, Welcome to AI Movies.\n"
                       f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    logger.info(f"User {update.message.from_user.id} started the bot.")
    update.message.reply_text(welcome_message)
    update.message.reply_text("👇 Enter Movie Name 👇")

def find_movie(update, context):
    user_id = update.message.from_user.id
    query = update.message.text.strip()

    logger.info(f"User {user_id} is searching for '{query}'.")

    # Check if the user is already processing a search
    if user_searching.get(user_id, False):
        logger.info(f"User {user_id} is already searching. Ignoring duplicate request.")
        update.message.reply_text("Please wait, your previous search is still being processed...")
        return

    # Mark the user as searching
    user_searching[user_id] = True
    update.message.reply_text("Processing...")

    try:
        movies_list = search_movies(query)
        logger.info(f"Found {len(movies_list)} movies for query '{query}'.")
    except Exception as e:
        logger.error(f"Error during search_movies for query '{query}': {e}")
        update.message.reply_text("An error occurred while searching for movies. Please try again later.")
        user_searching[user_id] = False
        return

    # Mark the user as no longer searching
    user_searching[user_id] = False

    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        update.message.reply_text('Search Results:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

def movie_result(update, context) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    movie_id = query.data

    logger.info(f"User {user_id} selected movie with ID '{movie_id}'.")

    try:
        s = get_movie(movie_id)
        if not s:
            query.message.reply_text("Failed to retrieve movie details.")
            return

        if s["img"]:
            response = requests.get(s["img"])
            img = BytesIO(response.content)
            query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
            logger.info(f"Sent photo for movie '{s['title']}' to user {user_id}.")
        else:
            query.message.reply_text(f"🎥 {s['title']}")

        links = s["links"]
        if links:
            link_text = ""
            for name, url in links.items():
                link_text += f"🎬 {name}\n{url}\n\n"
            caption = f"⚡ Fast Download Links:\n\n{link_text}"
            
            # Telegram message limit is 4096 characters
            for x in range(0, len(caption), 4095):
                query.message.reply_text(text=caption[x:x+4095])
            logger.info(f"Sent download links for movie '{s['title']}' to user {user_id}.")
        else:
            query.message.reply_text("No download links available for this movie.")
            logger.info(f"No download links found for movie '{s['title']}'.")

    except Exception as e:
        logger.error(f"Error in movie_result for movie ID '{movie_id}': {e}")
        query.message.reply_text("An error occurred while fetching movie details. Please try again later.")

def setup():
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
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        setup().process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'Internal Server Error', 500

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    try:
        webhook_url = f"{URL}/{TOKEN}"
        s = bot.setWebhook(webhook_url)
        if s:
            logger.info("Webhook setup successfully.")
            return "Webhook setup ok", 200
        else:
            logger.error("Webhook setup failed.")
            return "Webhook setup failed", 500
    except Exception as e:
        logger.error(f"Exception during webhook setup: {e}")
        return "Webhook setup failed due to an exception.", 500
            
