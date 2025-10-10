from sqlalchemy.ext.asyncio import AsyncSession
from api.database.database import get_async_session
from fastapi import Depends, HTTPException, status, Query
from typing import List, Dict
from api.config.config import logger
from sqlalchemy import select,update
from api.database.database import Event
from api.config.schemas import EventsSCH,MSG,UpdateEvents,SendMSG
from api.func.messages_func import send_msg

async def get_events(event_id : int = None,
        session: AsyncSession = Depends(get_async_session)) -> List[EventsSCH]:
    if event_id is None:
        query = (select(Event)
                 .where(Event.status_event != "FINISHED")
                 .join(Event.user)
                 .join(Event.group, isouter=True)
                 )
    else:
        query = (select(Event)
                 .where(Event.id == event_id)
                 .join(Event.user)
                 .join(Event.group, isouter=True)
                 )

    result = await session.execute(query)
    result = result.unique().scalars().all()
    result_list = list()
    for i in result:
        if i.group_id is None:
            result_list.append(
                {
                    "id": i.id,
                    "user_id": i.user.userid,
                    "message_text": i.message_text,
                    "message_id": i.message_id,
                    "status_event": i.status_event
                }
            )
        else:
            result_list.append(
                {
                    "id": i.id,
                    "group_id": i.group.chatid,
                    "city": i.group.city,
                    "user_id": i.user.userid,
                    "message_text": i.message_text,
                    "message_id": i.message_id,
                    "status_event": i.status_event
                }
            )

        i.status_event = "IN_PROCESSING"
    await session.commit()
    logger.info("Данные получены")
    return result_list

async def change_events(
        data:UpdateEvents = Query(...,description="Допустимые значения: NEW, FINISHED или IN_PROCESSING"),
        session: AsyncSession = Depends(get_async_session)) -> MSG:
    query = (select(Event)
             .where(Event.id == data.event_id))

    result = await session.execute(query)
    result = result.unique().scalars().one_or_none()
    if result:
        result.status_event = data.status_ev
        await session.commit()
        logger.info("Данные изменены")
        return {"result": "true"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при изменении данных",
        )

async def answer_event(event_id: int,
                       answer:str,
                       session: AsyncSession = Depends(get_async_session)):
    query = (select(Event)
                 .where(Event.id == event_id)
                 .join(Event.user)
                 .join(Event.group, isouter=True)
                 )
    result = await session.execute(query)
    result = result.unique().scalars().one_or_none()
    if result:
        if result.group_id is None:
            data = SendMSG(text=answer, user_id=result.user.userid)
        else:
            answ='@['+str(result.user.userid) +'] '+answer
            data = SendMSG(text=answ, user_id=result.group.chatid)
        await send_msg(data=data)
        result.status_event = "FINISHED"
        result.answer = answer
        await session.commit()
        logger.info("Ответ отправлен")
        return {"result": "true"}

    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при изменении данных",
        )