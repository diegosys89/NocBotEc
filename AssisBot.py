from configobj import ConfigObj
from twx.botapi import TelegramBot, InputFileInfo, InputFile,ReplyKeyboardMarkup
from multiprocessing import Process
import threading
from datetime import datetime
from AssisIA import AssisIA
import time
import logging

fileInit = '.\\config.init'

class AssisBot:
    def __init__(self):
        config = ConfigObj(fileInit)
        self.Listen = False
        self.IA = AssisIA()
        self.apikey = config['bot']['apikey']
        self.name = config['bot']['name']
        self.adminChatId = config['bot']['adminChatId']
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
        logging.info('Corriendo programa: '+str(self.ListenerUsers.is_alive()))

    def stopToListen(self):
        if self.ListenerUsers.is_alive():
            self.Listen = False
            logging.info('Deja de escuchar')
        else:
            logging.info("No hay programa que detener")

    def listeningUser(self):
        logging.info("Inicio subproceso de escucha")
        updates = self.Telegram.get_updates().wait()
        last_updateId = (updates[-1].update_id) if (len(updates)>0) else 0
        while True:
            try:
                updates = self.Telegram.get_updates(offset = last_updateId+1, timeout = 100).wait()
                logging.info("Updates: "+str(len(updates)))
                if len(updates)>0:
                    if self.Listen: #debería responder? (Es una bandera)
                        res = self.IA.getResponse(updates[0])
                        if (res['Options'] == False):
                            self.Telegram.send_message(updates[0].message.chat.id, res['Text']).wait()
                            if(res['Image']):
                                fp = open(res['ImagePath'], 'rb')
                                file_info = InputFileInfo('NOCData.png', fp, 'image/png')
                                chart = InputFile('photo', file_info)
                                self.Telegram.send_photo(updates[0].message.chat.id, photo=chart).wait()
                            if(res['Document']):
                                doc = open(res['DocumentPath'], 'rb')
                                file_info = InputFileInfo('Details.csv', doc, 'csv')
                                document = InputFile('document', file_info)
                                self.Telegram.send_document(updates[0].message.chat.id, document=document).wait()

                        else:
                            keyboard = res['Options']
                            reply_markup = ReplyKeyboardMarkup.create(keyboard)
                            msg = 'Seleccione el grupo para ver los detalles'
                            self.Telegram.send_message(updates[0].message.chat.id, msg, reply_markup=reply_markup).wait()

                        dataLoadDelta = (datetime.now()-datetime.strptime(res['UpdateTime'],'%a %b %d %H:%M:%S %Y'))
                        dataLoadTimeHours = dataLoadDelta.seconds / 3600
                        maxHours = 3
                        if(dataLoadTimeHours>=maxHours):
                            msg = "Carga de Datos igual a "+str(dataLoadDelta)+" horas. Revisar BD desactualizada"
                            self.Telegram.send_message(self.adminChatId, msg).wait()
                            msg = "Última actualización mayor a 02:30 horas. BD desactualizada, contactar a Administrador"
                            self.Telegram.send_message(updates[0].message.chat.id, msg).wait()

                    logging.info('Nuevo mensaje: '+updates[0].message.text)
                    last_updateId = updates[0].update_id
            except Exception as ex:
                template = "Un error del tipo {0} ha ocurrido, por favor contactar Administrador. Detalles:\n{1!r}"
                excepMsg = template.format(type(ex).__name__,ex.args)
                logging.error("Error generado en el Bot")
                logging.error(excepMsg)
                if (type(ex).__name__ == "FileNotFoundError"): #Error no se ha encontrado el archivo, contestar con el error
                    self.Telegram.send_message(updates[0].message.chat.id, excepMsg).wait()
                    self.Telegram.send_message(self.adminChatId, excepMsg).wait()
                    last_updateId = updates[0].update_id
                time.sleep(10)
