from datetime import datetime, timedelta, date
import requests
from bs4 import BeautifulSoup

from models import Appointment


WOCHENTAGE = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

class Dualis:
    def __init__(self, username=None, password=None):
        self.session = requests.Session()
        if username and password:
            self.login(username, password)


    def login(self, username, password):
        self.username = username
        self.password = password

        r = self.session.post("https://dualis.dhbw.de/scripts/mgrqispi.dll", data=
            f"usrname={self.username}&pass={self.password}&APPNAME=CampusNet&PRGNAME=LOGINCHECK&ARGUMENTS=clino%2Cusrname%2Cpass%2Cmenuno%2Cmenu_type%2Cbrowser%2Cplatform&clino=000000000000001&menuno=000324&menu_type=classic&browser=&platform="
        )
        if r.status_code != 200 or r.headers["REFRESH"].split("ARGUMENTS=")[1].split(",")[0] == "":
            raise Exception("Login failed")
        else:
            print("Login successful")

        self.arguments = r.headers["REFRESH"].split("ARGUMENTS=")[1].split(",")[0]


    def get_time_table_week(self, date: date) -> list:
        r = self.session.get(f"https://dualis.dhbw.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=SCHEDULER&ARGUMENTS={self.arguments},-N000030,-A{date.strftime('%d/%m/%Y')},-A,-N1,-N0,-N0")

        if r.status_code != 200:
            raise Exception("Request failed")


        soup = BeautifulSoup(r.text, 'html.parser')
        appointments = soup.find_all('td', class_='appointment')
        if not appointments:
            return []

        appointment_list = []
        for appointment in appointments:
            soup = BeautifulSoup(str(appointment), 'html.parser')
            appointment_date = appointment['abbr'].split(' ')[0]
            if appointment_date not in WOCHENTAGE: continue
            appointment_date = date + timedelta(days=WOCHENTAGE.index(appointment_date) - date.weekday())

            subject = soup.find('a', class_='link')['title']
            time_period = soup.find('span', class_='timePeriod')
            time_str = time_period.text.strip()[:13]
            room_element = time_period.find('a', class_='arrow')
            room = time_period.text.replace(time_str, '').strip() if room_element is None else room_element.text.strip()
            start_time, end_time = [datetime.strptime(t.strip(), '%H:%M').time() for t in time_str.split('-')]
            appointment_list.append(Appointment(appointment_date, start_time, end_time, subject, room))
        return appointment_list

