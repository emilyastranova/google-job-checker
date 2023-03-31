# Google Job Checker

The Google Job Checker is a Python script that checks Google's Careers site for changes in the job listings. The script uses Selenium to scrape the page and generate a report of any changes found. It can also send a message to a specified Telegram user when changes are found.

## Requirements

- Python 3.6 or higher
- Selenium
- Loguru
- Telebot
- Dotenv

## Usage

1. Clone the repository and navigate to the project directory:

    ```bash
    git clone https://github.com/tyleraharrison/google-job-checker.git
    cd google-job-checker
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set the required environment variables in a `.env` file:

    ```makefile
    QUERY="Your Google Careers query"
    TELEGRAM_TOKEN="Your Telegram Bot token"
    TELEGRAM_USER_ID="Your Telegram user ID"

4. Run the script:

    ```bash
    python3 main.py
    ```

## Options

The script supports the following options:

- `-v, --verbose`: Enable verbose logging
- `-l, --loop`: Run the script in a loop
- `-s, --seconds`: The time to sleep in seconds (default: 1800)
- `-t, --telegram`: Send a Telegram message when changes are found

## Docker

The script can also be run in a Docker container using the provided `Dockerfile` and `docker-compose.yml` files. To run the script in a Docker container, follow these steps:

1. Build the Docker image:

    ```bash
    docker compose build
    ```

2. Run the Docker container:

    ```bash
    docker compose up
    ```

## Notes

- The script saves the job listings links and the changes report to `links.json` and `changes.json`, respectively.
- The script initializes the driver in headless mode to avoid opening a browser window. However, you may remove the `--headless` option to run the script in non-headless mode for debugging purposes.
- The script handles the `SIGINT` signal (Ctrl+C) to exit gracefully.
