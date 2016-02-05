# -*- coding: utf-8 -*-
# lets begin

import vk

import requests
import threading
import time
from queue import Queue
import os
from random import randint


#from requests_futures.sessions import FuturesSession
#fsession = FuturesSession()


class VK(object):
    """
    A base class for VK
    Contain functions which directly work with VK
    """
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.pollConfig = {"mode": 66, "wait": 30, "act": "a_check"}
        self.pollServer = ""
        self.pollInitialzed = False
        self.online = False
        self.userID = 0
        self.methods = 0
        self.cache = {}
        self.queue = Queue(maxsize=60)
        self.blacklist = []
        self.captcha_needed = False
        self.captcha_img = None
        self.captcha_sid = None
        self.timeout = 1
        if os.path.exists("debug.txt"):
            self.debug = True
        else:
            self.debug = False
        self.threads = []


    def auth(self):
        self.session = vk.Session(access_token=self.access_token)
        self.vkapi = vk.API(self.session)
        try:
            self.bot_id = self.vkapi.users.get()[0]["uid"]
            print("Auth success. ID: " + str(self.bot_id))
            return self.bot_id
        except vk.exceptions.VkAPIError as e:
            raise e

    def initPoll(self):
        self.pollInitialized = False
        response = self.vkapi.messages.getLongPollServer()
        self.initPollServer = response
        self.pollServer = "http://{server}?act={act}&key={key}&ts={ts}&wait={wait}&mode={mode}".format(server=response["server"], 
            act=self.pollConfig["act"], key=response["key"], ts=response["ts"], wait=self.pollConfig["wait"],
            mode = self.pollConfig["mode"])

        self.pollTS = response["ts"]
        self.pollKey = response["key"]
        self.pollInitialized = True

    def updatePoll(self):
        self.pollServer = "http://{server}?act={act}&key={key}&ts={ts}&wait={wait}&mode={mode}".format(server=self.initPollServer["server"], 
            act=self.pollConfig["act"], key=self.initPollServer["key"], ts=self.pollTS, wait=self.pollConfig["wait"],
            mode = self.pollConfig["mode"])

    def getLostMessages(self, new_ts):
        request = vkapi.vkapi.messages.getLongPollHistory(ts=new_ts)
        return request

    def getLongPoll(self):
        response_exists = False
        while response_exists == False:
            try:

                response = fsession.get(self.pollServer).result().json()
                #print(response)
            except Exception:
                response = None
                pass
            #print(response)
            if response:
                #print(response)
                if response.get("updates", None):
                    if len(response["updates"]) != 0:
                        response_exists = True
                        #print(response)
                        #print(str(response["ts"]) + " - " + str(self.pollTS) + " = " + str(response["ts"] - self.pollTS))

                        self.pollTS = response["ts"]
                        self.updatePoll()

                        #if self.captcha_needed:
                        
                        #self.threads.append(msgthread)
                        #self.cmd.msg(response)
                        return response


    def getLongPoll_Message(self):

        response = self.getLongPoll()
        while response["updates"][0][0] != 4:
            response = self.getLongPoll()
        return response

with open('all_accs.txt') as f:
    lines = f.read().splitlines()

global bots
bots = {}

for i in lines:
    vkapi = VK(i)
    bot_id = vkapi.auth()
    bots[bot_id] = vkapi

full_bots_list = list(bots)[:]
#print(full_bots_list)


#print(bots)

#Checking for friends


option = 1

