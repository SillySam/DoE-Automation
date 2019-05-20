import requests
import json
import os
import datetime

class DOE:
    def __init__(self):
        self.session = None

    def login(self, email, password):
        ''' logs into the dashboard and returns the session (containing the cookie) '''
        self.session = requests.Session()
        r = requests.post(
            'https://www.onlinerecordbook.org/fo/authenticate?id=frontoffice-web&c=f',
            data={'username':email,'password':password,'client_id':'frontoffice-web'},
        )
        # Login failed
        if 'access_token' not in r.text:
            print('[!] Login Failed: ' + json.loads(r.text)['userMessage'])
            return False
        self.session.headers.update({'Authorization': 'Bearer ' + json.loads(r.text)['access_token']})
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        return True
    
    def get_activities(self):
        ''' Get all users's activities (minified responce)'''
        url  = 'https://www.onlinerecordbook.org/api/v1/awards?sort=-id&with=ADVENTUROUS_JOURNEYS,AJ_PREP_TRAINING,RESIDENTIAL_PROJECT,ACTIVITIES,ACTIVITIES_WITH_PROGRESS,AWARD_LEVEL,LEADER,PARTICIPANT_REGISTRATION_ASSESSMENT_STATE,PAYMENT_INFO&firstRow=0&maxRows=0&getTotalRowCount=false&userType=participant&locale=en-gb&timeZone=Pacific/Auckland&c=f'
        # TODO: Add checking if activities are already completed (will need to feed another variable into the returned dictonary)
        return json.loads(self.session.get(url).text)[0]['activities']

    def add_activity(self, activity_id, description, date=datetime.datetime.now().strftime("%Y-%m-%dT00:00:00"), time=3600):
        ''' Add log to an activity '''
        url  = 'https://www.onlinerecordbook.org/api/v1/activity-logs?userType=participant&locale=en-gb&timeZone=Pacific/Auckland&c=f'
        data = {
            'description': description,
            'duration': time,
            'date': date,
            'activity': {'id': str(activity_id) }
        }
        return self.session.post(url, json=data).text