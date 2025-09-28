from fastapi import APIRouter, Depends, status
from app.func.events_func import get_events, change_events
from app.config.schemas import GetEvents,SendMSG, MSG


events_router = APIRouter(tags=["Работа с событиями"])


@events_router.get(
    "/api/events",
    status_code=status.HTTP_200_OK,
    response_model=GetEvents,
    name="Получение сообщений для обработки",
    description="Получение сообщений для обработки",
)
async def get_events_route(events = Depends(get_events)) -> GetEvents:
    return {"result": "true", "events": events}

@events_router.post(
    "/api/events",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Получение сообщений для обработки",
    description="Получение сообщений для обработки",
)
async def post_events_route(result = Depends(change_events)) -> MSG:
    return result