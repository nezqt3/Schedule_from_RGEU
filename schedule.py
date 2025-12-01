import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Schedule:
    def __init__(self, time):
        self.time = time
        self.url = os.getenv("URL")
        
        self.data = None
        
    def get_response(self):
        try:
            response = requests.get(url=self.url)
            self.data = response.json()
        except Exception as e:
            print(f"Error fetching api: {e}", flush=True)
            self.data = None
        
     
    def get_group(self):
        self.get_response()
        if self.data is None:
            return "API недоступен"
        return self.data.get('instance', '—')
    
    def get_schedule(self):
        lessons = []
        
        if self.data is None:
            return "API недоступно", "—", []

        for week in self.data['weeks']:
            for day in week['days']:
                date_today = day['date']
                day_date = datetime.strptime(date_today, "%d.%m.%Y").date()

                if day_date == self.time:
                    day_of_week = day['name']

                    for pair in day['pairs']:
                        if not pair['lessons']:
                            continue

                        time_str = f"{pair['startTime']} - {pair['endTime']}"
                        subject = pair['lessons'][0]['subject']
                        kind = pair['lessons'][0]['kind']['name']

                        subgroups = []
                        for entry in pair['lessons']:
                            subgroups.append({
                                "subgroup": entry['subgroup']['name'],
                                "teacher": entry['teacher']['name'],
                                "audience": entry['audience']
                            })

                        lessons.append({
                            "subject": subject,
                            "kind": kind,
                            "time": time_str,
                            "subgroups": subgroups
                        })

                    return day_of_week, date_today, lessons

        return "Нет занятий", "—", lessons
                        