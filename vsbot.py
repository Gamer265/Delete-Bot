import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from uuid import uuid4

from settings import *

############## Client Setup ###############

# user_bot = TelegramClient(StringSession(SESSION_STRING), 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e")
user_bot = TelegramClient(StringSession(SESSION_STRING), 27447487, "012b94d5275b4b0b3da9df20955159ac")
sch = AsyncIOScheduler()
loop = asyncio.get_event_loop()


async def start_bot() -> None:
    await user_bot.start()
    user_bot.me = await user_bot.get_me()
    print(user_bot.me.username, "is Online Now.")


loop.run_until_complete(start_bot())


async def main_task(
    source_chat: int,
    views: int,
) -> None:
    if not user_bot.is_connected():
        await user_bot.connect()
    if not (source_chat and views):
        return
    r, v, f = 0, 0, 0
    title = (await user_bot.get_entity(source_chat)).title
    print(f"Started Checking {title}")
    async for z in user_bot.iter_messages(source_chat, reverse=True):
        try:
            r += 1
            if not isinstance(z, Message) or not z.views >= views:
                continue
            v += 1
            try:
                await z.delete()
                await asyncio.sleep(1)
                f += 1
            except BaseException:
                pass
        except BaseException:
            pass
    print(f"Succesfully Checked {title}")
    await user_bot.send_message(
        LOGS_CHANNEL,
        f"**{title}**\n\n**Total Checked:** `{r} Posts`\n**Total Deleted:** `{f} Posts`",
    )


############## Event Handlers ###############

async def do_task():
    for chat_id in CHAT_IDS.keys():
        data = CHAT_IDS[chat_id]
        try:
            sch.add_job(main_task, "interval", minutes=data[1], args=(int(chat_id), int(data[0])))
        except Exception as er:
            print(er)

loop.run_until_complete(do_task())
sch.start()
user_bot.run_until_disconnected()