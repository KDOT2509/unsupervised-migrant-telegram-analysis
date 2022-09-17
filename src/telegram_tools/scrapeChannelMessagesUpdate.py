from telethon import TelegramClient, events, sync
import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
load_dotenv() 
import datetime
from tqdm import tqdm 


# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


chats = ['https://t.me/refugeesinSwitzerland',
        'https://t.me/campax_ukraine_help_switzerland',
        'https://t.me/zh_helps_ukraine', 
        'https://t.me/zh_helps_UArefugee',
        'https://t.me/zurich_hb_help',
        'https://t.me/zh_housing',
        'https://t.me/helppetsfromukraine',
        'https://t.me/Zurich_UA',
        'https://t.me/zh_helps_UArefugees',
        'https://t.me/seep_helpukrainians',
        'https://t.me/Zh_helps_UA_mums',
        'https://t.me/job_sw_ukrainians',
        'https://t.me/zh_back_ukraine',
        'https://t.me/zh_helps_logistics',
        'https://t.me/AargauUkraine',
        'https://t.me/BernUkraine',
        'https://t.me/TicinoLuganoUkraine',
        'https://t.me/UASchweiz',
        # https://t.me/naym_info #EU wide channel for Infos for Ukrainians
        'https://t.me/help_people_fromUkraine',
        'https://t.me/GeneveUkraine',
        #'https://t.me/Stipendii4UA', EU wide funding opportunities 
        'https://t.me/SwissUA',
        'https://t.me/BaselUkraine',
        'https://t.me/ukrainer_basel',
        'https://t.me/GeneveUkraine',
        'https://t.me/StGallenUkraine',
        ]

csv_path = 'data/telegramAllGroups.csv'

async def callAPI():
    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path)
        chats_to_update = df_old.chat.unique()
        chats_to_scrape = list(set(chats) - set(chats_to_update))
        # print(chats_to_scrape, len(chats_to_scrape))
        chatHttps = []
        messageSender = []
        messageText = []
        messageDatetime = []
    else:
        chats_to_scrape = chats
    try:
        for chat in chats_to_update:
            print('update scrapping for chat:', chat)
            df_old["messageDatetime"] = pd.to_datetime(df_old["messageDatetime"])
            date_of_newest_post = min(df_old["messageDatetime"].values)
            async with TelegramClient('testSession', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
                async for message in client.iter_messages(chat, reverse = True, offset_date = pd.Timestamp(date_of_newest_post, tz=None).to_pydatetime()): #datetime.datetime(date_of_newest_post)):
                    # a = datetime.datetime.now()
                    chatHttps.append(chat)
                    messageSender.append(message.sender_id)
                    messageText.append(message.text)
                    messageDatetime.append(message.date)
                    # b = datetime.datetime.now()
                    # c = b - a
                    # print("iteration microsecs:", c.microseconds)
            df = pd.DataFrame({'chat':chatHttps, 'messageSender':messageSender, 'messageDatetime':messageDatetime, 'messageText':messageText})
            if os.path.exists(csv_path):
                df = pd.concat([df_old, df], sort=False)
            df.to_csv(csv_path, index=False)
    except NameError:
        print("nothing to update creating new file named", csv_path)
    for chat in chats_to_scrape:
        print('scrapping new chat:', chat)
        async with TelegramClient('testSession', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            async for message in client.iter_messages(chat):
                chatHttps.append(chat)
                messageSender.append(message.sender_id)
                messageText.append(message.text)
                messageDatetime.append(message.date)
        df = pd.DataFrame({'chat':chatHttps, 'messageSender':messageSender, 'messageDatetime':messageDatetime, 'messageText':messageText})
        if os.path.exists(csv_path):
            df = pd.concat([df_old, df], sort=False)
        df.to_csv(csv_path, index=False)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callAPI())
    loop.close()

if __name__ == '__main__':
    main()