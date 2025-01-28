import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from github import Github
import base64

# Load environment variables from .env file
load_dotenv()

# Initialize with your tokens
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPO') 
print(f"Loaded TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")  # Check initial load
 # format: "username/repository"

# Validate environment variables
if not all([TELEGRAM_TOKEN, GITHUB_TOKEN, REPO_NAME]):
    raise ValueError("Missing required environment variables. Please check your .env file")

# Initialize GitHub client
g = Github(GITHUB_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I can help you add agent links to the README. Use /addagent followed by the link.')

async def add_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add an agent link to the README when /addagent command is used."""
    try:
        # Get the link from the message
        if not context.args:
            await update.message.reply_text('Please provide a link after the /addagent command.')
            return

        link = ' '.join(context.args)

        # Get the repository
        repo = g.get_repo(REPO_NAME)

        try:
            # Get the README file
            readme_content = repo.get_contents("README.md")
            current_content = base64.b64decode(readme_content.content).decode('utf-8')

            # Add the new link to the content
            new_content = current_content + f"\n- {link}"

            # Update the README
            repo.update_file(
                path="README.md",
                message="Add new agent link via Telegram bot",
                content=new_content,
                sha=readme_content.sha
            )

            await update.message.reply_text('Successfully added the link to README!')

        except Exception as e:
            await update.message.reply_text(f'Error updating README: {str(e)}')

    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addagent", add_agent))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
