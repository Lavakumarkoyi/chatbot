from django import template
from django.shortcuts import render, redirect
from django.views.generic import View
from sadmin.views import navbar
from django.http import HttpResponseRedirect, HttpResponse
from sadmin.models import *
from datetime import datetime
from rest_framework.views import APIView
from sadmin.models import *

import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("localhost", 27017)

db = client.chatbot

print(db)


# Create your views here.


class create_intent_form(View):
    def get(self, request):
        print("Entered into create intent form")
        totalMenu = navbar(request.user)
        return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username})

    def post(self, request):
        print(request.user.id)
        user_id = request.user.id
        totalMenu = navbar(request.user)

        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id
        print(client_id)

        print("entered into post request")
        intent_name = request.POST['IntentName']
        # checking whether the intent with that name already exists in the db

        # check it in both private and public collections
        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)
        intent_find1 = db[public_collection].find_one(
            {'intent_name': intent_name})
        intent_find2 = db[private_collection].find_one(
            {'intent_name': intent_name})

        # check wether the intent present if it presents

        if intent_find1 is not None or intent_find2 is not None:
            return render(request, 'bots/create-intent-form.html', {'Menudata': totalMenu, 'username': request.user.username, 'message': 'Intent already exists'})
        intent_description = request.POST['IntentDescription']
        phrases = []
        privacy = request.POST['privacy']

        for key in request.POST.keys():
            if 'Phrase' in key:
                phrases.append(request.POST[key])

        collection = 'client{}_{}_intents'.format(
            client_id, privacy)
        print(collection)
        keys = request.POST.keys()

        db[collection].insert_one({'intent_name': intent_name, 'intent_description': intent_description, 'intent_phrases': phrases, 'created_on': datetime.now(
        ), 'created_by': request.user.username, 'user_id': user_id, 'client_id': client_id, 'intent_response_type': 'text', 'intent_response': []})

        fetch_intent_id = db[collection].find_one({'intent_name': intent_name})
        print(fetch_intent_id['_id'])
        intent_id = fetch_intent_id['_id']
        url = '/intents/response-form/%s' % intent_id
        print(url)
        return HttpResponseRedirect(url)


class create_intent(View):
    def get(self, request):
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        user_public_intents = db[public_collection].find()

        u_public_i = []
        for intent in user_public_intents:
            intent['id'] = intent['_id']
            u_public_i.append(intent)

        user_private_intents = db[private_collection].find(
            {'user_id': user_id})

        u_private_i = []
        for intent in user_private_intents:
            intent['id'] = intent['_id']
            u_private_i.append(intent)

        totalMenu = navbar(request.user)
        return render(request, 'bots/create-intent.html', {'Menudata': totalMenu, 'username': request.user.username, 'public_intents': u_public_i, 'private_intents': u_private_i})


class IntentResponseView(View):
    def get(self, request, intent_id):

        print(intent_id)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)
        find_intent1 = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        find_intent2 = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        if find_intent1 is not None or find_intent2 is not None:
            totalMenu = navbar(request.user)
            return render(request, 'bots/response-form.html', {'Menudata': totalMenu, 'username': request.user.username})

    def post(self, request, intent_id):
        print(intent_id)
        responses = []
        for key in request.POST.keys():
            if 'Response' in key:
                responses.append(request.POST[key])
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)
        check_intent_id1 = db[public_collection].find_one(
            {'_id': ObjectId(intent_id)})
        check_intent_id2 = db[private_collection].find_one(
            {'_id': ObjectId(intent_id)})

        if check_intent_id1 is not None:
            db[public_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses}})

            print('updated successfully in public intents')

            return redirect('/bot-console/intents/')
        else:
            db[private_collection].update_one(
                {'_id': ObjectId(intent_id)}, {"$set": {"intent_response": responses}})

            print('updated successfully in private intents')

            return redirect('/bot-console/intents/')


class delete_intent(View):
    def get(self, request, intent_id):
        print(intent_id)
        user_id = request.user.id
        client_id = client_user.objects.get(
            user_id_id=request.user.id).client_id_id

        print(client_id)

        public_collection = 'client{}_public_intents'.format(client_id)
        private_collection = 'client{}_private_intents'.format(client_id)

        public_groups_collection = 'client{}_public_groups'.format(client_id)
        private_groups_collection = 'client{}_private_groups'.format(client_id)

        one = db[public_groups_collection].update_many(
            {}, {'$pull': {"intent_ids": intent_id}}, True)
        two = db[private_groups_collection].update_many(
            {}, {'$pull': {'intent_ids': intent_id}}, True)

        print(one, two)

        three = db[public_groups_collection].update_many(
            {}, {'$pull': {'intents': {'intent_id': intent_id}}}, True)
        four = db[private_groups_collection].update_many(
            {}, {'$pull': {'intents': {'intent_id': intent_id}}}, True)

        print(three, four)

        print(public_collection, private_collection)

        print(db[public_collection].find(), db[private_collection].find())

        one = db[public_collection].find_one({'_id': ObjectId(intent_id)})
        two = db[private_collection].find_one({'_id': ObjectId(intent_id)})

        print(one, two)

        if one is not None:
            db[public_collection].remove({'_id': ObjectId(intent_id)})

            return redirect('/bot-console/intents/')

        if two is not None:
            db[private_collection].remove({'_id': ObjectId(intent_id)})

            return redirect('/bot-console/intents/')

        return HttpResponse('No intent found')
