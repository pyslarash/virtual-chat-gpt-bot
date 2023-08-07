import os
import openai
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN: Final = '6501086288:AAGtQcg8G1cM1MiAm0h-VYoqivpZIrA_CW8'
BOT_USERNAME: Final = '@VirtualChatGptBot'
GPT_TOKEN = ''

openai.api_key = GPT_TOKEN

# Commands

# This command starts the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global API_KEY_SET
    API_KEY_SET = False  # Reset the flag when /start is called
    await update.message.reply_text("Hey there! I am a bot that incorporates ChatGPT technology (based on GPT-3.5-Turbo). In order to start, I need your ChatGPT API key. Please, enter it below.")

# This command stops the bot
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is turning off. Goodbye!")
    context.application.stop_polling()

# Here we are validating the API key and if it's valid, we are starting the bot
def handle_response(text: str) -> str:
    global GPT_TOKEN, API_KEY_SET

    if not API_KEY_SET:
        # Check if the user provided an API key in the message text
        if text:
            api_key = text.strip()

            # Validate the API key by making a simple API call
            openai.api_key = api_key
            try:
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=0.5,
                    max_tokens=5,
                )
                GPT_TOKEN = api_key
                API_KEY_SET = True
                response_text = "API key successfully set. You can now chat with your ChatGPT."
            except openai.error.AuthenticationError:
                response_text = "Invalid API key. Please try again with a valid key."
        else:
            response_text = "Please enter your full API key from OpenAI."

        return response_text
    else:
        # Start using ChatGPT
        response = chatgpt_at_work(text)
        return response
    
def chatgpt_at_work(text: str) -> str:
    # You can use the global GPT_TOKEN variable here since it should be set by now
    global GPT_TOKEN

    # Set the API key before making the API call
    openai.api_key = GPT_TOKEN

    # Call the ChatGPT API to get a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        temperature=0.5,
        max_tokens=256,
    )

    # Extract the response from the API response
    response_text = response.choices[0].message['content']

    return response_text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
        
    print('Bot:', response)
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    

if __name__ == '__main__':
    print('Statring bot...')
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('stop', stop_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(error)
    
    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)