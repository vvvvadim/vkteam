from fastapi import APIRouter, Depends, status
from api.func.events_func import get_events, change_events,answer_event
from api.config.schemas import GetEvents,SendMSG, MSG


events_router = APIRouter(tags=["Работа с событиями"])


@events_router.get(
    "/api/events",
    status_code=status.HTTP_200_OK,
    response_model=GetEvents,
    name="Получение сообщений для обработки",
    description="Получение сообщений для обработки",
)
async def get_events_route(events = Depends(get_events)) -> GetEvents:
# async def get_events_route(events = Depends(get_events)):
    return {"result": "true", "events": events}

@events_router.put(
    "/api/events",
    status_code=status.HTTP_200_OK,
    response_model=MSG,
    name="Изменение статуса полученных событий",
    description="Изменение статуса полученных событий",
)
async def update_events_route(result = Depends(change_events)) -> MSG:
    return result

@events_router.post(
    "/api/events",
    status_code=status.HTTP_200_OK,
    # response_model=MSG,
    name="Изменение статуса полученных событий",
    description="Изменение статуса полученных событий",
)
async def update_events_route(result = Depends(answer_event)) -> MSG:
    return result