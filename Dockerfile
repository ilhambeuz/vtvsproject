FROM python:3.11-slim

# ffmpeg o'rnatish
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt && pip install -U yt-dlp

COPY . .

CMD ["python", "bot.py"]
