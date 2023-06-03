import sys
import os
import configparser
import json
from datetime import date, datetime
from typing import Any

from telethon import TelegramClient
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.functions.channels import GetChannelsRequest, GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import (PeerUser, PeerChat, PeerChannel)

# Parse Json Date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,datetime):
            return o.isoformat()
        if isinstance(o,bytes):
            return list(o)
        return json.JSONEncoder.default(self,o)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash= config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create Client and Log in to Telegram

client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")

    # Check authorization
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone,input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password : '))

    me = await client.get_me()
    input_channel ="https://t.me/badmintonsg" #"telegram URL or id"

    if input_channel.isdigit():
        entity = PeerChannel(int(input_channel))
    else:
        entity = input_channel

    my_channel = await client.get_entity(entity)

    # Get Messages
    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 1000

    while True:
        print("Current Offset Id is ",offset_id,"; Total Messages : ",total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id = offset_id,
            offset_date= None,
            add_offset = 0,
            limit = limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        
        for message in messages:
            #all_messages.append(message.to_dict())
            temp_dict = message.to_dict()
            # Some may not have 'message' key - e.g. new user added
            if 'message' in temp_dict.keys() and 'from_id' in temp_dict.keys():
                all_messages.append(dict(user_id=temp_dict['from_id']['user_id'],message=temp_dict['message']))
        
        offset_id = messages[len(messages)-1].id
        total_messages+=len(all_messages)
        if(total_count_limit != 0 and total_messages >= total_count_limit):
            break
    # Search for whatever location you want
    location = ['CCK','Chua Chu Kang', 'Choa Chu Kang']
    for message in all_messages:
        for place in location:
            if place in message['message']:
                print("##########")
                print(place)
                print("User Id: ",message['user_id'])
                print('Message : ', message['message'])

                break
    # Save messages to a JSON File
    #with open('group_messages.json','w') as outfile:
    #    json.dump(all_messages,outfile, cls=DateTimeEncoder)

with client:
    client.loop.run_until_complete(main(phone))