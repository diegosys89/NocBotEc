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
        if(str(input.message.text).find('tks')>0):
            self.NocData.loadData()
            num = self.NocData.get_nocQTY()
            goal = self.NocData.getMeta()
            text = (text + ", Tenemos " + str(num) + " tickets. Actualizado al: "+updateTime+
                    ". Meta para el día de hoy "+str(goal)+" tickets.")
            imagePath = False

        elif(str(input.message.text).find('top')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocTOP()
            text = (text+"\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        elif(str(input.message.text).find('fse')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocFSE()
            text = (text + "\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        elif(str(input.message.text).find('tre')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocTRE()
            text = (text + "\nActualizado al: "+updateTime)
            image = True
            imagePath = resp['ImagePath']

        else:
            text = (text + ", no tengo respuesta para tu petición")
            imagePath = None

        msg = {'Image':image,'ImagePath':imagePath,'Text':text,'UpdateTime':updateTime}
        return msg

#Primer nombre: data.sender.first_name
#Apellid: data.sender.last_name
#ID Chat: data.sender.id
#Fecha: data.sender.date
#Update ID: input.update_id
#Para mas datos verificar el archivo TelMsgTree.txt
#input.message.text es el texto de entrada
