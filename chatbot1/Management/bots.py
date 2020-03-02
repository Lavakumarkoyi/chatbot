from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import permission_classes
from .models import *
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponseRedirect
from sadmin.views import navbar
from sadmin.models import *

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot


class create_bot(View):
    @method_decorator(login_required)
    def get(self, request):
        totalMenu = navbar(request.user)

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        bots_collection = 'client{}_bots'.format(client_id)

        bots1 = db[bots_collection].find({'user_id': user_id})

        user_bots = []

        for bot in bots1:
            bot['id'] = bot['_id']
            user_bots.append(bot)

        totalMenu = navbar(request.user)
        return render(request, 'bots/create-bot.html', {'Menudata': totalMenu, 'username': request.user.username, 'bots': user_bots})


class create_bot_form(View):
    def get(self, request):
        totalMenu = navbar(request.user)
        return render(request, 'bots/create-bot-form.html', {'username': request.user.username, 'Menudata': totalMenu})

    def post(self, request):
        totalMenu = navbar(request.user)
        bot_name = request.POST['BotName']
        bot_description = request.POST['BotDescription']
        bot_welcome_message = request.POST['BotWelcomeMessage']
        bot_goodbye_message = request.POST['BotGoodByeMessage']
        bot_typing_name = request.POST['BotTypingName']
        bot_message_failed_scenario = request.POST['BotMessageFailedScenario']
        bot_message_connection_error = request.POST['BotMessageConnectionError']

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        collection = 'client{}_bots'.format(client_id)

        bot = db[collection].find_one({'bot_name': bot_name})

        if bot is not None:
            return render(request, 'bots/create-bot-form.html', {'username': request.user.username, 'Menudata': totalMenu, 'message': 'Bot already exists'})

        db[collection].insert_one({'bot_name': bot_name, 'bot_description': bot_description, 'bot_welcome_message': bot_welcome_message, 'bot_goodbye_message': bot_goodbye_message, 'bot_typing_name': bot_typing_name,
                                   'bot_message_failed_scenario': bot_message_failed_scenario, 'bot_message_connection_error': bot_message_connection_error, 'user_id': user_id, 'client_id': client_id, 'created_by': request.user.username, 'created_on': datetime.now(), 'update_on': ''})

        fetch_bot_id = db[collection].find_one({'bot_name': bot_name})
        print(fetch_bot_id['_id'])
        bot_id = fetch_bot_id['_id']
        url = '/bot-group/%s' % bot_id
        print(url)
        return HttpResponseRedirect(url)


class bot_group(View):
    def get(self, request, bot_id):

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_groups'.format(client_id)
        private_collection = 'client{}_private_groups'.format(client_id)

        public_groups = db[public_collection].find()
        private_groups = db[private_collection].find({'user_id': user_id})

        u_public_g = []
        for group in public_groups:
            group['id'] = group['_id']
            u_public_g.append(group)

        u_private_g = []
        for group in private_groups:
            group['id'] = group['_id']
            u_private_g.append(group)

        totalMenu = navbar(request.user)
        return render(request, 'bots/bot-group.html', {'Menudata': totalMenu, 'username': request.user.username, "public_groups": u_public_g, "private_intents": u_private_g})

    def post(self, request, bot_id):
        print("from post request", bot_id)
        print("Post request data", request.POST)
        groups = []

        group_ids = []
        for key in request.POST.keys():
            if 'group' in key:
                group_ids.append(request.POST[key])

        print('group_ids', group_ids)

        group_names = []

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_groups = 'client{}_public_groups'.format(client_id)
        private_groups = 'client{}_private_groups'.format(client_id)

        for group_id in group_ids:
            group_name = db[public_groups].find_one(
                {'_id': ObjectId(group_id)})
            if group_name is not None:
                group_names.append(group_name['group_name'])

        for group_id in group_ids:
            group_name = db[private_groups].find_one(
                {'_id': ObjectId(group_id)})
            if group_name is not None:
                group_names.append(group_name['group_name'])

        bots = 'client{}_bots'.format(client_id)

        for group_id, group_name in zip(group_ids, group_names):
            groups.append(
                {'group_id': group_id, 'group_name': group_name})

        for group in groups:
            print('selected groups', group)

        check_bot = db[bots].find_one({'_id': ObjectId(bot_id)})
        print(check_bot)

        if check_bot is not None:
            db[bots].update_one(
                {'_id': ObjectId(bot_id)}, {"$set": {"groups": groups, "group_ids": group_ids}})

            print('updated successfully')

            return redirect('/bot-console/bots')
        else:

            return redirect('/bot-console/bots')


class group_flow(View):
    def post(self, request, bot_id):
        print(request.POST)
        group_ids = []
        group_names = []
        groups = []
        i = 1

        for key in request.POST.keys():
            if i == 1:
                i = i + 1
                continue
            group_ids.append(request.POST[key])
            i = i + 1

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_groups = 'client{}_public_groups'.format(client_id)
        private_groups = 'client{}_private_groups'.format(client_id)

        for group_id in group_ids:
            group_name1 = db[public_groups].find_one(
                {'_id': ObjectId(group_id)})
            group_name2 = db[private_groups].find_one(
                {'_id': ObjectId(group_id)})
            if group_name1 is not None:
                group_names.append(group_name1['group_name'])
            if group_name2 is not None:
                group_names.append(group_name2['group_name'])

        bots_collection = 'client{}_bots'.format(client_id)

        for group_id, group_name in zip(group_ids, group_names):
            groups.append(
                {'group_id': group_id, 'group_name': group_name})

        print('group_ids after sorting', group_ids)
        print('group_names after sorting', group_names)

        for group in groups:
            print('groups after sorting', group)

        if bots_collection is not None:
            db[bots_collection].update_one({'_id': ObjectId(bot_id)}, {
                                           '$set': {'groups': groups, 'group_ids': group_ids}})

            print('updated successfully')

            return redirect('/sadmin/')

        return redirect('/sadmin')


class delete_bot(View):
    def get(self, request, bot_id):
        client_id = client_user.objects.filter(
            user_id_id=request.user.id)[0].client_id_id

        bots_collection = 'client{}_bots'.format(client_id)

        bot = db[bots_collection].find_one({'_id': ObjectId(bot_id)})

        if bot is not None:
            db[bots_collection].remove({'_id': ObjectId(bot_id)})

            return HttpResponseRedirect('/bot-console/bots')
