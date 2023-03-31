#!/usr/bin/env python3
"""Check Google's Careers site for changes in the job listings."""
import os
import sys
import json
import time
import signal
from argparse import ArgumentParser
from selenium import webdriver
from loguru import logger
import telebot
from dotenv import load_dotenv
from utils import scrape, generate_report

# Load the environment variables
load_dotenv()
QUERY = os.getenv("QUERY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

# Handle the SIGINT signal (Ctrl+C)
def handler(signum, frame): # pylint: disable=unused-argument
    """Handle the SIGINT signal."""
    print() # Newline after Ctrl+C character (^C)
    logger.info("[!] Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

@logger.catch
def main(telegram_bot: telebot.TeleBot = None):
    """Main function."""
    logger.info("Starting")

    # Initialize the driver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    # Scrape the page
    logger.info("Scraping query: {}", QUERY)
    links, changes = scrape(QUERY, driver)
    if changes:
        changes_report = generate_report(changes)
        logger.info(changes_report)

        # Save the changes
        with open("data/changes.json", "w", encoding="utf-8") as file:
            json.dump(changes, file, indent=4)
            logger.info("Saved changes")

        # If Telegram is enabled, send a message
        if telegram_bot:
            logger.debug("Sending Telegram message")
            telegram_bot.send_message(TELEGRAM_USER_ID, changes_report)
            logger.success("Sent Telegram message")
    else:
        logger.info("No changes found")

    # Save the links
    with open("data/links.json", "w", encoding="utf-8") as file:
        json.dump(links, file, indent=4)
        logger.info("Saved links")

    logger.success("Finished")

if __name__ == "__main__":
    # Parse the arguments
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-l", "--loop", action="store_true", help="Run the script in a loop")
    parser.add_argument("-s", "--seconds", type=int, default=1800, \
                        help="The time to sleep in seconds")
    parser.add_argument("-t", "--telegram", action="store_true", \
                        help="Send a Telegram message when changes are found")
    args = parser.parse_args()

    # Configure the logger
    if args.verbose:
        logger.debug("Verbose logging enabled")
        logger.enable("utils")

    # Make links.json and changes.json if they don't exist
    if not os.path.exists("data/links.json"):
        logger.debug("Creating links.json")
        with open("data/links.json", "w", encoding="utf-8") as file:
            json.dump([], file)

    if not os.path.exists("data/changes.json"):
        logger.debug("Creating changes.json")
        with open("data/changes.json", "w", encoding="utf-8") as file:
            json.dump([], file)

    # Check if the required environment variables are set
    if not QUERY:
        logger.error("QUERY environment variable not set")
        sys.exit(1)

    # Initialize the Telegram bot
    if args.telegram:
        logger.info("Initializing Telegram bot")
        try:
            bot = telebot.TeleBot(TELEGRAM_TOKEN)
            bot.send_message(TELEGRAM_USER_ID, "Bot initialized")
            logger.success("Initialized Telegram bot")
        except Exception as error: # pylint: disable=broad-except
            logger.error("Failed to initialize Telegram bot: {}", error)
            # Disable Telegram if it fails to initialize
            bot = None # pylint: disable=invalid-name

    # Run the main function every specified number of seconds if looping is enabled
    if args.loop:
        logger.info("Looping enabled ({} seconds)", args.seconds)
        while True:
            main(telegram_bot=bot)
            logger.info("Sleeping for {} seconds", args.seconds)
            time.sleep(args.seconds)
    else:
        main(telegram_bot=bot)
