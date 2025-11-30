from flask import Flask
from telebot import TeleBot
from apscheduler.schedulers.background import BackgroundScheduler
from schedule import Schedule
import os
from datetime import datetime, timedelta

app = Flask(__name__)

token = os.getenv("TOKEN")
ids = [os.getenv("FIRST_USER_ID"), os.getenv("SECOND_USER_ID"), os.getenv("THIRD_USER_ID")]
bot = TeleBot(token)

scheduler = BackgroundScheduler()

def send_schedule():
    now = datetime.now()
    date = now.date() + timedelta(days=1)

    schedule = Schedule(date)
    group = schedule.get_group()
    day_of_week, date_today, lessons = schedule.get_schedule()

    for chat_id in ids:
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

scheduler.add_job(send_schedule, "cron", hour=15, minute=0)
scheduler.add_job(send_schedule, "cron", hour=8, minute=0)  
scheduler.add_job(send_schedule, "cron", hour=22, minute=30)  
scheduler.start()

@app.get("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
