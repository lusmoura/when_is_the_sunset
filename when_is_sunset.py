#!/usr/bin/env python3

import os
import pickle
from datetime import datetime

from requests_html import HTMLSession
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Calendar:
    '''
        Class to wrap all functions related to google calendar
    '''
    
    def __init__(self):
        SCOPES = "https://www.googleapis.com/auth/calendar"
        
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_event(self, moment):
        '''
            Gets the event description

            Params: moment when sunset starts
            Retrun: dictionary with all event info
        '''

        date = datetime.now()
        start_time = date.replace(hour=moment.hour, minute=moment.minute)
        end_time = start_time + timedelta(minutes=30)

        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')

        event = {
            'summary': 'Pôr do Sol',
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Sao_Paulo',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 20},
                ],
            },
        }

        return event
    
    def add_event(self, hour):
        '''
            Adds event to google calendar

            Params: hour that sunset starts 
        '''
        calendar_list_entry = self.service.calendarList().get(calendarId='primary').execute()
        
        if calendar_list_entry['accessRole']:
            event = self.get_event(hour)
            event = self.service.events().insert(calendarId='primary', body=event).execute()

def get_hour(city=""):
    '''
        Gets sunset hour from google

        Params: city - where you want the get the sunset hour
        Return: hour as a datetime object
    '''

    url = f'https://www.google.com/search?q=por+do+sol+horario+{city}'
    
    session = HTMLSession()
    request = session.get(url)
    selector = '#rso > div:nth-child(1) > div > div.BmP5tf > w-answer > w-answer-desktop > div.MUxGbd.t51gnb.lyLwlc.lEBKkf'
    value_text = request.html.find(selector, first=True).text
    hour = datetime.strptime(value_text, '%H:%M')
    
    return hour

if __name__ == '__main__':
    hour = get_hour()
    Calendar().add_event(hour)