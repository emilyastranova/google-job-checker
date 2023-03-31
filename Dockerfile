FROM python:3.10-alpine

WORKDIR /app

# Install selenium/ChromeDriver
RUN apk add --no-cache chromium-chromedriver

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY main.py .
COPY utils.py .

# Run the app (looping and with Telegram notifications)
CMD ["python", "main.py", "-lt"]
