import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import html

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = '@MyTriviaGameBot'
categories = {
    1: "Random",
    2: "General Knowledge",
    3: "Entertainment: Books",
    4: "Entertainment: Film",
    5: "Entertainment: Music",
    6: "Entertainment: Musicals & Theatres",
    7: "Entertainment: Television",
    8: "Entertainment: Video Games",
    9: "Entertainment: Board Games",
    10: "Science & Nature",
    11: "Science: Computers",
    12: "Science: Mathematics",
    13: "Mythology",
    14: "Sports",
    15: "Geography",
    16: "History",
    17: "Politics",
    18: "Art",
    19: "Celebrities",
    20: "Animals",
    21: "Vehicles",
    22: "Entertainment: Comics",
    23: "Science: Gadgets",
    24: "Entertainment: Japanese Anime & Manga",
    25: "Entertainment: Cartoon & Animations"
}

user_questions = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = {
        "user_id": str(update.message.from_user.id)
    }
    requests.post("https://trivia-poc-server.onrender.com/trivia/start", json=data)
    user = update.message.from_user
    categories_text = ""
    for key, value in categories.items():
        categories_text += f"({key}) - {value}\n"

    await update.message.reply_text(f"Hello {user.first_name}\nTrivia game started\nSelect one of the following categories:\n{categories_text}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    categories_text = ""
    for key, value in categories.items():
        categories_text += f"({key}) - {value}\n"
    await update.message.reply_text(f"Send a category and I will give you a trivia question\nList of avialable categories are:\n{categories_text}")

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = {
        "user_id": str(update.message.from_user.id)
    }
    response = requests.get("https://trivia-poc-server.onrender.com/trivia/score", json=data).json()
    user = response['user']
    await update.message.reply_text(f"Your score is: {user['score']} points")

# Response

def handle_response(text: str) -> str:
    category_id = int(text)

    if category_id in categories:
        response = requests.get(f"https://trivia-poc-server.onrender.com/trivia/{categories[category_id]}").json()
        question = html.unescape(response["question"])
        correct_answer = response["correct_answer"]  # Assuming your API returns this
        return question, correct_answer
    else:
        return None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    user_id = update.message.from_user.id

    if user_id in user_questions:
        if message.lower() != "true" and message.lower() != "false" and message.lower() != "t" and message.lower() != "f":
            await update.message.reply_text("Please enter 'true' or 'false'.")
            return
        correct_answer = user_questions[user_id]['correct_answer']
        if message.lower() == 'f':
            message = "false"
        if message.lower() == 't':
            message = "true"
        if message.lower() == correct_answer.lower():
            await update.message.reply_text("Correct! 🎉")
            data = {
                "user_id": str(update.message.from_user.id)
            }
            requests.post("https://trivia-poc-server.onrender.com/trivia/score", json=data)
            del user_questions[user_id]
        else:
            await update.message.reply_text("Incorrect. 😢")
            del user_questions[user_id]
    else:
        question, correct_answer = handle_response(message)
        if question:
            user_questions[user_id] = {'question': question, 'correct_answer': correct_answer}
            await update.message.reply_text(f"True or False: {question}" )
        else:
            await update.message.reply_text("I don't know that category. Please try again. Use /help to see all categories.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("starting bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("score", score_command))
    
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print("polling...")
    app.run_polling(poll_interval=3)
