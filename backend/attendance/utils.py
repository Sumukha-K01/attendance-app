import requests
import json

def send_absent_sms(to_number, parent_name, student_name, roll_number, date, school_name):
    url = "https://control.msg91.com/api/v5/flow/"

    payload = {
        "flow_id": "YOUR_FLOW_ID",           # Use your actual Flow ID
        "sender": "SCHOOL",                  # Approved Sender ID (6 characters)
        "mobiles": f"91{to_number}",
        "parent_name": parent_name,
        "student_name": student_name,
        "roll_number": roll_number,
        "date": date,
        "school_name": school_name
    }

    headers = {
        "authkey": "YOUR_AUTH_KEY",          # Replace with your MSG91 Auth Key
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()
