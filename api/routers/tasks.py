from fastapi import APIRouter, Depends, status
from api.config.task import GetEvents

tasks_router = APIRouter(tags=["Управление задачами"])
test_task=GetEvents()

@tasks_router.get(
    "/task/stop",
    status_code=status.HTTP_200_OK,
    # response_model=GetTweet,
    name="Остановка фоновой задачи",
    description="Остановка фоновой задачи",
)
async def stop_task():
    """Endpoint для остановки фоновой задачи."""
    await test_task.stop()
    return {"message": "Фоновая задача будет остановлена"}


@tasks_router.get(
    "/task/start",
    status_code=status.HTTP_200_OK,
    # response_model=GetTweet,
    name="Запуск фоновой задачи",
    description="Запуск фоновой задачи",
)
async def stop_task():
    """Endpoint для запуска фоновой задачи."""
    await test_task.start()
    return {"message": "Фоновая задача запущена"}