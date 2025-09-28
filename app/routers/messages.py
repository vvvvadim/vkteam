from fastapi import APIRouter, Depends, status
from app.config.schemas import SendMSG,MSG,SendMSGAnswer
from app.config.config import logger
from app.func.messages_func import send_msg


messages_router = APIRouter(tags=["Отправка сообщений"])


@messages_router.post(
    "/api/messages",
    status_code=status.HTTP_200_OK,
    response_model=SendMSGAnswer,
    name="Получение сообщений для обработки",
    description="Получение сообщений для обработки",
)
async def post_messages(message = Depends(send_msg)) -> SendMSGAnswer:
    return message