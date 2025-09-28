from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_async_session
from fastapi import Depends, HTTPException, status, Query
from app.config.config import logger
from sqlalchemy import select
from app.database.database import Event
from app.config.schemas import SendMSGAnswer,SendMSG
import asyncio
from app.config.config import BOT_TOKEN, BASE_HTTP
import httpx


async def send_msg(
        data : SendMSG = Query(...,),
        session: AsyncSession = Depends(get_async_session)) -> SendMSGAnswer:
    params = {"token": BOT_TOKEN,
    "chatId": data.user_id,
    "text": data.text,
    }
    client = httpx.AsyncClient()
    if data.msg_id:
        params["replyMsgId"] = data.msg_id
    try:
        response = await client.post(
            BASE_HTTP + "messages/sendText",
            params=params)
        if data.msg_id:
            query = select(Event).where(Event.message_id == data.msg_id)
            result = await session.execute(query)
            result = result.unique().scalars().one_or_none()
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Указан не корректный ID",
                )
            else:
                result.status_event = "FINISHED"
            await session.commit()
        return response.json()

    except Exception as e:
        logger.error(f"Ошибка {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке сообщения: {str(e)}",
        )