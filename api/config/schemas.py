from typing import List
from pydantic import BaseModel, ConfigDict, PrivateAttr
from enum import Enum


class ErrorMSG(BaseModel):
    result: bool = False
    error_type: str
    error_message: str

    model_config = ConfigDict(from_attributes=True)


class MSG(BaseModel):
    result: str

    model_config = ConfigDict(from_attributes=True)


class SendMSGAnswer(BaseModel):
    msgId: str | None = None
    description : str | None = None
    ok: bool

class EventAnswer(BaseModel):
    event_id : str
    answer: str

class EventsSCH(BaseModel):
    id: int
    group_id: str | None = None
    city: str | None = None
    user_id: str
    message_text: str
    message_id: str
    status_event : str

    model_config = ConfigDict(from_attributes=True)


class GetEvents(BaseModel):
    result: str
    events: List[EventsSCH]

    model_config = ConfigDict(from_attributes=True)

class SendMSG(BaseModel):
    text : str
    msg_id: str | None = None
    user_id : str

    model_config = ConfigDict(from_attributes=True)

class EventsStatus(str, Enum):
    NEW = "NEW"
    FINISHED = "FINISHED"
    IN_PROCESSING = "IN_PROCESSING"


class UpdateEvents(BaseModel):
    event_id : int
    status_ev : EventsStatus

    model_config = ConfigDict(from_attributes=True)