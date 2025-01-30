import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Load environment variables from .env file
load_dotenv()

# Initialize with your tokens
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_DOC_ID = os.getenv('GOOGLE_DOC_ID')  # The ID of your Google Doc
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')  # Path to your service account JSON file

# Validate environment variables
if not all([TELEGRAM_TOKEN, GOOGLE_DOC_ID, GOOGLE_CREDENTIALS_FILE]):
    raise ValueError("Missing required environment variables. Please check your .env file")

# Initialize Google Docs client
SCOPES = ['https://www.googleapis.com/auth/documents']
credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
)
docs_service = build('docs', 'v1', credentials=credentials)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I can help you add agent links to the README. Use /add followed by the link.')

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add an agent link to the Google Doc when /add command is used."""
    try:
        # Check if this is a reply to another message
        replied_message = update.message.reply_to_message
        
        # Get the text either from reply or command args
        if replied_message:
            text_to_add = replied_message.text
        elif context.args:
            text_to_add = ' '.join(context.args)
        else:
            await update.message.reply_text('Please either reply to a message with /addagent or provide text after the command.')
            return

        try:

            # Calculate the full text to be inserted
            full_text = f'\n\n―――――――――――――――――――――――――――――――――\n\n{text_to_add}'
            
            # Append the new text with horizontal lines
            requests = [
                {
                    'insertText': {
                        'endOfSegmentLocation': {
                            "segmentId": "",
                            "tabId": ""
                        },
                        'text': full_text
                    }
                }
            ]    
            # Execute the update
            docs_service.documents().batchUpdate(
                documentId=GOOGLE_DOC_ID,
                body={'requests': requests}
            ).execute()

            await update.message.reply_text('Successfully added the text to the document!')

        except Exception as e:
            await update.message.reply_text(f'Error updating document: {str(e)}')

    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
