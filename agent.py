import datetime
import json
import os
from typing import List, Dict
import schedule
import time
import threading
import smtplib
from email.mime.text import MIMEText

class AICalendarAgent:
    def __init__(self, calendar_file='calendar.json'):
        """
        Initialize the AI Calendar Agent
        
        Args:
            calendar_file (str): Path to the calendar JSON file
        """
        self.calendar_file = calendar_file
        self.calendar_data = self.load_calendar()

    def load_calendar(self) -> List[Dict]:
        """
        Load calendar events from JSON file
        
        Returns:
            List of calendar events
        """
        try:
            with open(self.calendar_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_calendar(self):
        """
        Save calendar events to JSON file
        """
        with open(self.calendar_file, 'w') as f:
            json.dump(self.calendar_data, f, indent=2)

    def add_event(self, event: Dict):
        """
        Add a new event to the calendar
        
        Args:
            event (Dict): Event details with keys: 
                          'title', 'date', 'time', 'description'
        """
        # Validate event data
        required_keys = ['title', 'date', 'time']
        if not all(key in event for key in required_keys):
            raise ValueError("Event must have title, date, and time")

        self.calendar_data.append(event)
        self.save_calendar()
        print(f"Event '{event['title']}' added successfully!")

    def remove_event(self, event_title: str):
        """
        Remove an event from the calendar
        
        Args:
            event_title (str): Title of the event to remove
        """
        self.calendar_data = [
            event for event in self.calendar_data 
            if event['title'] != event_title
        ]
        self.save_calendar()
        print(f"Event '{event_title}' removed successfully!")

    def get_events_for_date(self, date: str) -> List[Dict]:
        """
        Get events for a specific date
        
        Args:
            date (str): Date in YYYY-MM-DD format
        
        Returns:
            List of events for the given date
        """
        return [
            event for event in self.calendar_data 
            if event['date'] == date
        ]

    def send_email_notification(self, event: Dict):
        """
        Send email notification for an event
        
        Args:
            event (Dict): Event details
        """
        # Note: Replace with your email configuration
        sender_email = "your_email@example.com"
        sender_password = "your_email_password"
        recipient_email = "your_email@example.com"

        msg = MIMEText(f"""
        Event Reminder:
        Title: {event['title']}
        Date: {event['date']}
        Time: {event['time']}
        Description: {event.get('description', 'No description')}
        """)
        msg['Subject'] = f"Reminder: {event['title']}"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Notification sent for event: {event['title']}")
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def start_notification_service(self):
        """
        Start background thread for event notifications
        """
        def check_events():
            today = datetime.date.today().strftime('%Y-%m-%d')
            today_events = self.get_events_for_date(today)
            
            for event in today_events:
                self.send_email_notification(event)

        # Run every day at midnight
        schedule.every().day.at("00:00").do(check_events)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def process_message(self, message: str):
        """
        Process natural language messages to manage calendar
        
        Args:
            message (str): User's message
        """
        message = message.lower()

        if 'add event' in message:
            # Simplified parsing - in real-world, use NLP
            parts = message.split('on')
            title = parts[0].replace('add event', '').strip()
            date_time = parts[1].strip().split()
            
            event = {
                'title': title,
                'date': date_time[0],
                'time': date_time[1] if len(date_time) > 1 else '09:00',
                'description': ''
            }
            self.add_event(event)

        elif 'remove event' in message:
            title = message.replace('remove event', '').strip()
            self.remove_event(title)

def main():
    agent = AICalendarAgent()
    
    # Start notification service in a separate thread
    notification_thread = threading.Thread(
        target=agent.start_notification_service, 
        daemon=True
    )
    notification_thread.start()

    # Example interactions
    agent.add_event({
        'title': 'Team Meeting', 
        'date': '2024-04-15', 
        'time': '10:00', 
        'description': 'Quarterly review'
    })

    # Simulating message processing
    agent.process_message("add event project review on 2024-04-20 14:00")

if __name__ == "__main__":
    main()
