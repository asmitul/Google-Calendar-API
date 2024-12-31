from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self, credentials: Credentials):
        self.service = build("calendar", "v3", credentials=credentials)
    
    async def get_events(self, params: dict):
        try:
            events_result = self.service.events().list(**params).execute()
            return events_result.get("items", [])
        except HttpError as error:
            raise error

    async def create_event(self, event_data: dict):
        try:
            return self.service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
        except HttpError as error:
            raise error 