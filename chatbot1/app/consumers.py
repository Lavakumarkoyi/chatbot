from django.contrib.auth.models import User
from channels.consumer import AsyncConsumer
from django.contrib.auth import get_user_model
import asyncio
import json
from django.shortcuts import render
from datetime import datetime
from channels.auth import login
from asgiref.sync import async_to_sync
from sadmin.models import *
from django.contrib.auth.models import User
import random

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot

print(db)


class ChatConsumer(AsyncConsumer):

    # print(User.objects.all())

    questions = []
    welcome = 'hi welcome to my chatbot'
    goodbye = 'Thank you for providing your information'
    i = 0

    MessageData = []

    j = 0

    async def websocket_connect(self, event):
        self.questions = []
        user = self.scope['user']
        bot_id = self.scope['url_route']['kwargs']['bot_id']
        username = self.scope['url_route']['kwargs']['username']

        user = User.objects.get(username=username)

        user_id = user.id

        client_id = client_user.objects.get(
            user_id_id=user_id).client_id_id

        print(client_id, user_id)

        bot_collection = 'client{}_bots'.format(client_id)

        public_group = 'client{}_public_groups'.format(client_id)
        private_group = 'client{}_private_groups'.format(client_id)

        public_intent = 'client{}_public_intents'.format(client_id)
        private_intent = 'client{}_private_intents'.format(client_id)

        bot = db[bot_collection].find_one({'_id': ObjectId(bot_id)})
        self.welcome = bot['bot_welcome_message']
        self.goodbye = bot['bot_goodbye_message']

        group_ids = bot['group_ids']

        print("group ids", group_ids)

        intent_ids = []

        for group_id in group_ids:
            print(group_id, type(group_id))
            public_groups = db[public_group].find_one(
                {'_id': ObjectId(group_id)})
            print("public group", public_group)
            if public_groups is not None:
                for intent in public_groups['intent_ids']:
                    intent_ids.append(intent)
                print('intent_ids', intent_ids)
            private_groups = db[private_group].find_one(
                {'_id': ObjectId(group_id)})
            if private_groups is not None:
                for intent in private_groups['intent_ids']:
                    intent_ids.append(intent)

        for intent in intent_ids:
            intent1 = db[public_intent].find_one({'_id': ObjectId(intent)})
            if intent1 is not None:
                self.questions.append(
                    random.choice(intent1['intent_response']))
            intent2 = db[private_intent].find_one({'_id': ObjectId(intent)})
            if intent2 is not None:
                self.questions.append(
                    random.choice(intent2['intent_response']))

        if len(self.questions) > 0:
            await self.send({
                'type': 'websocket.accept'
            })

    async def websocket_receive(self, event):

        print(event.get('text'))
        user = self.scope['user']

        if user.is_authenticated:
            username = user.username
        if event.get('text') == 'opened':
            serverdata = {
                'msgtype': 'intro',
                'msg': self.questions[self.i],
                'welcome': self.welcome,
                'user': 'server'
            }

            self.i = self.i + 1

            await self.send({
                'type': 'websocket.send',
                'text': json.dumps(serverdata)
            })
        else:
            userdata = {
                'msg': event.get('text'),
                'user': 'client'
            }

            messages = {
                'question': self.questions[self.j],
                'answer': event.get('text')
            }

            self.MessageData.append(messages)

            self.j = self.j + 1

            if self.i == len(self.questions):
                serverdata = {
                    'msg': self.goodbye,
                    'user': 'server'
                }

                closesocket = {
                    'msg': 'close'
                }

                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps([userdata, serverdata, closesocket])
                })
                print('Hi')

                print(self.MessageData)

                async_to_sync(db.chatdata.insert_one(
                    {"user": username, "date": datetime.now(), "chats": [self.MessageData]}))

                self.scope["session"].save()
            else:
                closesocket = {
                    'msg': 'open'
                }
                serverdata = {
                    'msg': self.questions[self.i],
                    'user': 'server'
                }

                await self.send({
                    'type': 'websocket.send',
                    'text': json.dumps([userdata, serverdata, closesocket])
                })

                self.i = self.i + 1

    async def websocket_disconnect(self, event):
        print(event)
