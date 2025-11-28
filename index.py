import os
from telebot import TeleBot
from apscheduler.schedulers.blocking import BlockingScheduler
from schedule import Schedule
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Main:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.ids = [os.getenv("FIRST_USER_ID"), os.getenv("SECOND_USER_ID")]
        self.bot = TeleBot(self.token)
        self.scheduler = BlockingScheduler()
        
    def _send_schedule(self):
        now = datetime.now()
        date = now.date()

        schedule = Schedule(date)
        group = schedule.get_group()
        day_of_week, date_today, lessons = schedule.get_schedule()

        for chat_id in self.ids:

            if not lessons:
                text = (
                    f"📅 {day_of_week}, {date_today}\n"
                    f"🎓 Группа: {group}\n\n"
                    f"Сегодня пар нет 🙂"
                )
                self.bot.send_message(chat_id=chat_id, text=text)
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

            self.bot.send_message(chat_id=chat_id, text=text)
        
    def start(self):
        self.scheduler.add_job(self._send_schedule, "cron", hour=8, minute=0)
        self.scheduler.start()

main = Main()
main.start()
