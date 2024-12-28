import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from settings import *

############## Client Setup ###############

user_bot = TelegramClient(StringSession(SESSION_STRING), 27447487, "012b94d5275b4b0b3da9df20955159ac")
sch = AsyncIOScheduler()


async def start_bot() -> None:
    await user_bot.start()
    user_bot.me = await user_bot.get_me()
    print(user_bot.me.username, "is Online Now.")


async def main_task(source_chat: int, views: int) -> None:
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
            except Exception as e:
                print(f"Error deleting message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")
    print(f"Successfully Checked {title}")
    await user_bot.send_message(
        LOGS_CHANNEL,
        f"**{title}**\n\n**Total Checked:** `{r} Posts`\n**Total Deleted:** `{f} Posts`",
    )


async def do_task():
    for chat_id, data in CHAT_IDS.items():
        try:
            sch.add_job(main_task, "interval", minutes=data[1], args=(int(chat_id), int(data[0])))
            print(f"Job added for chat_id {chat_id}")
        except Exception as er:
            print(f"Error adding job for chat_id {chat_id}: {er}")


async def main():
    await start_bot()
    await do_task()
    sch.start()
    await user_bot.run_until_disconnected()


# Start the event loop
if __name__ == "__main__":
    asyncio.run(main())
