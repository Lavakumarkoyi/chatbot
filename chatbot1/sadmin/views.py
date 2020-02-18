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

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot


# Create your views here


class login(APIView):
    permission_classes = (AllowAny,)
    # registered = False

    def get(self, request):
        return render(request, 'sadmin/login.html')

    def post(self, request):
        registered = request.POST['registered']
        # print(registered)
        if registered == 'false':
            emailId = request.POST['email']
            try:
                user = User.objects.get(email=emailId)
            except Exception as e:
                # print("Exception of email", e)
                return render(request, 'sadmin/login.html', {
                    'message': 'USER DOESNOT EXIST'
                })

            if user.is_staff or user.is_superuser:
                if user.is_active:
                    # auth_login(request, user)
                    # print("Entered into user is active")
                    return render(request, 'sadmin/password.html', {
                        'userName': user.username
                    })
                else:
                    return render(request, 'sadmin/login.html', {
                        'message': 'USER IS NOT ACTIVE'
                    })
            else:
                # print(user.id)
                client_id = client_user.objects.get(
                    user_id_id=user.id).client_id_id

                # fetch all the users with that client id

                users_with_client_id = client_user.objects.filter(
                    client_id_id=client_id)

                user_ids = []

                for i in users_with_client_id:
                    user_ids.append(i.user_id_id)

                print(user_ids)

                for i in user_ids:
                    client_admin_details = get_user_model().objects.get(id=i)
                    print(client_admin_details)
                    if client_admin_details.is_staff:
                        print(client_admin_details)
                        break

                if client_admin_details.is_active:
                    if user.is_active:
                        print(user.username)
                        return render(request, 'sadmin/password.html', {
                            'userName': user.username
                        })
                    else:
                        return render(request, 'sadmin/login.html', {
                            'message': 'USER DOES NOT EXIST'
                        })
                else:
                    return render(request, 'sadmin/login.html', {'message': 'USER DOES NOT EXIST'})

        if registered == 'true':
            username = request.POST['email']
            password = request.POST['password']

            print(username, password)
            user = authenticate(username=username, password=password)
            # print(user)

            if user is not None:
                auth_login(request, user)
                print("user logged in successfully")
                return redirect('/sadmin')
            else:
                return render(request, 'sadmin/password.html', {
                    'message': 'PASSWORD IS INCORRECT',
                    'userName': username
                })


def navbar(user):
    totalMenu = []
    if user.is_staff:
        MenuItems = Menu.objects.filter(
            Q(userAccess='is_active') | Q(userAccess='is_staff'))
        for MenuItem in MenuItems:
            subMenuItems = SubMenu.objects.all().prefetch_related(
                'Menu').filter(Menu_id=MenuItem.MenuName)
            data = {
                "MenuItem": MenuItem,
                "SubMenuItem": subMenuItems
            }
            totalMenu.append(data)
    else:
        MenuItems = Menu.objects.filter(userAccess='is_active')
        for MenuItem in MenuItems:
            subMenuItems = SubMenu.objects.all().prefetch_related(
                'Menu').filter(Menu_id=MenuItem.MenuName)
            data = {
                "MenuItem": MenuItem,
                "SubMenuItem": subMenuItems
            }
            totalMenu.append(data)

    return totalMenu


class create_bot(View):
    @method_decorator(login_required)
    def get(self, request):
        totalMenu = navbar(request.user)

        user_id = request.user.id

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        bots_collection = 'client{}_bots'.format(client_id)

        # public_collection = 'client{}_public_groups'.format(client_id)
        # private_collection = 'client{}_private_groups'.format(client_id)

        bots1 = db[bots_collection].find({'user_id': user_id})

        user_bots = []

        for bot in bots1:
            bot['id'] = bot['_id']
            user_bots.append(bot)

        # user_private_groups = db[private_collection].find(
        #     {'user_id': user_id})

        # u_private_g = []
        # for group in user_private_groups:
        #     group['id'] = group['_id']
        #     u_private_g.append(group)

        totalMenu = navbar(request.user)
        return render(request, 'bots/create-bot.html', {'Menudata': totalMenu, 'username': request.user.username, 'bots': user_bots})


