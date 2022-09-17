from telethon import TelegramClient, events, sync
import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
load_dotenv() 
import datetime

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
    #   'https://t.me/UAhelpCHbot',
        'https://t.me/seep_helpukrainians',
        'https://t.me/Zh_helps_UA_mums',
        'https://t.me/job_sw_ukrainians',
    #   'https://t.me/stomatologc',
        'https://t.me/zh_back_ukraine']

csv_phone_numbers_path = 'data/telegramPhoneNumbersMostActiveUsers.csv'
df_1000_most_active = pd.read_csv('data/results/1000MostActiveUsers.csv')
most_active_message_sender = df_1000_most_active.sender_id.to_list()
async def callAPI():
    messageSenderFull = []
    for chat in chats:
        print('searching chat', chat, 'for 1000 most active users')
        async with TelegramClient('testSession', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            async for message in client.iter_messages(chat):
                if message.sender_id in most_active_message_sender:
                    most_active_message_sender.remove(message.sender_id)
                    print("match found only", len(most_active_message_sender), "to go :)")
                    messageSenderFull.append(message.sender)
                    if not most_active_message_sender:
                        print("breaking")
                        break
        if not most_active_message_sender:
            print("breaking again")
            break
    df = pd.DataFrame({'senderFull':messageSenderFull})
    df.to_csv(csv_phone_numbers_path, index=False)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callAPI())
    loop.close()

if __name__ == '__main__':
    main()