if option == 2:
    friends = {}
    for i in bots:
        print("Checking {}'s friends".format(i))
        friends[i] = bots[i].vkapi.friends.get(user_id=i)
        #print(friends)


    #print(friends)

    all_bots_list = list(bots)

    for bot in friends:

        print("Working on {}".format(bot))
        bots_list = all_bots_list[:]
        bots_list.remove(bot)

        for i in bots_list:
            if i not in friends[bot]:
                print("{} is not on {}'s friends".format(i, bot))
                try:
                    bots[bot].vkapi.friends.add(user_id=i)
                except Exception as e:
                    if e.is_captcha_needed:
                        print("captcha img : {} | {}".format(e.captcha_sid, e.captcha_img))
                        answer_captcha = input(": ")
                        bots[bot].vkapi.friends.add(user_id=i, captcha_sid = e.captcha_sid, captcha_key=answer_captcha)
                time.sleep(3)
                try:
                    bots[i].vkapi.friends.add(user_id=bot)
                except Exception as e:
                    if e.is_captcha_needed:
                        print("captcha img : {} | {}".format(e.captcha_sid, e.captcha_img))
                        answer_captcha = input(": ")
                        bots[i].vkapi.friends.add(user_id=bot, captcha_sid = e.captcha_sid, captcha_key=answer_captcha )
                print("Successfully added {}".format(i))

def loop(vkapi_loop):
    #print(threading.currentThread().getName())
    vkapi_loop.initPoll()
    #print(vkapi_loop.pollServer)
    vkapi = vkapi_loop
    asd = vkapi.vkapi.messages.getLongPollServer(use_ssl = 0)
    ts = asd["ts"]

    while True:
        try:
            # connection get long poll server

            urlstring = "http://" + str(asd["server"]) + "?act=a_check&key=" + str(asd["key"]) + "&ts=" + str(ts) + "&wait=25&mode=2"
            response = requests.get(urlstring).json()
            ts = response["ts"]
            result2 = response
            # getting result
            #print(response)
            if result2["updates"][0][0] == 4:
                #print(str(threading.currentThread().getName()) + " " + response["updates"][0][6])
                #print("ID #" + str(idd+1) + ": " + str(result2))
                #print("dd: " + str(result2[7]))

                if response["updates"][0][7].get("from", None):
                    uid = response["updates"][0][7]["from"]
                    groupChat = True
                else:
                    uid = response["updates"][0][3]
                    groupChat = False

                if groupChat:
                    group_id = abs(2000000000 - response["updates"][0][3])
                    chat_id = group_id


                if response["updates"][0][6] == "test_message_1234":
                    vkapi.vkapi.messages.send(chat_id=group_id, message="Hello! Hello! Hello!")

                if response["updates"][0][6] == "assemble!":

                    chat_info = vkapi.vkapi.messages.getChat(chat_id = group_id)
                    #print(chat_info)
                    #print(full_bots_list)
                    for i in full_bots_list:
                        #print(i)
                        if i not in chat_info["users"]:
                            #print("!!@#!*@#*!@*#!*@#*!@*#")
                            #print("Adding {} to {} chat".format(i, chat_id))
                            vkapi.vkapi.messages.addChatUser(chat_id = chat_id, user_id=i)

                    pass




                if result2["updates"][0][7].get("source_act") == "chat_kick_user":
                    #print("USER KICKED !!! ! !!!")
                    if result2["updates"][0][7].get('from') != result2["updates"][0][7].get('source_mid'):
                        try:
                            kicked_user_id = str(result2["updates"][0][7].get("source_mid"))
                            #chat_id = chatidcheck(result2[3])
                            #print("Chat ID: " + str(chat_id) + " | UserID: " + str(kicked_user_id))
                            vk_add = vkapi.vkapi.messages.addChatUser(chat_id = chat_id, user_id = kicked_user_id)
                            #print(vk_add)
                        except Exception:
                            traceback.print_exc()
                            pass

            #    #print("Message from Bot #" + str(idd+1) + ": " + str(result2[6]))
            #    pass
            #else:
            

            #print("ID #" + str(idd+1) + ": " + str(result2))
            
        except Exception:
            #traceback.print_exc()
            pass





        #while True:
            
        #    response = vkapi_loop.getLongPoll()
        #    print(str(threading.currentThread().getName()) + " " + str(response))
        #print(response["ts"])
        #user_id = response["updates"][0][7]["from"]
        #print("user id is " + str(user_id))
        #vkapi.addUser(user_id)


threads = {}
for i in bots:
    print("Starting thread for {}".format(i))
    threads[i] = threading.Thread(target=loop, args=(bots[i],))
    threads[i].start()