class logout(View):
    def get(self, request):
        auth_logout(request)
        return redirect('/')


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

        # public_collection = 'client{}_public_groups'.format(client_id)
        # private_collection = 'client{}_private_groups'.format(client_id)

        bots = 'client{}_bots'.format(client_id)

        for group_id, group_name in zip(group_ids, group_names):
            groups.append(
                {'group_id': group_id, 'group_name': group_name})

        for group in groups:
            print('selected groups', group)

        # check_public_group = db[public_collection].find_one(
        #     {'_id': ObjectId(group_id)})
        # check_private_group = db[private_collection].find_one(
        #     {'_id': ObjectId(group_id)})

        check_bot = db[bots].find_one({'_id': ObjectId(bot_id)})
        print(check_bot)

        # for intent in intents:
        #     print('final after sorting', intent)

        if check_bot is not None:
            db[bots].update_one(
                {'_id': ObjectId(bot_id)}, {"$set": {"groups": groups, "group_ids": group_ids}})

            print('updated successfully')

            return redirect('/sadmin')
        else:

            return redirect('/sadmin')


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

        # public_collection = 'client{}_public_groups'.format(client_id)
        # private_collection = 'client{}_private_groups'.format(client_id)

        bots_collection = 'client{}_bots'.format(client_id)

        for group_id, group_name in zip(group_ids, group_names):
            groups.append(
                {'group_id': group_id, 'group_name': group_name})

        # check_public_group = db[public_collection].find_one(
        #     {'_id': ObjectId(group_id)})
        # check_private_group = db[private_collection].find_one(
        #     {'_id': ObjectId(group_id)})

        print('group_ids after sorting', group_ids)
        print('group_names after sorting', group_names)

        for group in groups:
            print('groups after sorting', group)

        if bots_collection is not None:
            db[bots_collection].update_one({'_id': ObjectId(bot_id)}, {
                                           '$set': {'groups': groups, 'group_ids': group_ids}})

            print('updated successfully')

            return redirect('/sadmin/')

        # if check_public_group is not None:
        #     db[public_collection].update_one(
        #         {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

        #     print('updated successfully in public groups')

        #     return redirect('/groups/create-group')
        # else:
        #     db[private_collection].update_one(
        #         {'_id': ObjectId(group_id)}, {"$set": {"intents": intents, "intent_ids": intent_ids}})

        #     print('updated successfully in private groups')

        #     return redirect('/groups/create-group')

        return redirect('/sadmin')


class create_subuser(View):
    @permission_classes((IsAuthenticated, IsAdminUser))
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_staff:
            totalMenu = navbar(request.user)
            return render(request, 'sadmin/registration.html', {'username': request.user.username, 'Menudata': totalMenu})

    def post(self, request):
        userdata = request.POST
        totalMenu = navbar(request.user)
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']

        if get_user_model().objects.filter(username=username).exists():
            return render(request, 'sadmin/registration.html', {'message': 'User already exists', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
        elif get_user_model().objects.filter(email=email).exists():
            return render(request, 'sadmin/registration.html', {'message': 'email already exists', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
        elif password != password1:
            return render(request, 'sadmin/registration.html', {'message': 'Password not match', 'username': request.user.username, 'Menudata': totalMenu, 'formData': userdata})
        else:
            u = get_user_model().objects.create_user(email=email, username=username)
            u.set_password(password)
            u.save()

            print(request.user.id)

            client_id = client_user.objects.filter(
                user_id_id=request.user.id)[0]
            print(client_id.client_id_id)
            print('client_id fetched')

            user_addedNow = get_user_model().objects.filter(
                username=username)[0]

            print(user_addedNow.id)

            print('user id is fetched')

            p = client_user(client_id_id=client_id.client_id_id,
                            user_id_id=user_addedNow.id)
            p.save()
            print('user created and user created with relation to client')

            return render(request, 'sadmin/registration.html', {'message': 'user created successfully', 'Menudata': totalMenu, 'username': request.user.username})


class Manageusers(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_staff:
            print("logged in user", request.user)
            print("logged in user id", request.user.id)
            client_id = client_user.objects.filter(
                user_id_id=request.user.id)[0].client_id_id
            print(client_id)

            users_under_client = client_user.objects.filter(
                client_id_id=client_id).values()
            print(users_under_client)

            user_ids = []

            for i in users_under_client:
                print(i)
                user_ids.append(i['user_id_id'])

            print(user_ids)

            Manage_user_list = []

            for i in user_ids:
                users = get_user_model().objects.filter(id=i)[0]
                print(users)
                if users.is_staff:
                    continue
                else:
                    data = {
                        'username': users.username,
                        'email': users.email
                    }
                    Manage_user_list.append(data)

            print(Manage_user_list)
            totalMenu = navbar(request.user)
            return render(request, 'sadmin/data_List.html', {'Menudata': totalMenu, 'username': request.user.username, 'users': Manage_user_list})


class delete_bot(View):
    def get(self, request, bot_id):
        client_id = client_user.objects.filter(
            user_id_id=request.user.id)[0].client_id_id

        bots_collection = 'client{}_bots'.format(client_id)

        bot = db[bots_collection].find_one({'_id': ObjectId(bot_id)})

        if bot is not None:
            db[bots_collection].remove({'_id': ObjectId(bot_id)})

            return HttpResponseRedirect('/sadmin')


"""def logout(request):
    print("Logout :", request)
    # logout(request)
    return redirect('/')"""
