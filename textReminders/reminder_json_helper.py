import os
import json
from datetime import datetime

def reminder_json_exists():
    return os.path.isfile('reminder.json')

def read_reminder_json():
    if reminder_json_exists():
        with open('reminder.json') as reminder_json:
            data = json.load(reminder_json)
            reminders = data.get('reminders', [])
            for reminder in reminders:
                if 'due_time' in reminder:
                    reminder['due_time'] = datetime.strptime(reminder['due_time'], '%H:%M:%S').time()
            return reminders
    else:
        return []

def create_reminder_json(reminder):
    if not reminder_json_exists():
        data = {}
        data['reminders'] = []
        data['reminders'].append(reminder)
        write_reminder_json(data)
    else:
        update_reminder_json(reminder)

def update_reminder_json(reminder):
    with open('reminder.json') as reminder_json:
        data = json.load(reminder_json)
        reminders = data.get('reminders', [])
        reminder_index = next((index for (index, r) in enumerate(reminders) if r['id'] == reminder['id']), None)
        if reminder_index is not None:
            reminders[reminder_index] = reminder
        else:
            reminders.append(reminder)
        write_reminder_json(data)

def write_reminder_json(data, filename='reminder.json'):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)
