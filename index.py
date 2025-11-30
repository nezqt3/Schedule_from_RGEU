from flask import Flask
from telebot import TeleBot
from apscheduler.schedulers.background import BackgroundScheduler
from schedule import Schedule
import os
from datetime import datetime, timedelta
from pytz import timezone
import threading
import time

app = Flask(__name__)

token = os.getenv("TOKEN")
ids = [
    os.getenv("FIRST_USER_ID"),
    os.getenv("SECOND_USER_ID"),
    os.getenv("THIRD_USER_ID")
]
bot = TeleBot(token)

scheduler = BackgroundScheduler()

def send_schedule():
    print("CRON: running...", flush=True)

    now = datetime.now()
    date = now.date() + timedelta(days=1)

    schedule = Schedule(date)
    group = schedule.get_group()
    day_of_week, date_today, lessons = schedule.get_schedule()

    for chat_id in ids:
        if not chat_id:
            continue

        if not lessons:
            text = (
                f"📅 {day_of_week}, {date_today}\n"
                f"🎓 Группа: {group}\n\n"
                f"Сегодня пар нет 🙂"
            )
            bot.send_message(chat_id, text)
            continue

        text = (
            f"📅 {day_of_week}, {date_today}\n"
            f"🎓 Группа: {group}\n\n"
            f"📘 Расписание:\n"
        )

        for idx, lesson in enumerate(lessons, 1):
            text += f"\n{idx}) {lesson['subject']} ({lesson['kind']})"
            text += f"\n   ⏰ {lesson['time']}\n"

            for subgroup in lesson['subgroups']:
                text += (
                    f"   🔹 {subgroup['subgroup']}\n"
                    f"      👨‍🏫 {subgroup['teacher'] or '—'}\n"
                    f"      🏫 {subgroup['audience'] or '—'}\n"
                )
            text += "\n"

        bot.send_message(chat_id, text)

scheduler.add_job(send_schedule, "cron", hour=15, minute=0, timezone=timezone("Europe/Moscow"))
scheduler.add_job(send_schedule, "cron", hour=8, minute=0, timezone=timezone("Europe/Moscow"))
scheduler.add_job(send_schedule, "cron", hour=22, minute=9, timezone=timezone("Europe/Moscow"))
scheduler.add_job(send_schedule, "cron", hour=22, minute=18, timezone=timezone("Europe/Moscow"))

def run_schedule():
    scheduler.start()
    print("Scheduler started", flush=True)

def run_flask():
    app.run(host="0.0.0.0", port=3000)

def keep_alive():
    while True:
        print("alive", flush=True)
        time.sleep(30)

threading.Thread(target=run_schedule, daemon=True).start()
threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
