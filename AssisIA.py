from NocData import NocData

class AssisIA:
    def __init__(self):
        self.DLmodel = 0
        self.NocData = NocData()

    def getResponse(self, input):
        data = input.message
        if(str(input.message.text).find('tks')>0):
            self.NocData.loadData()
            num = self.NocData.get_nocQTY()
            goal = self.NocData.getMeta()
            updateTime = self.NocData.getModificationDate()
            text = ("Hola " + data.sender.first_name + ", Tenemos " + str(num) + " tickets. Actualizado al: "+updateTime+
                    ". Meta para el día de hoy "+str(goal)+" tickets.")
            msg = {'Image':False,'ImagePath':False,'Text':text}
            return msg

        elif(str(input.message.text).find('top')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocTOP()
            updateTime = self.NocData.getModificationDate()
            text = ("Hola "+data.sender.first_name+"\nActualizado al: "+updateTime)
            msg = {'Image':True,'ImagePath':resp['ImagePath'],'Text':text}
            return msg
        elif(str(input.message.text).find('fse')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocFSE()
            updateTime = self.NocData.getModificationDate()
            text = ("Hola "+data.sender.first_name+"\nActualizado al: "+updateTime)
            msg = {'Image':True,'ImagePath':resp['ImagePath'],'Text':text}
            return msg
        elif(str(input.message.text).find('tre')>0):
            self.NocData.loadData()
            resp = self.NocData.get_nocTRE()
            updateTime = self.NocData.getModificationDate()
            text = ("Hola "+data.sender.first_name+"\nActualizado al: "+updateTime)
            msg = {'Image':True,'ImagePath':resp['ImagePath'],'Text':text}
            return msg
        else:
            text = ("Hola "+data.sender.first_name+", no tengo respuesta para tu petición")
            msg = {'Image':False,'ImagePath':None,'Text':text}
            return msg

#Primer nombre: data.sender.first_name
#Apellid: data.sender.last_name
#ID Chat: data.sender.id
#Fecha: data.sender.date
#Update ID: input.update_id
#Para mas datos verificar el archivo TelMsgTree.txt
#input.message.text es el texto de entrada
