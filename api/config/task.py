import asyncio
from sqlalchemy import select
from api.config.config import BOT_TOKEN, BASE_HTTP
from api.database.database import User, Event, get_db_session
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
                            if i["payload"]["chat"]["type"] == "private":
                                current_counter = i["eventId"]
                                logger.info(f"Получено сообщение: {i}")
                                user_data=User(
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



