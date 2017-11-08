from configobj import ConfigObj
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math, os, time
from datetime import datetime, timedelta
from calendar import monthrange
from tabulate import tabulate

fileInit = '.\\config.init'

class NocData:

    def __init__(self):
        config = ConfigObj(fileInit)
        self.pathNoc = config['NocData']['pathNoc']
        self.pathTtInfo = config['NocData']['pathTtInfo']
        self.pathLista = config['NocData']['pathLista']
        self.goal = config['NocData']['ttGoal']
        self.modificationDate = ''
        self.nocFSE = ''
        self.nocTRE = ''
        self.nocTOP = ''
        self.nocQTY = ''

    def loadData(self):
        if(self.getModificationDate()!=self.modificationDate):
            self.modificationDate = self.getModificationDate()
            nocData = pd.read_csv(self.pathNoc)
            ticketInfo = pd.read_csv(self.pathTtInfo)
            lista = pd.read_csv(self.pathLista)
            nocData.rename(columns = {'﻿Incident Number' : 'Incident Number'}, inplace = True)
            ticketInfo.rename(columns = {'﻿Incident Number' : 'Incident Number'}, inplace = True)
            lista.rename(columns = {'﻿Operador Cierre' : 'Operador Cierre'}, inplace = True)

            #Cambio de Tipo de datos a las fechas
            nocData['Last Resolved Date'] = pd.to_datetime(nocData['Last Resolved Date'], dayfirst = True)
            nocData['Submit Date'] = pd.to_datetime(nocData['Submit Date'], dayfirst = True)

            #Se preparan los datos para ser unidos
            closedInfo = ticketInfo.loc[(ticketInfo['Event'] == 'Closed')]#Datos de Cierre
            closedInfo = closedInfo.drop(closedInfo[[1,2,3,4,5,6,7,8,9]], axis = 1) #Se dejan solo columnas necesarias
            openInfo = ticketInfo.loc[ticketInfo['Event'] == 'Open'] #Se guarda para la apertura
            openInfo = openInfo.drop(openInfo[[1,2,3,10,11,12,13,14]], axis = 1) #Se dejan solo columnas necesarias

            #No sería necesario realizar todo un query de las que corresponden a las fechas ya que eso lo haría el Qlik Sense
            #Aqui se juntan todas las tablas se Guardan en nocDataFinal
            nocDataFinal = pd.merge(nocData, openInfo, on = 'Incident Number')
            nocDataFinal = pd.merge(nocDataFinal, closedInfo, on = 'Incident Number')

            self.nocData = nocDataFinal
            self.lista = lista
            self.nocFSE = self.getFSE()
            self.nocTOP = self.getTopCierre(10)
            self.nocTRE = self.getTRE()
            self.nocQTY = self.getMonthTicketQuantity()
            return True
        else:
            return False

    def get_nocTOP(self):
        return self.nocTOP

    def get_nocFSE(self):
        return self.nocFSE

    def get_nocTRE(self):
        return self.nocTRE

    def get_nocQTY(self):
        return self.nocQTY

    def getModificationDate(self):
        t = os.path.getmtime(self.pathNoc)
        return(time.ctime(int(t)))

    def getTopCierre(self, top, turno = 'Todos'):
        nocTopClosed = self.getTicketsByTurn(self.nocData,turno)
        top10 = nocTopClosed.groupby("Operador Cierre").count().sort_values(by = 'Closed Flag',ascending = False)
        top10 = pd.DataFrame({'Tickets':pd.Series(top10['Closed Flag'])})
        top10 = top10.reset_index()
        top10 = pd.merge(top10,self.lista, how='outer',on='Operador Cierre') #outer para que no elimine en la tabla 1 los que no haya nombres
        top10['Nombre'].loc[top10['Nombre'].isnull()] = top10['Operador Cierre']
        top10 = pd.DataFrame({'TTs Cerrados':top10['Tickets'],'Nombre':top10['Nombre']}).head(top)
        top10 = top10.loc[top10['TTs Cerrados'].isnull() == False]
        top10.index = top10.index + 1

        finalchart = top10
        final = (tabulate(top10, headers=['Index', 'Nombre','No. Tks'], tablefmt='orgtbl'))

        #Creación de gráfica---------------------------------------
        finalchart['TTs Cerrados'] = finalchart['TTs Cerrados'].astype(int)
        finalchart['Nombre - Pos'] = finalchart.index.astype(str) + '.- ' + finalchart['Nombre']
        ImagePath = 'D:\\Projects\\NocBot_Beta\\Charts\\Top10.png'
        finalchart = finalchart.sort_values(by = 'TTs Cerrados')
        objects = finalchart['Nombre - Pos']
        y_pos = np.arange(len(objects))
        performance = finalchart['TTs Cerrados']

        plt.clf()
        plt.barh(y_pos, performance, align='center', alpha=0.5)
        plt.yticks(y_pos, objects)
        plt.xlabel('Tickets')
        plt.title('Cierre Tickets Operador ('+str(self.getModificationDate())+')')
        plt.xticks(rotation=90)
        for i, v in enumerate(performance):
            plt.text(v+0.25, i -.30, str(v), color='blue')
        plt.savefig(os.path.join(ImagePath), dpi=300, format='png', bbox_inches='tight') # use format='svg' or 'pdf' for vectorial pictures
        #--------------------------------------------------------
        data = {'Datos':final,'ImagePath':ImagePath}
        return data

    def getTicketsByTurn(self, df, x):
        ahora = datetime.now()
        ayer = ahora - timedelta(days=1)
        dia = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 00:00:00'
        veladaInicio = str(ayer.year)+'/'+str(ayer.month)+'/'+str(ayer.day)+' 22:00:00'
        mananaIncio = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 07:00:00'
        tardeInicio = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 15:00:00'
        tardeFin = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 22:00:00'
        turno9Inicio = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 09:00:00'
        turno9Fin = str(ahora.year)+'/'+str(ahora.month)+'/'+str(ahora.day)+' 18:00:00'

        if x == 'Velada':
            df = df.loc[(df['Last Resolved Date']>=pd.to_datetime(veladaInicio)) & (df['Last Resolved Date']<=pd.to_datetime(mananaIncio))]
        elif x == 'Turno7':
            df = df.loc[(df['Last Resolved Date']>=pd.to_datetime(mananaIncio)) & (df['Last Resolved Date']<=pd.to_datetime(tardeInicio))]
        elif x == 'Turno3':
            df = df.loc[(df['Last Resolved Date']>=pd.to_datetime(tardeInicio)) & (df['Last Resolved Date']<=pd.to_datetime(tardeFin))]
        elif x == 'Turno9':
            df = df.loc[(df['Last Resolved Date']>=pd.to_datetime(turno9Inicio)) & (df['Last Resolved Date']<=pd.to_datetime(turno9Fin))]
        else:
            df = df.loc[df['Last Resolved Date']>=pd.to_datetime(dia)]
        df = df.loc[df['Closed Flag'] == 1]
        return df

    def getMonthTicketQuantity(self, *argv):
        #Conteo de Tickets cerrados al momento del mes, hay que refactorizar la funci'on
        fechaCorte = (argv[0]) if len(argv)>0 else datetime.now()
        fin = str(fechaCorte.year)+'/'+str(fechaCorte.month)+'/'+str(fechaCorte.day)+' 23:59:59'
        inicio = str(fechaCorte.year)+'/'+str(fechaCorte.month)+'/01'+' 00:00:00'
        data = self.nocData
        noc_query = data.loc[((data['Last Resolved Date']<=pd.to_datetime(fin)) & (data['Last Resolved Date']>=pd.to_datetime(inicio)))]
        tt_qty = noc_query['Closed Flag'].count()
        return tt_qty

    def getFSE(self,*argv):
        ImagePath = 'D:\\Projects\\NocBot_Beta\\Charts\\FSE.png'
        noc_query = self.nocData.loc[(self.nocData['Status'] == 'Closed') | (self.nocData['Status'] == 'Resolved')]
        noc_query = noc_query.loc[noc_query['FSE']!='No Aplica']

        #Son los strings para las tablas
        columns = ('Critical (95%)', 'High (95%)', 'Medium (90%)', 'Low (85%)')
        rows = ['Acceso', 'Transporte+IP', 'Plataformas', 'Core']
        #Se prepara para que busque en todos los grupos
        noc_groups = ['EXT Acceso Infra Calidad NOC','EXT Transporte IP NOC','EXT Plataformas NOC','EXT Core Voz Datos NOC']
        urgency = ['1-Critical', '2-High', '3-Medium', '4-Low']

        #Se arma el array con los datos para la tabla
        data_list = []
        for i in range(len(noc_groups)):
            data_list.append([])
            for j in range(len(urgency)):
                data_list[i].append(self.calculateFSE(noc_query,noc_groups[i],urgency[j]))

        #Table - Main table
        umbrales = [95,95,90,85]
        plt.clf()
        ax = plt.subplot2grid((3,3), (0,3), colspan=2, rowspan=2)
        ax.table(cellText=data_list,
                    rowLabels=rows,
                    colLabels=columns,
                    loc="upper center", cellColours = self.getColorMap(data_list,umbrales))
        ax.axis("off")
        #fig.set_size_inches(w=6, h=5)
        plt.title('Cumplimiento FSE ('+str(self.getModificationDate())+')')
        plt.savefig(os.path.join(ImagePath), dpi=300, format='png', bbox_inches='tight')
        data = {'Datos':data_list,'ImagePath':ImagePath}
        return data

    def calculateFSE(self, df, assignee, urgency):
        fse = df.loc[df['Urgency'] == urgency]
        if (assignee == 'EXT Acceso Infra Calidad NOC'):
            fse = fse.loc[(fse['Assignee'] == assignee) | ((fse['Assigned Group'] == 'O&M Infraestructura') & (fse['Assignee']=='TEC - O&M NOC')) | (fse['Assigned Group'] == 'NOC Primer Nivel')]
            per = fse['FSE'].loc[fse['FSE'].isin(['Cumple','Justificado'])].count() / fse['FSE'].count()
        else:
            per = fse['FSE'].loc[(fse['FSE'].isin(['Cumple','Justificado'])) & (fse['Assignee'] == assignee)].count() / fse['FSE'].loc[fse['Assignee'] == assignee].count()
        if math.isnan(per):
            return '-'
        else:
            return ("{1:.{0}f}%".format(2,per*100))

    def calculateTRE(self, df, urgency, TRE):
        if urgency!='all':
            df = df.loc[df['Urgency'] == urgency]
        per = df[TRE].loc[(df[TRE] == 'Cumple') | (df[TRE] == 'Justificado')].count() / df[TRE].count()
        if math.isnan(per):
            return '-'
        else:
            return ("{1:.{0}f}%".format(2,per*100))

    def getTRE(self,*argv):
        ImagePath = 'D:\\Projects\\NocBot_Beta\\Charts\\TRE.png'
        fechaCorte = datetime.now()
        fin = str(fechaCorte.year)+'/'+str(fechaCorte.month)+'/'+str(fechaCorte.day)+' 23:59:59'
        inicio = str(fechaCorte.year)+'/'+str(fechaCorte.month)+'/01'+' 00:00:00'
        data = self.nocData
        noc_query = data.loc[((data['Submit Date']<=pd.to_datetime(fin)) & (data['Submit Date']>=pd.to_datetime(inicio)))]
        trea = noc_query.loc[(noc_query['TREa'].isnull() == False) & (noc_query['TREa'] != 'No Aplica')]
        tresa = noc_query.loc[(noc_query['TREsa'].isnull() == False) & (noc_query['TREsa'] != 'No Aplica')]
        rows = ['Value']
        columns = ['TREa (95%)','TREsa Critical (95%)', 'TREsa High (90%)', 'TREsa Medium (85%)', 'TREsa Low (75%)']

        #Se arma el array con los datos para la tabla
        data_list = []
        data_list.append([])
        data_list[0].append(self.calculateTRE(trea,'all','TREa'))
        data_list[0].append(self.calculateTRE(tresa,'1-Critical','TREsa'))
        data_list[0].append(self.calculateTRE(tresa,'2-High','TREsa'))
        data_list[0].append(self.calculateTRE(tresa,'3-Medium','TREsa'))
        data_list[0].append(self.calculateTRE(tresa,'4-Low','TREsa'))

        #Table - Main table
        umbrales = [95,95,90,85,75]
        plt.clf()
        ax = plt.subplot2grid((6,6), (0,6), colspan=2, rowspan=2)
        ax.table(cellText=data_list,
                    rowLabels=rows,
                    colLabels=columns, loc="upper center", cellColours = self.getColorMap(data_list,umbrales))
        ax.axis("off")
        plt.title('Tiempo de Registro ('+str(self.getModificationDate())+')')
        plt.savefig(os.path.join(ImagePath), dpi=300, format='png', bbox_inches='tight') # use format
        data = {'Datos':data_list,'ImagePath':ImagePath}
        return data

    def getColorMap(self, data_list, umbral):
        color_list = []
        for i in range(len(data_list)):
            color_list.append([])
            for j in range(len(data_list[i])):
                try:
                    if(float(data_list[i][j][:-1])>umbral[j]):
                        color_list[i].append('w')
                    else:
                        color_list[i].append('r')
                except:
                    color_list[i].append('w')
        return color_list

    def getMeta(self):
        mes, dias = monthrange(datetime.now().year, datetime.now().month)
        porDia = int(ConfigObj(fileInit)['NocData']['ttGoal']) / dias
        meta = porDia * datetime.now().day
        return math.ceil(meta)
