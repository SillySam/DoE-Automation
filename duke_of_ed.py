import requests
import config
import json
import datetime
import schedule
from time import sleep
import os

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
        return json.loads(self.session.get(url).text)[0]['activities']

    def add_activity(self, activity_id, description, date, time=3600):
        ''' Add log to an activity '''
        url  = 'https://www.onlinerecordbook.org/api/v1/activity-logs?userType=participant&locale=en-gb&timeZone=Pacific/Auckland&c=f'
        data = {
            'description': description,
            'duration': time,
            'date': date,
            'activity': {'id': str(activity_id) }
        }
        self.session.post(url, json=data)

def fill_activities():
    ''' Enter information into the dashboard '''
    print('[+] Logging in!')
    doe  = DOE()
    if doe.login(config.EMAIL, config.PASSWORD):
        date = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00")

        # Generate tasksheet if not found
        if not os.path.isfile('tasks.json'):
            create_tasksheet(doe)
            print('[!] Generated tasksheet - fill this in before running again')
            exit(0)
        
        # Load data from file
        f = open('tasks.json', 'r')
        loaded_json = json.loads(f.read())
        print('[!] Found `tasks.json`, analysing...')
        f.close()          

        # Iterate tasks
        added = 0
        for id, value in loaded_json.items():
            description = value['descriptions'][0]
            print('[+] Adding {} {}: {}'.format(value['name'], value['type'], description[0]))
            if description != '':
                doe.add_activity(id, description, date)
                del value['descriptions'][0]
                added += 1
        
        # Close
        if added < 1:
            print('[-] Nothing was added, therefore lists are all clear. Stopping')
            exit(0)

        # Save new json
        f = open('tasks.json', 'w')
        f.write(loaded_json)
        f.close()

def create_tasksheet(doe):
    ''' Generate task sheet '''
    output = {}
    for activity in doe.get_activities():
        output.update({
            activity['id']: {
                'type': activity['activitySection']['value'],
                'name': activity['activityCategory']['name'],
                'descriptions': [
                    ''
                ]
            }
        })
    f = open('tasks.json', 'w')
    f.write(json.dumps(output, indent=4, sort_keys=True))
    f.close()

if __name__ == "__main__":
    schedule.every().wednesday.do(fill_activities)
    while True:
        schedule.run_pending()
        sleep(10)
