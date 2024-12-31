import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from pydantic import BaseModel, validator
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .utils.auth import get_credentials
from .services.calendar_service import CalendarService


app = FastAPI(
    title="Google Calendar API",
    description="Google Calendar API",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class TaskStatus(str, Enum):
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: TaskStatus = TaskStatus.NEEDS_ACTION

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    created_at: str

class TaskList(BaseModel):
    id: str
    title: str

class TaskItem(BaseModel):
    id: str
    title: str
    notes: Optional[str] = None
    due: Optional[str] = None
    status: str
    position: Optional[str] = None
    parent: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    start: str
    end: str
    summary: str
    description: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    details: Optional[dict] = None

class EventCreate(BaseModel):
    summary: str
    start_time: str
    end_time: str
    description: Optional[str] = None

    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid datetime format')

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

@app.get("/")
async def root():
    return {"message": "Welcome to Google Calendar API"}

@app.get("/login")
async def login():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      client_config = json.loads(os.getenv("GOOGLE_CLIENT_CONFIG"))
      flow = InstalledAppFlow.from_client_config(
          client_config, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      return {"start": start, "summary": event["summary"]}

  except HttpError as error:
    print(f"An error occurred: {error}")

@app.get("/calendar/events", response_model=List[EventResponse])
async def calendar_events(
    max_results: int = 10,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None
):
    """获取日历事件列表"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("calendar", "v3", credentials=creds)
        
        if not time_min:
            time_min = datetime.utcnow().isoformat() + "Z"
        
        params = {
            "calendarId": "primary",
            "timeMin": time_min,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        if time_max:
            params["timeMax"] = time_max

        events_result = service.events().list(**params).execute()
        events = events_result.get("items", [])

        if not events:
            return []

        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event["id"],
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "summary": event["summary"],
                "description": event.get("description", "")
            })

        return [EventResponse(**event) for event in formatted_events]

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/calendar/events", response_model=MessageResponse)
async def create_event(event: EventCreate):
    """创建新的日历事件"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")
            
        calendar_service = CalendarService(creds)
        event_data = {
            'summary': event.summary,
            'description': event.description,
            'start': {
                'dateTime': event.start_time,
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': event.end_time,
                'timeZone': TIMEZONE,
            },
        }
        
        created_event = await calendar_service.create_event(event_data)
        return MessageResponse(
            message="事件创建成功",
            details={"eventId": created_event['id']}
        )
    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.put("/calendar/events/{event_id}")
async def update_event(
    event_id: str,
    summary: Optional[str] = Body(None),
    start_time: Optional[str] = Body(None),
    end_time: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
):
    """更新现有的日历事件"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("calendar", "v3", credentials=creds)
        
        # 首先获取现有事件
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # 更新提供的字段
        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if start_time:
            event['start']['dateTime'] = start_time
        if end_time:
            event['end']['dateTime'] = end_time

        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return {"message": "事件更新成功", "event": updated_event}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.delete("/calendar/events/{event_id}")
async def delete_event(event_id: str):
    """删除日历事件"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("calendar", "v3", credentials=creds)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return {"message": "事件删除成功"}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/tasks/lists", response_model=List[TaskList])
async def get_task_lists():
    """获取所有任务列表"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        results = service.tasklists().list(maxResults=100).execute()
        items = results.get("items", [])

        if not items:
            return []

        return [TaskList(id=item["id"], title=item["title"]) for item in items]

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/tasks/lists")
async def create_task_list(title: str = Body(...)):
    """创建新的任务列表"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        tasklist = service.tasklists().insert(body={"title": title}).execute()
        
        return {"id": tasklist["id"], "title": tasklist["title"]}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/tasks/lists/{tasklist_id}/tasks", response_model=List[TaskItem])
async def get_tasks(tasklist_id: str):
    """获取指定任务列表中的所有任务"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        results = service.tasks().list(tasklist=tasklist_id, maxResults=100).execute()
        items = results.get("items", [])

        if not items:
            return []

        return [
            TaskItem(
                id=item["id"],
                title=item["title"],
                notes=item.get("notes"),
                due=item.get("due"),
                status=item["status"],
                position=item.get("position"),
                parent=item.get("parent")
            ) 
            for item in items
        ]

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/tasks/lists/{tasklist_id}/tasks")
async def create_task(
    tasklist_id: str,
    title: str = Body(...),
    notes: Optional[str] = Body(None),
    due: Optional[str] = Body(None)
):
    """在指定的任务列表中创建新任务"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        
        task_body = {
            "title": title,
            "status": TaskStatus.NEEDS_ACTION.value
        }
        if notes:
            task_body["notes"] = notes
        if due:
            task_body["due"] = due

        task = service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
        
        return TaskItem(
            id=task["id"],
            title=task["title"],
            notes=task.get("notes"),
            due=task.get("due"),
            status=task["status"],
            position=task.get("position"),
            parent=task.get("parent")
        )

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.put("/tasks/lists/{tasklist_id}/tasks/{task_id}")
async def update_task(
    tasklist_id: str,
    task_id: str,
    title: Optional[str] = Body(None),
    notes: Optional[str] = Body(None),
    due: Optional[str] = Body(None),
    status: Optional[TaskStatus] = Body(None)
):
    """更新指定任务的信息"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        
        # 首先获取现有任务
        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        
        # 更新提供的字段
        if title:
            task["title"] = title
        if notes:
            task["notes"] = notes
        if due:
            task["due"] = due
        if status:
            task["status"] = status.value

        updated_task = service.tasks().update(
            tasklist=tasklist_id,
            task=task_id,
            body=task
        ).execute()
        
        return TaskItem(
            id=updated_task["id"],
            title=updated_task["title"],
            notes=updated_task.get("notes"),
            due=updated_task.get("due"),
            status=updated_task["status"],
            position=updated_task.get("position"),
            parent=updated_task.get("parent")
        )

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.delete("/tasks/lists/{tasklist_id}/tasks/{task_id}")
async def delete_task(tasklist_id: str, task_id: str):
    """删除指定的任务"""
    try:
        creds = await get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="认证失败")

        service = build("tasks", "v1", credentials=creds)
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        
        return {"message": "任务删除成功"}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=str(error))

