from NocData import NocData

class AssisIA:
    def __init__(self):
        self.DLmodel = 0
        self.NocData = NocData()

    def getResponse(self, input):
        data = input.message
        updateTime = self.NocData.getModificationDate()
        text = ("Hola " + data.sender.first_name)
        image = False
        options = False
        imagePath = False
        if(str(input.message.text).find('tks')>0):

            num = self.NocData.getMonthTicketQuantity()
            goal = self.NocData.getMeta()
            text = (text + ", Tenemos " + str(num) + " tickets. Actualizado al: "+updateTime+
                    ". Meta para el día de hoy "+str(goal)+" tickets.")

        elif(str(input.message.text).find('top')>0):
            resp = self.NocData.getTopCierre(10)
            text = (text+"\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        elif(str(input.message.text).find('fse')>0):
            options = [['EXT Acceso Infra Calidad NOC','EXT Transporte IP NOC','EXT Plataformas NOC','EXT Core Voz Datos NOC'],['NOC Unificado']]

        elif(str(input.message.text).find('tre')>0):
            resp = self.NocData.getTRE()
            text = (text + "\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        elif(str(input.message.text) in ['EXT Acceso Infra Calidad NOC','EXT Transporte IP NOC','EXT Plataformas NOC','EXT Core Voz Datos NOC','NOC Unificado']):
            print(str(input.message.text))
            resp = self.NocData.getFSE(str(input.message.text))
            text = (text + "\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        else:
            text = (text + ", no tengo respuesta para tu petición")
            imagePath = False

        msg = {'Image':image,'ImagePath':imagePath,'Text':text, 'Options': options,'UpdateTime':updateTime}
        return msg

#Primer nombre: data.sender.first_name
#Apellid: data.sender.last_name
#ID Chat: data.sender.id
#Fecha: data.sender.date
#Update ID: input.update_id
#Para mas datos verificar el archivo TelMsgTree.txt
#input.message.text es el texto de entrada
