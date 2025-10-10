from fastapi import APIRouter, Depends, status
from api.config.schemas import SendMSG,MSG,SendMSGAnswer
from api.config.config import logger
from api.func.messages_func import send_msg


messages_router = APIRouter(tags=["Отправка сообщений"])


@messages_router.post(
    "/api/messages",
    status_code=status.HTTP_200_OK,
    response_model=SendMSGAnswer,
    name="Отправка ответов на сообщения",
    description="Отправка ответов на сообщения",
)
async def post_messages(message = Depends(send_msg)) -> SendMSGAnswer:
    return message