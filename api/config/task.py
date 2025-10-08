import asyncio
from sqlalchemy import select
from api.config.config import BOT_TOKEN, BASE_HTTP
from api.database.database import User, Event, get_db_session,Group
from api.config.config import logger
from datetime import datetime
import httpx

class GetEvents:
    def __init__(self):
        self.task_running = False
        self.background_task = None
        self.client = None

    async def send_request(self, current_counter):
        if self.client is None:
            self.client = httpx.AsyncClient()
        try:
            response = await asyncio.wait_for(self.client.get(
                BASE_HTTP + "events/get", params={
                    "token": BOT_TOKEN,
                    "lastEventId": current_counter,
                    "pollTime": 0,
                }
            ), timeout=2)
            return response

        except asyncio.TimeoutError:
            logger.error("Превышено время выполнения запроса")
            return None, None
        except Exception as e:
            logger.error(f"Ошибка {e}")
            return None, None

    async def write_data_to_db(self, event_data: Event):
        async with get_db_session() as session:
            session.add(event_data)
            await session.commit()
            return True


    async def get_user_id(self, user_data: User ):
        async with get_db_session() as session:
            query = (select(User)
                     .where(User.userid == user_data.userid))
            logger.info(f"{user_data.userid}")

            result = await session.execute(query)
            user = result.scalar_one_or_none()
            logger.info(f"{user}")
            if not user:
                session.add(user_data)
                await session.commit()
                user = user_data
                logger.info(f"Add new use with id: {user.id}")
            return user

    async def get_group_id(self, group_data: Group ):
        async with get_db_session() as session:
            query = (select(Group)
                     .where(Group.chatid == group_data.chatid))
            logger.info(f"{group_data.chatid}")

            result = await session.execute(query)
            group = result.scalar_one_or_none()
            logger.info(f"{group}")
            if not group:
                session.add(group_data)
                await session.commit()
                group = group_data
                logger.info(f"Add new use with id: {group.id}")
            return group

    async def send_error_msg(self, message:str, chatid:str, message_id:str):
        params = {"token": BOT_TOKEN,
                  "chatId": chatid,
                  "text": message,
                  }
        client = httpx.AsyncClient()
        if message_id:
            params["replyMsgId"] = message_id

        return await client.post(
            BASE_HTTP + "messages/sendText",
            params=params)



    async def check_city(self, chatid:str):
        chatname = chatid.split(':')[0]
        if chatname.lower() == 'врн':
            city='Воронеж'
        elif chatname.lower() == 'смл':
            city = 'Семилуки'
        elif chatname.lower() == 'орл':
            city = 'Орёл'
        elif chatname.lower() == 'пнз':
            city = 'Пенза'
        elif chatname.lower() == 'тмб':
            city = 'Тамбов'
        elif chatname.lower() == 'лпц':
            city = 'Липецк'
        else:
            city='Город не определен'
        return city

    async def check_str(self, text) -> bool:
        if text.startswith('*') and text[1:].isdigit() and len(text[1:])<7:
            return True
        else:
            return False

    async def get_event(self):
        self.task_running = True
        current_counter = 0
        logger.info("Задача начата")
        while self.task_running:
            try:
                response = await self.send_request(current_counter=current_counter)
                json_data = response.json()
                if response.status_code == 200:
                    if len(json_data["events"]) > 0:
                        for i in json_data["events"]:
                            if "text" in i["payload"]:
                                if await self.check_str(text=i["payload"]["text"]):
                                    if i["payload"]["chat"]["type"] == "private":
                                        current_counter = i["eventId"]
                                        logger.info(f"Получено сообщение: {i}")
                                        user_data = User(
                                            firstname=i["payload"]["from"]["firstName"],
                                            lastname=i["payload"]["from"]["lastName"],
                                            userid=i["payload"]["from"]["userId"],
                                        )
                                        user_full = await self.get_user_id(user_data=user_data)
                                        event_data = Event(
                                            message_text=i["payload"]["text"],
                                            message_id=i["payload"]["msgId"],
                                            user_id=user_full.id
                                        )

                                        await self.write_data_to_db(event_data=event_data)

                                    elif i["payload"]["chat"]["type"] == "group":
                                        current_counter = i["eventId"]
                                        logger.info(f"Получено сообщение: {i}")
                                        group_data = Group(
                                            chatid=i["payload"]["chat"]["chatId"],
                                            title=i["payload"]["chat"]["title"],
                                            city=await self.check_city(chatid=i["payload"]["chat"]["title"]),
                                        )
                                        user_data = User(
                                            firstname=i["payload"]["from"]["firstName"],
                                            lastname=i["payload"]["from"]["lastName"],
                                            userid=i["payload"]["from"]["userId"],
                                        )

                                        group_full = await self.get_group_id(group_data=group_data)
                                        user_full = await self.get_user_id(user_data=user_data)

                                        event_data = Event(
                                            message_text=i["payload"]["text"],
                                            message_id=i["payload"]["msgId"],
                                            user_id=user_full.id,
                                            group_id=group_full.id
                                        )

                                        await self.write_data_to_db(event_data=event_data)
                                    else:
                                        current_counter = i["eventId"]
                                        continue
                                else:
                                    current_counter = i["eventId"]
                                    await self.send_error_msg(
                                        message='@['+i["payload"]["from"]["userId"]+']'+' '+'Не корректный запрос остатка',
                                        chatid=i["payload"]["chat"]["chatId"],
                                        message_id=i["payload"]["msgId"],
                                    )
                                    continue
                            else:
                                current_counter = i["eventId"]
                                continue
                    else:
                        logger.info("Events is empty")
                else:
                    logger.info("Error response data")
                logger.info("Данные успешно получены")

                logger.info(f"{datetime.now():%H:%M:%S.%f} Задача завершена {current_counter}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка получения данных от сервера{e}")
                continue


    async def start(self):
        if not self.task_running:
            self.background_task = asyncio.create_task(self.get_event())
            logger.info("Фоновая задача запущена")
        else:
            logger.info("Фоновая задача уже выполняется")


    async def stop(self):
        if self.background_task:
            self.task_running = False
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                logger.info("Фоновая задача остановлена")