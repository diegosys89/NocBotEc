from configobj import ConfigObj
from twx.botapi import TelegramBot, InputFileInfo, InputFile
from multiprocessing import Process
import threading
from datetime import datetime
from AssisIA import AssisIA
import time

fileInit = '.\\config.init'

class AssisBot:
    def __init__(self):
        config = ConfigObj(fileInit)
        self.Listen = False
        self.IA = AssisIA()
        self.apikey = config['bot']['apikey']
        self.name = config['bot']['name']
        self.updatesDelay = float(config['bot']['delay'])
        self.Telegram = TelegramBot(self.apikey)
        self.Telegram.update_bot_info().wait()
        self.ListenerUsers =  threading.Thread(target = self.listeningUser, daemon = True)

    def changeApiKey(self, apikey):
        self.Telegram = TelegramBot(apikey)
        self.Telegram.update_bot_info().wait()

    def startToListen(self):
        self.Listen = True
        if (not self.ListenerUsers.is_alive()):
            self.ListenerUsers.start()
        print('Corriendo programa: '+str(self.ListenerUsers.is_alive()))

    def stopToListen(self):
        if self.ListenerUsers.is_alive():
            self.Listen = False
            print('Deja de escuchar')
        else:
            print("No hay programa que detener")

    def listeningUser(self):
        print("Inicio subproceso de escucha")
        updates = self.Telegram.get_updates().wait()
        #last_updateId = (updates[-1].message.sender.id) if (len(updates)>0) else 0
        last_updateId = (updates[-1].update_id) if (len(updates)>0) else 0
        while True:
            try:
                updates = self.Telegram.get_updates(offset = last_updateId+1, timeout = 100).wait()
                print("Updates: "+str(len(updates))+", hora: "+str(datetime.now()))
                if len(updates)>0:
                    if self.Listen: #debería responder? (Es una bandera)
                        res = self.IA.getResponse(updates[0])
                        self.Telegram.send_message(updates[0].message.chat.id, res['Text']).wait()
                        if(res['Image']):
                            fp = open(res['ImagePath'], 'rb')
                            file_info = InputFileInfo('NOCData.png', fp, 'image/png')
                            chart = InputFile('photo', file_info)
                            self.Telegram.send_photo(updates[0].message.chat.id, photo=chart).wait()

                    print(updates[0].message.text)
                    last_updateId = updates[0].update_id
            except:
                print("Error capturado a: "+str(datetime.now()))
                time.sleep(10)
